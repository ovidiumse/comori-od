#!/usr/bin/pypy3
import os
import argparse
import logging
import yaml
import requests
import simplejson as json
from getpass import getpass

PARSER_ = argparse.ArgumentParser(description="OD metadata uploader.")

EXTERNAL_HOST = "https://api.comori-od.ro"
LOCAL_HOST = "http://localhost:9000"

COMORI_OD_API_HOST = LOCAL_HOST
API_OTPKEY = ""

def parseArgs():
    PARSER_.add_argument("-i",
                         "--input",
                         dest="yaml_filepath",
                         action="store",
                         type=str,
                         help="Input YAML file")
    PARSER_.add_argument("--endpoint", dest="endpoint", type=str, help="API endpoint", required=True)
    PARSER_.add_argument("--index",
                         dest="idx_name",
                         action="store",
                         required=True,
                         help="Index name")
    PARSER_.add_argument("-e",
                         "--external-host",
                         action="store_true",
                         help="Upload to external host")
    PARSER_.add_argument("-v",
                         "--verbose",
                         dest="verbose",
                         action="store_true",
                         help="Verbose logging")

    return PARSER_.parse_args()

def upload(index_name, data, endpoint):
    response = requests.post(f"{COMORI_OD_API_HOST}/{index_name}/{endpoint}",
                             headers={'Authorization': f'Token {API_OTPKEY}'},
                             json=data)
    response.raise_for_status()
    return response.json()


def main():
    args = parseArgs()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    global COMORI_OD_API_HOST

    if args.external_host:
        COMORI_OD_API_HOST = EXTERNAL_HOST

    print("API HOST: {}".format(COMORI_OD_API_HOST))

    global API_OTPKEY
    if "API_TOTP_KEY" in os.environ:
        API_OTPKEY = os.getenv("API_TOTP_KEY")
    else:
        API_OTPKEY = getpass("OTP code: ")
        os.environ["API_TOTP_KEY"] = API_OTPKEY

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    if args.yaml_filepath:
        with open(args.yaml_filepath, 'r') as yaml_file:
            data = yaml.full_load(yaml_file)
            response = upload(args.idx_name, data, args.endpoint)
            logging.info(f"Response: {json.dumps(response, indent=2)}")

if "__main__" == __name__:
    main()