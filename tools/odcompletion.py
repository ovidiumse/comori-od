import sys
import argparse
import simplejson as json
import requests
import logging

PARSER_ = argparse.ArgumentParser(description="OD content competion.")

EXTERNAL_HOST = "vps-4864b0cc.vps.ovh.net:8000"
LOCAL_HOST = "localhost:9000"

COMORI_OD_API_HOST = LOCAL_HOST
COMORI_OD_API_BASEURL = "http://{}".format(COMORI_OD_API_HOST)


def parseArgs():
    PARSER_.add_argument("-i", "--index-name", action="store", dest="idx_name", help="Index name")
    PARSER_.add_argument("-l", "--localhost", action="store_true", help="Query localhost")
    PARSER_.add_argument("term", action="store", help="Query term")

    return PARSER_.parse_args()


def get(uri):
    response = requests.get("{}/{}".format(COMORI_OD_API_BASEURL, uri))
    if response.status_code != requests.codes.ok:
        logging.error("Error: {}".format(json.dumps(response.json(), indent=2)))
    response.raise_for_status()
    return response.json()


def suggest(idx_name, term):
    results = get("{}/titles/completion?prefix={}".format(idx_name, term))
    print("Found {} results in {}ms:".format(results['hits']['total']['value'], results['took']))
    hits = results['hits']['hits']
    for hit in hits:
        result = hit['_source']
        print("Volume: {}".format(result['volume']))
        print("Book: {}".format(result['book']))
        print("Title: {}".format(result['title']))
        print("Author: {}".format(result['author']))
        print("")


def main():
    args = parseArgs()

    global COMORI_OD_API_HOST

    if args.localhost:
        COMORI_OD_API_HOST = LOCAL_HOST
    else:
        COMORI_OD_API_HOST = EXTERNAL_HOST

    suggest(args.idx_name, args.term)


if "__main__" == __name__:
    main()