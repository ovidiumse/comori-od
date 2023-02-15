import uvicorn
import logging
import ujson
import yaml
import user_agents
import geoip2.database
import requests
import time

from datetime import datetime
from flatten_json import flatten
from fastapi import FastAPI, Request
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

app = FastAPI()

LOGGER_ = logging.getLogger(__name__)

def make_logline(metric):
    fields_dict = metric["fields"]
    tags_dict = metric["tags"]
    result = f"{tags_dict['remote_addr']} {tags_dict['client_addr']} - {fields_dict['remote_user']} [{fields_dict['time_local']}] {fields_dict['request_time']} {fields_dict.get('upstream_response_time')} "
    result += '"' + f"{tags_dict['method']} {tags_dict['request']}" + '" '
    result += f"{tags_dict['status']} {fields_dict['bytes_sent']} "
    result += '"' + f"{tags_dict['http_referer']}" + '" '
    result += '"' + f"{fields_dict['http_user_agent']}" + '" '

    return result

async def send_to_loki(data):

    try:
        response = requests.get(f"{CFG['loki']['url']}/ready")
        while response.status_code != 200:
            logging.info("Waiting for Loki to become ready...")
            time.sleep(1)
            response = requests.get(f"{CFG['loki']['url']}/ready")

        streams = []
        for metric in data["metrics"]:
        
            stream = {
                'stream': {},
                'values': [[str(time.time_ns()), make_logline(metric)]]
            }

            for tag, value in metric["tags"].items():
                stream["stream"][tag] = value

            stream["stream"]["geoip_location_latitude"] = metric["fields"]["geoip_location_latitude"]
            stream["stream"]["geoip_location_longitude"] = metric["fields"]["geoip_location_longitude"]
            
            streams.append(stream)
       
        data = { "streams": streams }

        response = requests.post(f"{CFG['loki']['url']}/loki/api/v1/push", json=data)
        if response.status_code > 300:
            raise Exception(f"Sending log failed! Error: {response.text}")

    except Exception as e:
        logging.error(f"Sending log failed! Error: {e}")

async def send_to_influx(data):
    float_fields = ["request_time", "upstream_response_time", "geoip_location_latitude", "geoip_location_longitude"]

    for metric in data["metrics"]:
        try:
            p = Point(metric["name"])
            for tag, value in metric['tags'].items():
                p.field(tag, value)

            for field, value in metric['fields'].items():
                if field in float_fields:
                    p.field(field, float(value))
                else:
                    p.field(field, value)

            InfluxDb.write(bucket=CFG['influx']['bucket'], record=p)
        except Exception as e:
            logging.error(f"Sending log metrics failed! Error: {e}")


@app.post("/nginx_log")
async def nginx_log(request: Request):
    try:
        data = await request.json()
        for metric in data["metrics"]:
            fields_dict = metric["fields"]
            tags_dict = metric["tags"]
            
            with geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-City.mmdb') as reader:
                response = reader.city(tags_dict['client_addr'])
                tags_dict["geoip"] = {
                    "city": response.city.name,
                    "continent": response.continent.name,
                    "continent_code": response.continent.code,
                    "country": response.country.name,
                    "country_code": response.country.iso_code,
                    "location": {
                        "time_zone": response.location.time_zone
                    },
                    "region": response.subdivisions.most_specific.name,
                    "region_code": response.subdivisions.most_specific.iso_code
                }

                fields_dict["geoip"] = {
                    "location": {
                        "latitude": response.location.latitude,
                        "longitude": response.location.longitude
                    }
                }

            user_agent = user_agents.parse(fields_dict["http_user_agent"])
            tags_dict["user_agent"] = {
                "browser_family": user_agent.browser.family, 
                "browser_version": user_agent.browser.version_string, 
                "os_family": user_agent.os.family, 
                "os_version": user_agent.os.version_string,
                "device_family": user_agent.device.family,
                "device_brand": user_agent.device.brand,
                "device_model": user_agent.device.model,
                "is_mobile": user_agent.is_mobile,
                "is_bot": user_agent.is_bot,
                "is_pc": user_agent.is_pc,
                "is_tablet": user_agent.is_tablet
            }

            metric["fields"] = flatten(metric["fields"])
            metric["tags"] = flatten(metric["tags"])

        await send_to_loki(data)
        await send_to_influx(data)
    except Exception as e:
        logging.error(f"Failed to transform! Error: {e}")
        raise


if __name__ == "__main__":
    log_cfg = {}
    with open('logging_cfg.yaml', 'r') as log_conf_file:
        log_cfg = yaml.full_load(log_conf_file)
    
    global CFG
    CFG = {}
    with open('cfg.yaml', 'r') as cfg_file:
        CFG = yaml.full_load(cfg_file)

    global InfluxDb
    client = InfluxDBClient(url=CFG['influx']['url'], token=CFG['influx']['token'], org=CFG['influx']['org'])
    InfluxDb = client.write_api(write_options=SYNCHRONOUS)

    logging.config.dictConfig(log_cfg)

    LOGGER_.info("Initializing svc...")

    uvicorn.run(app, host="0.0.0.0", port=9003, log_level="debug")
