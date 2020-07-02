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
    PARSER_.add_argument("-i",
                         "--index-name",
                         action="store",
                         dest="idx_name",
                         default="od",
                         help="Index name")
    PARSER_.add_argument("-t", "--doc-type", action="store", required=True, help="Document type")
    PARSER_.add_argument("-e", "--external-host", action="store_true", help="Query external host")
    PARSER_.add_argument("query", action="store", help="Query")

    return PARSER_.parse_args()


def get(uri):
    response = requests.get("{}/{}".format(COMORI_OD_API_BASEURL, uri))
    if response.status_code != requests.codes.ok:
        logging.error("Error: {}".format(json.dumps(response.json(), indent=2)))
    response.raise_for_status()
    return response.json()


def search(idx_name, doc_type, query):
    results = get("{}/{}?q={}".format(idx_name, doc_type, query))
    print("Got {} hits:".format(results['hits']['total']['value']))
    for hit in results['hits']['hits']:
        result = hit['_source']
        print("Id: {}".format(hit['_id']))
        print("Score: {}".format(hit['_score']))
        print("Volume: {}".format(result['volume']))
        print("Book: {}".format(result['book']))
        print("Title: {}".format(result['title']))
        print("Type: {}".format(result['type']))
        print("Author: {}".format(result['author']))
        if 'highlight' in hit:
            print("highlight: {}".format(json.dumps(hit['highlight'], indent=2)))
        print("")


def main():
    args = parseArgs()

    global COMORI_OD_API_HOST, COMORI_OD_API_BASEURL

    if args.external_host:
        COMORI_OD_API_HOST = EXTERNAL_HOST
        COMORI_OD_API_BASEURL = "http://{}".format(COMORI_OD_API_HOST)

    print("Searching {} using {}...".format(args.query, COMORI_OD_API_BASEURL))
    search(args.idx_name, args.doc_type, args.query)


if "__main__" == __name__:
    main()
