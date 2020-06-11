import argparse
import simplejson as json
import requests
import logging

PARSER_ = argparse.ArgumentParser(description="OD content uploader.")

EXTERNAL_HOST = "vps-4864b0cc.vps.ovh.net:8000"
LOCAL_HOST = "localhost:8000"

COMORI_OD_API_HOST = EXTERNAL_HOST
COMORI_OD_TESTAPI_BASEURL = "http://{}".format(COMORI_OD_API_HOST)


def parseArgs():
    PARSER_.add_argument("-i",
                         "--input",
                         dest="json_filepath",
                         action="store",
                         type=str,
                         required=True,
                         help="Input JSON file")
    PARSER_.add_argument("-d",
                         "--delete-index",
                         dest="delete_index",
                         action="store_true",
                         help="Delete existing index")
    PARSER_.add_argument("-v",
                         "--verbose",
                         dest="verbose",
                         action="store_true",
                         help="Verbose logging")

    return PARSER_.parse_args()


def post(uri, data):
    response = requests.post("{}/{}".format(COMORI_OD_TESTAPI_BASEURL, uri), json=data)
    response.raise_for_status()
    return response.json()


def delete(uri):
    response = requests.delete("{}/{}".format(COMORI_OD_TESTAPI_BASEURL, uri))
    response.raise_for_status()


def chunk(data, n):
    for i in range(0, len(data), n):
        yield data[i:i + n]


def create_index():
    props = ['volume', 'book', 'author', 'title', 'verses']

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
                    }
                },
                "analyzer": {
                    "romanian": {
                        "tokenizer":
                        "standard",
                        "filter":
                        ["lowercase", "romanian_stop", "romanian_keywords", "romanian_stemmer"]
                    },
                    "folding": {
                        "tokenizer":
                        "standard",
                        "filter": [
                            "asciifolding", "lowercase", "romanian_stop", "romanian_keywords",
                            "romanian_stemmer"
                        ]
                    }
                }
            }
        }
    }

    mappings = {'properties': {}}
    for p in props:
        mappings['properties'][p] = {
            'type': 'text',
            "term_vector": "with_positions_offsets",
            'analyzer': 'standard',
            'fields': {
                'folded': {
                    'type': 'text',
                    'analyzer': 'folding',
                    "term_vector": "with_positions_offsets"
                }
            }
        }

    mappings['properties']['title']['boost'] = 2
    mappings['properties']['title']['fields']['folded']['boost'] = 2
    mappings['properties']['title']['fields']['completion'] = {
        'type': 'completion',
        'analyzer': 'folding'
    }

    post("index/od", {'settings': settings, 'doc_type': 'articles', 'mappings': mappings})


def index_all(articles):
    try:
        failed = 0
        indexed = 0
        for ch in chunk(articles, 100):
            response = post("od/articles", ch)
            if response['total'] != response['indexed']:
                failed += response['total'] - respose['indexed']
                logging.warning("So far {} articles failed to index!".format(failed))
            indexed += response['indexed']
            logging.info("{} / {} indexed!".format(indexed, len(articles)))

    except Exception as ex:
        logging.error('Indexing failed! Error: {}'.format(ex), exc_info=True)


def delete_index():
    try:
        delete("index/od")
    except Exception as ex:
        logging.error('Indexing failed! Error: {}'.format(ex), exc_info=True)


def main():
    args = parseArgs()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    if args.delete_index:
        logging.info("Deleting index...")
        delete_index()
        logging.info("Creating index...")
        create_index()

    with open(args.json_filepath, 'r') as json_file:
        articles = json.load(json_file)
        logging.info("Indexing {} articles...".format(len(articles)))
        index_all(articles)
        logging.info("Indexed {} articles!".format(len(articles)))


if "__main__" == __name__:
    main()