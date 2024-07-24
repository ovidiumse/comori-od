#!/usr/bin/pypy3
import os
import re
import sys
import argparse
import simplejson as json
import requests
import logging
import hashlib
from collections import defaultdict
from datetime import datetime
from unidecode import unidecode
from getpass import getpass

PARSER_ = argparse.ArgumentParser(description="Bible content uploader.")
LOGGER_ = logging.getLogger(__name__)

COMORI_OD_API_HOST = ""
API_OTPKEY = ""

MAX_BULK_SIZE = 100
MAX_BULK_CONTENT_SIZE = 100000

def parseArgs():
    PARSER_.add_argument("-i",
                         "--input",
                         dest="json_filepath",
                         action="store",
                         type=str,
                         help="Input JSON file")
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
    PARSER_.add_argument("-v",
                         "--verbose",
                         dest="verbose",
                         action="store_true",
                         help="Verbose logging")

    args, _ = PARSER_.parse_known_args()
    return args


def post(uri, data):
    response = requests.post(
        "{}/{}".format(COMORI_OD_API_HOST, uri),
        headers={'Authorization': 'Token {}'.format(API_OTPKEY)},
        json=data)

    if response.status_code != requests.codes.ok:
        LOGGER_.error("Error: {}".format(response, indent=2))
    response.raise_for_status()
    return response.json() if response.text else {}


def delete(uri):
    response = requests.delete(
        "{}/{}".format(COMORI_OD_API_HOST, uri),
        headers={'Authorization': 'Token {}'.format(API_OTPKEY)})

    response.raise_for_status()


def chunk(data, n):
    for i in range(0, len(data), n):
        yield data[i:i + n]


def create_index():
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
                        "type": "hunspell",
                        "language": "ro_simple"
                    },
                    "od_shingle": {
                        'type': 'shingle',
                        "min_shingle_size": 2,
                        "max_shingle_size": 4,
                    },
                    "synonyms": {
                        "type": "synonym_graph",
                        "lenient": True,
                        "synonyms": [
                            "vremurile => vremile",
                            "vremile => vremurile",
                            "predestinare => predestinație",
                            "predestinație => predestinare",
                            "trimis => trimes",
                            "trimes => trimis",
                            "Isus => Iisus",
                            "Iisus => Isus"
                        ]
                    }
                },
                "analyzer": {
                    "standard": {
                        'type': 'custom',
                        "tokenizer": "standard",
                        "filter": ["lowercase", "romanian_keywords"]
                    },
                    "folding": {
                        'type': 'custom',
                        "tokenizer": "standard",
                        "filter":
                        ["lowercase", "asciifolding", "romanian_keywords"]
                    },
                    "folding_stemmed": {

                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ["lowercase", "synonyms", "asciifolding", "romanian_stemmer", "romanian_keywords"]
                    },
                    "completion": {
                        'type': 'custom',
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding"]
                    },
                    "completion_folding_stemmed": {
                        'type': 'custom',
                        "tokenizer": "standard",
                        "filter": ["lowercase",  "asciifolding", "romanian_stemmer"]
                    },
                    "suggesting": {
                        'type': 'custom',
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding", "od_shingle"]
                    }
                }
            }
        }
    }

    mappings = {
        'dynamic': False,
        'properties': {
            'book': {
                'type': 'keyword',
            },
            'title': {
                'type': 'text',
                'term_vector': 'with_positions_offsets',
                'analyzer': 'romanian',
                'fields': {
                    'keyword': {
                        'type': 'keyword'
                    },
                    'folded': {
                        'type': 'text',
                        'term_vector': 'with_positions_offsets',
                        'analyzer': 'folding',
                    },
                    'folded_stemmed': {
                        'type': 'text',
                        'term_vector': 'with_positions_offsets',
                        'analyzer': 'folding_stemmed',
                    },
                    'completion': {
                        'type': 'search_as_you_type',
                        'analyzer': 'completion',
                    },
                    'completion_folded_stemmed': {
                        'type': 'search_as_you_type',
                        'analyzer': 'completion_folding_stemmed',
                    },
                    'suggesting': {
                        'type': 'text',
                        'analyzer': 'suggesting'
                    }
                }
            },
            'chapter': {
                'type': 'integer',
            },
            'chapter_link': {
                'type': 'text'
            },
            'verses': {
                "properties": {
                    'type': {
                        'type': 'keyword'
                    },
                    'name': {
                        'type': 'keyword'
                    },
                    'content': {
                        'properties': {
                            'type': {
                                'type': 'keyword'
                            },
                            'text': {
                                'type': 'text'
                            }
                        }
                    }
                }
            },
            'body': {
                'type': 'text',
                'term_vector': 'with_positions_offsets',
                'analyzer': 'romanian',
                'fields': {
                    'folded': {
                        'type': 'text',
                        'term_vector': 'with_positions_offsets',
                        'analyzer': 'folding'
                    },
                    'folded_stemmed': {
                        'type': 'text',
                        'term_vector': 'with_positions_offsets',
                        'analyzer': 'folding_stemmed'
                    },
                    'suggesting': {
                        'type': 'text',
                        'analyzer': 'suggesting'
                    }
                }
            },
            '_insert_idx': {
                'type': 'integer'
            },
            '_insert_ts': {
                'type': 'date'
            },
            'references': {
                'enabled': False
            }
        }
    }

    post("bible", {'settings': settings, 'mappings': mappings})

