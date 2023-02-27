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
TEST_HOST = "https://testapi.comori-od.ro"
NEW_HOST = "https://api.comori-od.ro"
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
    PARSER_.add_argument("-t", "--test-host", action="store_true", help="Upload to test host")
    PARSER_.add_argument("-n", "--new-host", action="store_true", help="Upload to new host")
    PARSER_.add_argument("-v",
                         "--verbose",
                         dest="verbose",
                         action="store_true",
                         help="Verbose logging")

    args, _ = PARSER_.parse_known_args()
    return args

def upload(index_name, data, endpoint):
    response = requests.post(f"{COMORI_OD_API_HOST}/{index_name}/{endpoint}",
                             headers={'Authorization': f'Token {API_OTPKEY}'},
                             json=data)
    response.raise_for_status()
    return response.json()

def expand_links(index_name, data):
    if isinstance(data, dict):
        for key, entry in data.items():
            data[key] = expand_links(index_name, entry)
        return data
    elif isinstance(data, list):
        entries = []
        for entry in data:
            entries.append(expand_links(index_name, entry))
        return entries
    elif isinstance(data, str):
        if data.startswith('/'):
            return f"{COMORI_OD_API_HOST}/{index_name}{data}"
        else:
            return data
    else:
        return data

def main():
    args = parseArgs()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    global COMORI_OD_API_HOST

    if args.external_host:
        COMORI_OD_API_HOST = EXTERNAL_HOST
    elif args.test_host:
        COMORI_OD_API_HOST = TEST_HOST
    elif args.new_host:
        COMORI_OD_API_HOST = NEW_HOST

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
            data = expand_links(args.idx_name, data)
            response = upload(args.idx_name, data, args.endpoint)
            logging.info(f"Response: {json.dumps(response, indent=2)}")

if "__main__" == __name__:
    main()