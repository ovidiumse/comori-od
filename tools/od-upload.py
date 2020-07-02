#!/usr/bin/pypy3
import argparse
import simplejson as json
import requests
import logging

PARSER_ = argparse.ArgumentParser(description="OD content uploader.")

EXTERNAL_HOST = "comori-od.ro"
LOCAL_HOST = "localhost"

COMORI_OD_API_HOST = LOCAL_HOST
COMORI_OD_API_BASEURL = "http://{}".format(COMORI_OD_API_HOST)


def parseArgs():
    PARSER_.add_argument("-i",
                         "--input",
                         dest="json_filepath",
                         action="store",
                         type=str,
                         help="Input JSON file")
    PARSER_.add_argument("--index",
                         dest="idx_name",
                         action="store",
                         required=True,
                         help="Index name")
    PARSER_.add_argument("-d",
                         "--delete-index",
                         dest="delete_index",
                         action="store_true",
                         help="Delete existing index")
    PARSER_.add_argument("-c",
                         "--create-index",
                         dest="create_index",
                         action="store_true",
                         help="Create the index")
    PARSER_.add_argument("-e",
                         "--external-host",
                         action="store_true",
                         help="Upload to external host")
    PARSER_.add_argument("-p", "--port", action="store", required=True)
    PARSER_.add_argument("-v",
                         "--verbose",
                         dest="verbose",
                         action="store_true",
                         help="Verbose logging")

    return PARSER_.parse_args()


def post(uri, data):
    response = requests.post("{}/{}".format(COMORI_OD_API_BASEURL, uri), json=data)
    if response.status_code != requests.codes.ok:
        logging.error("Error: {}".format(json.dumps(response.json(), indent=2)))
    response.raise_for_status()
    return response.json()


def delete(uri):
    response = requests.delete("{}/{}".format(COMORI_OD_API_BASEURL, uri))
    response.raise_for_status()


def chunk(data, n):
    for i in range(0, len(data), n):
        yield data[i:i + n]


def create_index(idx_name):
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "filter": {
                    "romanian_stop": {
                        "type": "stop",
                        "stopwords": "_romanian_"
                    },
                    "romanian_keywords": {
                        "type": "keyword_marker",
                        "keywords": ["exemplu"]
                    },
                    "romanian_stemmer": {
                        "type": "stemmer",
                        "language": "romanian"
                    },
                    "od_shingle": {
                        'type': 'shingle',
                        "min_shingle_size": 2,
                        "max_shingle_size": 4,
                    }
                },
                "analyzer": {
                    "romanian": {
                        'type':
                        'custom',
                        "tokenizer":
                        "standard",
                        "filter":
                        ["lowercase", "romanian_stop", "romanian_keywords", "romanian_stemmer"]
                    },
                    "folding": {
                        'type':
                        'custom',
                        "tokenizer":
                        "standard",
                        "filter": [
                            "lowercase", "romanian_stop", "romanian_keywords", "romanian_stemmer",
                            "asciifolding"
                        ]
                    },
                    "completion": {
                        'type': 'custom',
                        "tokenizer": "standard",
                        "filter": ["lowercase", "romanian_stemmer", "asciifolding"]
                    },
                    "suggesting": {
                        'type': 'custom',
                        "tokenizer": "standard",
                        "filter": ["lowercase", "romanian_stop", "asciifolding", "od_shingle"]
                    }
                }
            }
        }
    }

    mappings = {
        'dynamic': False,
        'properties': {
            'volume': {
                'type': 'keyword',
            },
            'book': {
                'type': 'keyword',
            },
            'author': {
                'type': 'keyword',
            },
            'title': {
                'type': 'text',
                'term_vector': 'with_positions_offsets',
                'analyzer': 'standard',
                'fields': {
                    'folded': {
                        'type': 'text',
                        'analyzer': 'folding',
                        'term_vector': 'with_positions_offsets',
                    },
                    'completion': {
                        'type': 'search_as_you_type',
                        'analyzer': 'completion',
                    },
                    'suggesting': {
                        'type': 'text',
                        'analyzer': 'suggesting'
                    }
                }
            },
            'verses': {
                "properties": {
                    'type': {
                        'type': 'keyword'
                    },
                    'text': {
                        'type': 'text',
                        'term_vector': 'with_positions_offsets',
                        'analyzer': 'standard',
                        'fields': {
                            'folded': {
                                'type': 'text',
                                'analyzer': 'folding',
                                'term_vector': 'with_positions_offsets',
                            },
                            'suggesting': {
                                'type': 'text',
                                'analyzer': 'suggesting'
                            }
                        }
                    }
                }
            }
        }
    }

    post(idx_name, {'settings': settings, 'doc_type': 'articles', 'mappings': mappings})


def index_all(idx_name, articles):
    failed = 0
    indexed = 0
    for bulk in chunk(articles, 100):
        response = post("{}/articles".format(idx_name), bulk)
        if response['total'] != response['indexed']:
            failed += response['total'] - respose['indexed']
            logging.warning("So far {} articles failed to index!".format(failed))
        indexed += response['indexed']
        logging.info("{} / {} indexed!".format(indexed, len(articles)))


def delete_index(idx_name):
    try:
        delete(idx_name)
    except Exception as ex:
        logging.error('Indexing failed! Error: {}'.format(ex), exc_info=True)


def main():
    args = parseArgs()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    global COMORI_OD_API_HOST, COMORI_OD_API_BASEURL

    if args.external_host:
        COMORI_OD_API_HOST = EXTERNAL_HOST

    COMORI_OD_API_BASEURL = "http://{}:{}".format(COMORI_OD_API_HOST, args.port)

    print("API HOST: {}".format(COMORI_OD_API_HOST))

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    if args.delete_index:
        logging.info("Deleting index from {}...".format(COMORI_OD_API_BASEURL))
        delete_index(args.idx_name)

    if args.create_index:
        logging.info("Creating index from {}...".format(COMORI_OD_API_BASEURL))
        create_index(args.idx_name)

    if args.json_filepath:
        with open(args.json_filepath, 'r') as json_file:
            articles = json.load(json_file)

        try:
            logging.info("Indexing {} articles to {}...".format(len(articles), COMORI_OD_API_BASEURL))
            index_all(args.idx_name, articles)
            logging.info("Indexed {} articles to {}!".format(len(articles), COMORI_OD_API_BASEURL))
        except Exception as ex:
            logging.error('Indexing failed! Error: {}'.format(ex), exc_info=True)


if "__main__" == __name__:
    main()