#!/usr/bin/pypy3
import os
import re
import argparse
import simplejson as json
import requests
import logging
import hashlib
from collections import defaultdict
from datetime import datetime
from unidecode import unidecode
from getpass import getpass

PARSER_ = argparse.ArgumentParser(description="OD content uploader.")

EXTERNAL_HOST = "https://api.comori-od.ro"
TEST_HOST = "https://testapi.comori-od.ro"
NEW_HOST = "https://api.comori-od.ro"
LOCAL_HOST = "http://localhost:9000"

COMORI_OD_API_HOST = LOCAL_HOST
API_OTPKEY = ""

MAX_BULK_SIZE = 100
MAX_BULK_CONTENT_SIZE = 1000000

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
    PARSER_.add_argument("-da",
                         "--date-added",
                         dest="date_added",
                         action="store",
                         default=None,
                         type=str,
                         help="Date added")
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
    PARSER_.add_argument("-t", "--test-host", action="store_true", help="Upload to test host")
    PARSER_.add_argument("-n", "--new-host", action="store_true", help="Upload to the new host")
    PARSER_.add_argument("-o", "--output-dir", dest="output_dir", action="store", help="JSON output dir", default=None)
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
        logging.error("Error: {}".format(response, indent=2))
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
            'type': {
                'type': 'keyword'
            },
            'verses': {
                "properties": {
                    'type': {
                        'type': 'keyword'
                    },
                    'text': {
                        'type': 'text',
                        'term_vector': 'with_positions_offsets',
                        'analyzer': 'romanian',
                        'fields': {
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
                            'suggesting': {
                                'type': 'text',
                                'analyzer': 'suggesting'
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
            'date_added': {
                'type': 'date'
            },
            'bible-refs': {
                'enabled': False
            }
        }
    }

    post(idx_name, {'settings': settings, 'mappings': mappings})

def upload(idx_name, bulk):
    url = f"{idx_name}/articles"

    response = post(url, bulk)
    if response['total'] != response['indexed']:
        failed = response['total'] - response['indexed']
        logging.warning("{} articles failed to index!".format(failed))

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


def index_all(idx_name, date_added, articles):
    indexed = 0

    for idx, article in enumerate(articles):
        id = "{} {} {}".format(article['title'], article['book'], article['author'])
        id = unidecode(id).lower()
        id = re.sub('[\.\,\!\(\)\[\] ]+', '-', id)
        id = re.sub('(\-)+', '-', id)
        article['_id'] = id
        article['_index'] = idx_name
        article['_insert_idx'] = idx
        article['_insert_ts'] = datetime.now().isoformat()
        article['date_added'] = date_added

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
            indexed += upload(idx_name, b)
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

    global COMORI_OD_API_HOST

    if args.external_host:
        COMORI_OD_API_HOST = EXTERNAL_HOST
    elif args.test_host:
        COMORI_OD_API_HOST = TEST_HOST
    elif args.new_host:
        COMORI_OD_API_HOST = NEW_HOST

    if args.json_filepath:
        print(f"Started od-upload.py on {os.path.basename(args.json_filepath)} and {COMORI_OD_API_HOST}")
    else:
        print(f"Started od-upload.py on {COMORI_OD_API_HOST}")

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

    if args.delete_index:
        logging.info("Deleting index from {}...".format(COMORI_OD_API_HOST))
        delete_index(args.idx_name)

    if args.create_index:
        logging.info("Creating index from {}...".format(COMORI_OD_API_HOST))
        create_index(args.idx_name)

    if args.json_filepath:
        with open(args.json_filepath, 'r', encoding='utf-8') as json_file:
            articles = json.load(json_file)

        try:
            logging.info("Indexing {} articles from {} to {}...".
                         format(len(articles), args.json_filepath, COMORI_OD_API_HOST))
            if not args.date_added:
                raise Exception("Date-added not provided")

            index_all(args.idx_name, args.date_added, articles)
            logging.info("Indexed {} articles from {} to {}!".format(len(articles),
                                                                     args.json_filepath,
                                                                     COMORI_OD_API_HOST))
        except Exception as ex:
            logging.error('Indexing failed! Error: {}'.format(ex), exc_info=True)

        if args.output_dir:
            articlesByBook = defaultdict(list)
            for article in articles:
                articlesByBook[article['book']].append(article)

            logging.info("Writing books to files...")
            for book, atcs in articlesByBook.items():
                filePath = f"{args.output_dir}/{book}.json"
                with open(filePath, 'w') as book_file:
                    json.dump(atcs, book_file)

            logging.info("Writting articles to files...")
            for article in articles:
                filePath = f"{args.output_dir}/{article['_id']}.json"
                with open(filePath, 'w') as article_file:
                    json.dump(article, article_file)

    print("Done\n")

if "__main__" == __name__:
    main()
