#!/usr/bin/pypy3
import sys
import argparse
import simplejson as json
import requests
import logging

PARSER_ = argparse.ArgumentParser(description="OD content suggester.")

EXTERNAL_HOST = "https://api.comori-od.ro"
TEST_HOST = "https://testapi.comori-od.ro"
LOCAL_HOST = "http://localhost:9000"

COMORI_OD_API_HOST = LOCAL_HOST

def parseArgs():
    PARSER_.add_argument("-e", "--external-host", action="store_true", help="Query external host")
    PARSER_.add_argument("-t", "--test-host", action="store_true", help="Query test host")
    PARSER_.add_argument("-f",
                         "--fields",
                         action="store",
                         default=[
                             "hits", "id", "score", "volume", "book", "title",
                             "type", "author", "highlight"
                         ],
                         nargs='+')
    PARSER_.add_argument("query", action="store", help="Query")

    return PARSER_.parse_args()


def get(uri):
    response = requests.get("{}/{}".format(COMORI_OD_API_HOST, uri))
    if response.status_code != requests.codes.ok:
        logging.error("Error: {}".format(json.dumps(response.json(), indent=2)))
    response.raise_for_status()
    return response.json()


def search(query, fields):
    results = get("od/articles?q={}".format(query))
    if "hits" in fields:
        print("Got {} hits:".format(results['hits']['total']['value']))

    for hit in results['hits']['hits']:
        result = hit['_source']
    
        if "id" in fields:
            print("Id: {}".format(hit['_id']))

        if "score" in fields:
            print("Score: {}".format(hit['_score']))
        
        if "volume" in fields:
            print("Volume: {}".format(result['volume']))

        if "book" in fields:
            print("Book: {}".format(result['book']))

        if "title" in fields:
            print("Title: {}".format(result['title']))

        if "type" in fields:
            print("Type: {}".format(result['type']))

        if "author" in fields:
            print("Author: {}".format(result['author']))

        if "highlight" in fields and 'highlight' in hit:
            for field in hit['highlight']:
                for highlight in hit['highlight'][field]:
                    print("Highlight: {}".format(highlight))
        print("")


def main():
    args = parseArgs()

    global COMORI_OD_API_HOST

    if args.external_host:
        COMORI_OD_API_HOST = EXTERNAL_HOST
    elif args.test_host:
        COMORI_OD_API_HOST = TEST_HOST

    search(args.query, args.fields)


if "__main__" == __name__:
    main()
