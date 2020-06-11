import argparse
import simplejson as json
import requests
import logging

PARSER_ = argparse.ArgumentParser(description="OD content uploader.")

EXTERNAL_HOST = "vps-4864b0cc.vps.ovh.net:8000"
LOCAL_HOST = "localhost:8000"

<<<<<<< Updated upstream
COMORI_OD_API_HOST = EXTERNAL_HOST
=======
COMORI_OD_API_HOST = LOCAL_HOST
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======
    PARSER_.add_argument("-l", "--localhost", action="store_true", help="Upload to localhost")
>>>>>>> Stashed changes
    PARSER_.add_argument("-v",
                         "--verbose",
                         dest="verbose",
                         action="store_true",
                         help="Verbose logging")

    return PARSER_.parse_args()


def post(uri, data):
    response = requests.post("{}/{}".format(COMORI_OD_TESTAPI_BASEURL, uri), json=data)
<<<<<<< Updated upstream
=======
    if response.status_code != requests.codes.ok:
        logging.error("Error: {}".format(json.dumps(response.json(), indent=2)))
>>>>>>> Stashed changes
    response.raise_for_status()
    return response.json()


def delete(uri):
    response = requests.delete("{}/{}".format(COMORI_OD_TESTAPI_BASEURL, uri))
    response.raise_for_status()


def chunk(data, n):
    for i in range(0, len(data), n):
        yield data[i:i + n]


def create_index():
<<<<<<< Updated upstream
    props = ['volume', 'book', 'author', 'title', 'verses']
=======
    props = [{
        'name': 'volume',
        'type': 'keyword'
    }, {
        'name': 'book',
        'type': 'keyword'
    }, {
        'name': 'author',
        'type': 'keyword'
    }, {
        'name': 'title',
        'type': 'text'
    }, {
        'name': 'verses',
        'type': 'text'
    }]
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
        mappings['properties'][p] = {
            'type': 'text',
            "term_vector": "with_positions_offsets",
            'analyzer': 'standard',
            'fields': {
                'folded': {
                    'type': 'text',
=======
        fieldInfo = mappings['properties'][p['name']] = {
            'type': p['type'],
        }

        if p['type'] == 'text':
            fieldInfo['term_vector'] = 'with_positions_offsets'
            fieldInfo['analyzer'] = 'standard'
            fieldInfo['fields'] = {
                'folded': {
                    'type': p['type'],
>>>>>>> Stashed changes
                    'analyzer': 'folding',
                    "term_vector": "with_positions_offsets"
                }
            }
<<<<<<< Updated upstream
        }

    mappings['properties']['title']['boost'] = 2
    mappings['properties']['title']['fields']['folded']['boost'] = 2
    mappings['properties']['title']['fields']['completion'] = {
=======

    titleInfo = mappings['properties']['title']
    titleInfo['boost'] = 2
    titleInfo['fields']['folded']['boost'] = 2
    titleInfo['fields']['completion'] = {
>>>>>>> Stashed changes
        'type': 'completion',
        'analyzer': 'folding'
    }

<<<<<<< Updated upstream
    post("index/od", {'settings': settings, 'doc_type': 'articles', 'mappings': mappings})
=======
    post("od", {'settings': settings, 'doc_type': 'articles', 'mappings': mappings})
>>>>>>> Stashed changes


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
<<<<<<< Updated upstream
        delete("index/od")
=======
        delete("od")
>>>>>>> Stashed changes
    except Exception as ex:
        logging.error('Indexing failed! Error: {}'.format(ex), exc_info=True)


def main():
    args = parseArgs()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

<<<<<<< Updated upstream
=======
    global COMORI_OD_API_HOST

    if args.localhost:
        COMORI_OD_API_HOST = LOCAL_HOST
    else:
        COMORI_OD_API_HOST = EXTERNAL_HOST

>>>>>>> Stashed changes
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    if args.delete_index:
<<<<<<< Updated upstream
        logging.info("Deleting index...")
        delete_index()
        logging.info("Creating index...")
=======
        logging.info("Deleting index from {}...".format(COMORI_OD_API_HOST))
        delete_index()
        logging.info("Creating index from {}...".format(COMORI_OD_API_HOST))
>>>>>>> Stashed changes
        create_index()

    with open(args.json_filepath, 'r') as json_file:
        articles = json.load(json_file)
<<<<<<< Updated upstream
        logging.info("Indexing {} articles...".format(len(articles)))
        index_all(articles)
        logging.info("Indexed {} articles!".format(len(articles)))
=======
        logging.info("Indexing {} articles to {}...".format(len(articles), COMORI_OD_API_HOST))
        index_all(articles)
        logging.info("Indexed {} articles to {}!".format(len(articles), COMORI_OD_API_HOST))
>>>>>>> Stashed changes


if "__main__" == __name__:
    main()