def upload(bulk):
    url = "bible/articles"

    response = post(url, bulk)
    if response['total'] != response['indexed']:
        failed = response['total'] - response['indexed']
        LOGGER_.warning("{} Bible titles failed to index!".format(failed))

    return response['indexed']

def calculate_maxsize(bulks):
    max_size = 0
    for bulk in bulks:
        bulk_size = 0
        for article in bulk:
            for line in article["body"]:
                bulk_size += len(line)

        if bulk_size > max_size:
            max_size = bulk_size

    return max_size


def index_all(articles):
    indexed = 0

    for idx, article in enumerate(articles):
        id = "{} {} {}".format(article['book'], article['chapter'], article['title'])
        id = unidecode(id).lower()
        id = re.sub('[\.\,\!\(\)\[\] ]+', '-', id)
        id = re.sub('(\-)+', '-', id)
        article['_id'] = id
        article['_insert_idx'] = idx
        article['_insert_ts'] = datetime.now().isoformat()

    for bulk in chunk(articles, MAX_BULK_SIZE):
        bulks = [bulk]
        bulk_size = MAX_BULK_SIZE
        while bulk_size > 1:
            bulk_content_size = calculate_maxsize(bulks)
            if bulk_content_size <= MAX_BULK_CONTENT_SIZE:
                break

            new_bulks = []
            for b in bulks:
                new_bulks.append(b[:bulk_size])
                new_bulks.append(b[bulk_size:])
                
            bulks = [b for b in new_bulks if b]
            bulk_size = int(bulk_size / 2)

        for b in bulks:
            indexed += upload(b)
            LOGGER_.info("{} / {} indexed!".format(indexed, len(articles)))


def delete_index():
    try:
        delete("bible")
    except Exception as ex:
        LOGGER_.error('Indexing failed! Error: {}'.format(ex), exc_info=True)


def main():
    args = parseArgs()

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    global COMORI_OD_API_HOST
    COMORI_OD_API_HOST = os.getenv("COMORI_OD_API_HOST", "http://localhost:9000")

    if args.json_filepath:
        print(f"Started bible-upload.py on {os.path.basename(args.json_filepath)} and {COMORI_OD_API_HOST}")
    else:
        print(f"Started bible-upload.py on {COMORI_OD_API_HOST}")

    print("API HOST: {}".format(COMORI_OD_API_HOST))

    global API_OTPKEY
    if "API_TOTP_KEY" in os.environ:
        API_OTPKEY = os.getenv("API_TOTP_KEY")
    else:
        API_OTPKEY = getpass("OTP code: ")
        os.environ["API_TOTP_KEY"] = API_OTPKEY

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    if args.delete_index:
        LOGGER_.info("Deleting index from {}...".format(COMORI_OD_API_HOST))
        delete_index()

    if args.create_index:
        LOGGER_.info("Creating index from {}...".format(COMORI_OD_API_HOST))
        create_index()

    if args.json_filepath:
        with open(args.json_filepath, 'r', encoding='utf-8') as json_file:
            articles = json.load(json_file)

        try:
            LOGGER_.info("Indexing {} articles from {} to {}...".
                         format(len(articles), args.json_filepath, COMORI_OD_API_HOST))

            index_all(articles)
            LOGGER_.info("Indexed {} Bible articles from {} to {}!".format(len(articles),
                                                                     args.json_filepath,
                                                                     COMORI_OD_API_HOST))
        except Exception as ex:
            LOGGER_.error('Indexing failed! Error: {}'.format(ex), exc_info=True)

    print("Done\n")

if "__main__" == __name__:
    main()
