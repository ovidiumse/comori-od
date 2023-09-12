#!/usr/bin/pypy3
import sys
import argparse
import simplejson as json
import requests
import logging

PARSER_ = argparse.ArgumentParser(description="OD content suggester.")

EXTERNAL_HOST = "vps-4864b0cc.vps.ovh.net:8000"
LOCAL_HOST = "localhost:9000"

COMORI_OD_API_HOST = LOCAL_HOST
COMORI_OD_API_BASEURL = "http://{}".format(COMORI_OD_API_HOST)


def parseArgs():
    PARSER_.add_argument("-e", "--external-host", action="store_true", help="Query external host")
    PARSER_.add_argument("query", action="store", help="Query")

    return PARSER_.parse_args()


def get(uri):
    response = requests.get("{}/{}".format(COMORI_OD_API_BASEURL, uri))
    if response.status_code != requests.codes.ok:
        logging.error("Error: {}".format(json.dumps(response.json(), indent=2)))
    response.raise_for_status()
    return response.json()


def suggest(query):
    results = get("od/suggest?q={}".format(query))
    options = results['suggest']['simple_phrase'][0]['options']
    print("Got {} suggestions in {}ms:".format(len(options), results['took']))
    for option in options:
        print("Text: {}".format(option['text']))
        print("Highlighted: {}".format(option['highlighted']))
        print("Score: {}".format(option['score']))
        print("Would match: {}".format(option['collate_match']))
        print("")


def main():
    args = parseArgs()

    global COMORI_OD_API_HOST

    if args.external_host:
        COMORI_OD_API_HOST = EXTERNAL_HOST

    suggest(args.query)


if "__main__" == __name__:
    main()
