#!/usr/bin/pypy3
import os
import falcon
from falcon_auth import FalconAuthMiddleware
from falcon_auth.backends import AuthBackend
import simplejson as json
import logging
import logging.config
import urllib
import yaml
import jwt
import pymongo
from pyotp import TOTP, random_base32
from elasticsearch import Elasticsearch, TransportError, helpers
from falcon.http_status import HTTPStatus
from pymongo import MongoClient

LOGGER_ = None
ES = None

def buildTermFilter(field, values):
    fieldFilters = []

    for value in values.split(','):
        if value:
            fieldFilters.append({'term': {field: value}})

    # need to simulate a boolean or over the filters
    # of the same field
    if fieldFilters:
        fieldFilters = {
            'bool': {
                'should': fieldFilters,
                'minimum_should_match': 1
            }
        }

    return fieldFilters

def parseFilters(req):
    authors = urllib.parse.unquote(req.params['authors']) if 'authors' in req.params else ""
    types = urllib.parse.unquote(req.params['types']) if 'types' in req.params else ""
    volumes = urllib.parse.unquote(req.params['volumes']) if 'volumes' in req.params else ""
    books = urllib.parse.unquote(req.params['books']) if 'books' in req.params else ""

    filters = []

    fieldFilters = [
        buildTermFilter('author', authors),
        buildTermFilter('type', types),
        buildTermFilter('volume', volumes),
        buildTermFilter('book', books)
    ]

    for fieldFilter in fieldFilters:
        if fieldFilter:
            filters.append(fieldFilter)

    return {
        'bool': {
            'must': filters
        }
    }

class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
        if req.method == 'OPTIONS':
            raise HTTPStatus(falcon.HTTP_200, body='\n')


class Index(object):
    def on_delete(self, req, resp, idx_name):
        resp.content_type = 'application/json'

        try:
            LOGGER_.info(f"Deleting index {idx_name}...")

            ES.indices.delete(index=idx_name)
            resp.status = falcon.HTTP_200
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Deleting index failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Deleting index failed! Error: {}".format(ex), exc_info=True)

    def on_get(self, req, resp, idx_name):
        try:
            LOGGER_.info(f"Getting data for index {idx_name}...")

            mapping = ES.indices.get_mapping(index=idx_name)
            settings = ES.indices.get(index=idx_name)
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({'settings': settings, 'mapping': mapping})
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Getting index info failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Getting index info failed! Error: {}".format(ex), exc_info=True)

    def on_post(self, req, resp, idx_name):
        data = json.loads(req.stream.read())

        try:
            LOGGER_.info(f"Creating index {idx_name} with data {json.dumps(data, indent=1)}")

            if ES.indices.exists(idx_name):
                ES.indices.delete(index=idx_name)

            ES.indices.create(index=idx_name, body=data['settings'])
            ES.indices.put_mapping(index=idx_name, body=data['mappings'])
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({})
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Creating index failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Creating index failed! Error: {}".format(ex), exc_info=True)


class Articles(object):
    def index(self, idx_name, article):
        try:
            LOGGER_.info(f"Indexing article {article['title']} from {article['book']} into {idx_name}...")

            ES.index(index=idx_name, body=json.dumps(article))
            return True
        except Exception as ex:
            LOGGER_.error("Indexing {} failed!".format(article), exc_info=True)
            return False

    def buildShouldMatch(self, q):
        if not q:
            return []

        should_match = []

        fields = ["title", "title.folded", "verses.text", "verses.text.folded"]
        for f in fields:
            should_match.append({
                "intervals": {
                    f: {
                        "match": {
                            "query": q,
                            "max_gaps": 4,
                            "ordered": True
                        }
                    }
                }
            })

            should_match.append({
                "intervals": {
                    f: {
                        "match": {
                            "query": q,
                            "max_gaps": 4,
                            "ordered": True,
                            "analyzer": "folding_synonym"
                        }
                    }
                }
            })

        return should_match

    def buildShouldMatchHighlight(self, q):
        should_match_highlight = []
        should_match_highlight.append({
            "simple_query_string": {
                "query": "\"{}\"~{}".format(q, 4),
                "fields": ["title^2", "title.folded^2", "verses.text", "verses.text.folded"],
                "default_operator": "AND"
            }
        })

        should_match_highlight.append({
            "simple_query_string": {
                "query": "\"{}\"~{}".format(q, 4),
                "fields": ["title^2", "title.folded^2", "verses.text", "verses.text.folded"],
                "default_operator": "AND",
                "analyzer": "folding_synonym"
            }
        })

        return should_match_highlight

    def buildQuery(self, should_match, filters):
        return {
            'bool': {
                'should': should_match,
                'filter': filters,
                'minimum_should_match': min(1, len(should_match))
            }
        }

    def query(self, idx_name, req):
        limit = req.params['limit'] if 'limit' in req.params else 100
        offset = req.params['offset'] if 'offset' in req.params else 0
        q = urllib.parse.unquote(req.params['q'])

        include_aggs = 'include_aggs' in req.params
        include_unmatched = 'include_unmatched' in req.params

        filters = parseFilters(req)
        LOGGER_.info(f"Quering {idx_name} with req {json.dumps(req.params, indent=2)}")

        should_match = self.buildShouldMatch(q)
        should_match_highlight = self.buildShouldMatchHighlight(q)

        query_body = {
            'query': self.buildQuery(should_match, filters),
            '_source': {
                'excludes': ['verses', 'bible-refs']
            },
            'highlight': {
                'highlight_query': {
                    'bool': {
                        'should': should_match_highlight
                    }
                },
                'fields': {
                    'title': {
                        "matched_fields": ["title", "title.folded"],
                        'type': 'fvh'
                    },
                    'verses.text': {
                        "matched_fields":
                        ["verses.text", "verses.text.folded"],
                        'type': 'fvh'
                    }
                },
                "order": "score"
            },
            'size': limit,
            'from': offset
        }

        if include_aggs:
            for fieldName in ['author', 'type', 'volume', 'book']:
                if 'aggs' not in query_body:
                    query_body['aggs'] = {}

                query_body['aggs'][f'{fieldName}s'] =  {
                    'terms': {
                        'field': fieldName,
                        'size': 1000000,
                        'min_doc_count': 0 if include_unmatched else 1,
                        'order': {'min_insert_ts': 'asc'}
                    },
                    'aggs': {
                        'min_insert_ts': {
                            'min': {
                                'field': '_insert_ts'
                            }
                        }
                    }
                }

        return ES.search(index=idx_name, body=query_body, timeout="1m")

    def getById(self, idx_name, req):
        LOGGER_.info(f"Getting article from {idx_name} with request {json.dumps(req.params, indent=2)}")

        return ES.get(index=idx_name, id=req.params['id'])

    def getRandomArticle(self, idx_name, req):
        LOGGER_.info(f"Getting random article from {idx_name} with request {json.dumps(req.params, indent=2)}")

        limit = req.params['limit'] if 'limit' in req.params else 1
        offset = req.params['offset'] if 'offset' in req.params else 0

        return ES.search(index=idx_name,
                         body={
                             'query': {
                                 'function_score': {
                                     'random_score': {}
                                 }
                             },
                             'size': limit,
                             'from': offset
                         })

    def on_get(self, req, resp, idx_name):
        try:
            if 'q' in req.params:
                results = self.query(idx_name, req)
            elif 'id' in req.params:
                results = self.getById(idx_name, req)
            else:
                results = self.getRandomArticle(idx_name, req)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(results)
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)

    def on_post(self, req, resp, idx_name):
        try:
            articles = json.loads(req.stream.read())
            indexed = 0

            LOGGER_.info(f"Indexing {len(articles)} into {idx_name}...")

            for a in articles:
                a['_index'] = idx_name
            indexed, _ = helpers.bulk(ES, articles, stats_only=True)
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({'total': len(articles), 'indexed': indexed})
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({
                'total': len(articles),
                'indexed': indexed,
                'exception': ex.error,
                'info': ex.info
            })
            LOGGER_.error("Posting articles failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Posting articles failed! Error: {}".format(ex), exc_info=True)


class ContentHandler(object):
    def on_get(self, req, resp, idx_name):

        try:
            filters = parseFilters(req)
            LOGGER_.info(f"Quering contents from {idx_name} with req {json.dumps(req.params, indent=2)}")

            limit = req.params['limit'] if 'limit' in req.params else 10000
            offset = req.params['offset'] if 'offset' in req.params else 0

            query_body = {
                'query': {
                    'bool': {
                        'filter': filters
                    }
                },
                'size': limit,
                'from': offset,
                'sort': [{'_insert_ts': {'order': 'asc'}}]
            }

            response = ES.search(index=idx_name, body=query_body)
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(response)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error(f"Querying contents from {idx_name} failed! Error: {ex}", exc_info=True)

class FieldAggregator(Articles):
    def __init__(self, fieldName, aggs):
        self.fieldName = fieldName
        self.aggs = aggs

    def getValues(self, idx_name, req):
        LOGGER_.info(f"Getting {self.fieldName}s from {idx_name} with req {json.dumps(req.params, indent=2)}")

        include_unmatched = 'include_unmatched' in req.params

        q = urllib.parse.unquote(req.params['q']) if 'q' in req.params else None
        filters = parseFilters(req)

        query_body = {
            'query': self.buildQuery(self.buildShouldMatch(q), filters),
            'size': 0,
            'aggs': {
                f'{self.fieldName}s': {
                    'terms': {
                        'field': self.fieldName,
                        'size': 1000000,
                        'min_doc_count': 0 if include_unmatched else 1,
                        'order': {'min_insert_ts': 'asc'}
                    },
                    'aggs': {
                        'min_insert_ts': {
                            'min': {
                                'field': '_insert_ts'
                            }
                        }
                    }
                }
            }
        }

        for agg in self.aggs:
            aggs_body = query_body['aggs'][f'{self.fieldName}s']['aggs']
            aggs_body[f'{agg}s'] = {'terms': {'field': agg, 'size': 100}}

        return ES.search(index=idx_name, body=query_body, timeout="1m")

    def on_get(self, req, resp, idx_name):
        try:
            results = self.getValues(idx_name, req)
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(results)
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)

    def on_delete(self, req, resp, idx_name, value):
        try:
            query = {
                'query': {
                    'match': {
                        self.fieldName: {
                            'query': value
                        }
                    }
                }
            }

            ES.delete_by_query(idx_name, body=query)
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)


class Titles(object):
    def on_get(self, req, resp, idx_name):
        try:
            filters = parseFilters(req)
            LOGGER_.info(f"Quering titles from {idx_name} with req {json.dumps(req.params, indent=2)}")

            limit = req.params['limit'] if 'limit' in req.params else 10000
            offset = req.params['offset'] if 'offset' in req.params else 0

            query_body = {
                'query': {
                    'bool': {
                        'filter': filters
                    }
                },
                '_source': {
                    'excludes': ['verses', 'bible-refs'],
                },
                'size': limit,
                'from': offset,
                'sort': [{'_insert_ts': {'order': 'asc'}}]
            }

            response = ES.search(index=idx_name, body=query_body)
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(response)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error(f"Querying titles from {idx_name} failed! Error: {ex}", exc_info=True)


class TitlesCompletion(object):
    def on_get(self, req, resp, idx_name):
        try:
            LOGGER_.info(f"Getting title completion from {idx_name} with req {json.dumps(req.params, indent=2)}")

            results = ES.search(index=idx_name,
                                body={
                                    'query': {
                                        'match_phrase_prefix': {
                                            'title.completion': req.params['prefix']
                                        }
                                    },
                                    '_source': {
                                        'excludes': ['verses', 'bible-refs']
                                    },
                                })
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(results)
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)


class Suggester(object):
    def on_get(self, req, resp, idx_name):
        try:
            LOGGER_.info(
                f"Getting search suggestions from {idx_name} with req {json.dumps(req.params, indent=2)}"
            )

            results = ES.search(index=idx_name,
                                body={
                                    'suggest': {
                                        'text': req.params['q'],
                                        'simple_phrase': {
                                            'phrase': {
                                                'field':
                                                'verses.text.suggesting',
                                                'size': 1,
                                                'gram_size': 4,
                                                'max_errors': 4,
                                                'direct_generator': [{
                                                    'field': 'verses.text.suggesting',
                                                    'suggest_mode': 'popular',
                                                }],
                                                'highlight': {
                                                    'pre_tag': '<em>',
                                                    'post_tag': '</em>'
                                                },
                                                "collate": {
                                                    "query": {
                                                        "source": {
                                                            "match": {
                                                                "{{field_name}}": "{{suggestion}}"
                                                            }
                                                        }
                                                    },
                                                    "params": {
                                                        "field_name": "verses.text.folded"
                                                    },
                                                    "prune": True
                                                }
                                            }
                                        }
                                    }
                                })
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(results)
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)


class Similar(object):
    def on_get(self, req, resp, idx_name):
        try:
            LOGGER_.info(f"Getting similar documents from {idx_name} with req {json.dumps(req.params, indent=2)}")

            results = ES.search(index=idx_name,
                                body={
                                    'query': {
                                        'more_like_this': {
                                            'fields': ["verses.text", "verses.text.folded"],
                                            'like': [{
                                                '_id': req.params['id']
                                            }],
                                            'min_term_freq': 3,
                                            'min_word_length': 4,
                                            'minimum_should_match': '50%'
                                        },
                                    },
                                    '_source': {
                                        'excludes': ['verses', 'bible-refs']
                                    },
                                    'size': 4
                                })
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(results)
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)


class Favorites(object):
    auth = {
        'auth_disabled': True
    }

    dbsByIndexName = {}

    def __init__(self):
        self.public_key = os.environ.get("APPLE_APP_PKEY")

    def getClient(self, idx_name):
        LOGGER_.info(f"Creating Mongo db connection for {idx_name}...")
        return MongoClient('comori-od-mongo',
                            username=os.environ.get("MONGO_USERNAME"),
                            password=os.environ.get("MONGO_PASSWORD"))

    def getDb(self, idx_name):
        if idx_name not in self.dbsByIndexName:
            db = self.dbsByIndexName[idx_name] = self.getClient(idx_name)[f"comori_{idx_name}"]
            self.createIndexes(idx_name, db)
            return db

        return self.dbsByIndexName[idx_name]

    def getCollection(self, idx_name, name):
        return self.getDb(idx_name)[name]

    def on_get(self, req, resp, idx_name):
        try:
            LOGGER_.info(f"Getting favorites from {idx_name} with req {json.dumps(req.params, indent=2)}")

            auth = jwt.decode(req.get_header("Authorization"), self.public_key, algorithms='RS256')
            favs = [fav for fav in self.getCollection(idx_name, 'favorites').find({'uid': self.getUserId(auth)})]

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(favs)
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)

    def on_delete(self, req, resp, idx_name, article_id):
        try:
            LOGGER_.info(
                f"Removing favorite from {idx_name} with id {article_id} and req {json.dumps(req.params, indent=2)}"
            )

            auth = jwt.decode(req.get_header("Authorization"), self.public_key, algorithms='RS256')
            favid = self.getDocumentId(auth, article_id)

            LOGGER_.info(f"Attempting to remove favorite {favid} from {idx_name}...")
            self.getCollection(idx_name, 'favorites').delete_one({'_id': favid})

            resp.status = falcon.HTTP_200
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)

    def on_post(self, req, resp, idx_name):
        try:
            LOGGER_.info(f"Adding favorite to {idx_name} with req {json.dumps(req.params, indent=2)}")

            auth = jwt.decode(req.get_header("Authorization"), self.public_key, algorithms='RS256')
            data = json.loads(req.stream.read())

            data['_id'] = self.getDocumentId(auth, data['id'])
            data['uid'] = self.getUserId(auth)

            self.getCollection(idx_name, 'favorites').insert_one(data)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps({"message": "You have saved the article '{}'!".format(data['title'])})
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            LOGGER_.error("Request handling failed! Error: {}".format(ex), exc_info=True)

    def createIndexes(self, idx_name, db):
        LOGGER_.info(f"Creating favorites indexes for {idx_name}...")

        db['favorites'].create_index([('uid', pymongo.ASCENDING)], unique=False)

    def getUserId(self, auth):
        return "{}.{}".format(auth['sub'], auth['iss'])

    def getDocumentId(self, auth, article_id):
        return "{}.{}.{}".format(auth['sub'], auth['iss'], article_id)

class TotpAuthBackend(AuthBackend):
    def __init__(self):
        key = os.environ['API_TOTP_KEY'] if os.environ.get('API_TOTP_KEY') else random_base32()
        logging.info("TOTP key: {}".format(key))
        self.totp = TOTP(key)
        self.auth_header_prefix = "Token"

    def _extract_credentials(self, req):
        auth = req.get_header('Authorization')
        return self.parse_auth_token_from_request(auth_header=auth)

    def authenticate(self, req, resp, resource):
        try:
            token = self._extract_credentials(req)
            if not token or not self.totp.verify(token, None, 120):
                raise falcon.HTTPUnauthorized(title='401 Unauthorized',
                                            description='Invalid Token',
                                            challenges=None)
        except Exception as ex:
            LOGGER_.error("Authorization handling failed! Error: {}".format(ex), exc_info=True)
            raise

    def get_auth_token(self, user_payload):
        """
        Extracts token from the `user_payload`
        """
        token = user_payload.get('token') or None
        if not token:
            raise ValueError('`user_payload` must provide api token')

        return '{auth_header_prefix} {token}'.format(
            auth_header_prefix=self.auth_header_prefix, token=token)


def load_app(cfg_filepath):
    logging.config.fileConfig('logging.conf')

    global LOGGER_
    LOGGER_ = logging.getLogger(__name__)

    cfg = {}
    with open(cfg_filepath, 'r') as cfg_file:
        cfg = yaml.full_load(cfg_file)

    global ES
    ES = Elasticsearch(hosts=[cfg['es']],
                       http_auth=(os.getenv("ELASTIC_USER", "elastic"),
                                  os.getenv("ELASTIC_PASSWORD", "")))

    logging.info("Cfg: {}".format(json.dumps(cfg, indent=2)))

    totpAuth = TotpAuthBackend()
    authMiddleware = FalconAuthMiddleware(totpAuth, None, ["OPTIONS", "GET"])
    app = falcon.API(middleware=[HandleCORS(), authMiddleware])

    index = Index()
    articles = Articles()
    content = ContentHandler()
    authors = FieldAggregator('author', [])
    types = FieldAggregator('type', [])
    volumes = FieldAggregator('volume', ['author'])
    books = FieldAggregator('book', ['author', 'volume'])
    titles = Titles()
    titlesCompletion = TitlesCompletion()
    suggester = Suggester()
    similar = Similar()
    favorites = Favorites()

    app.add_route('/{idx_name}', index)
    app.add_route('/{idx_name}/articles', articles)
    app.add_route('/{idx_name}/authors', authors)
    app.add_route('/{idx_name}/authors/{value}', authors)
    app.add_route('/{idx_name}/types', types)
    app.add_route('/{idx_name}/types/{value}', types)
    app.add_route('/{idx_name}/volumes', volumes)
    app.add_route('/{idx_name}/volumes/{value}', volumes)
    app.add_route('/{idx_name}/books', books)
    app.add_route('/{idx_name}/books/{value}', books)
    app.add_route('/{idx_name}/content', content)
    app.add_route('/{idx_name}/titles', titles)
    app.add_route('/{idx_name}/titles/completion', titlesCompletion)
    app.add_route('/{idx_name}/suggest/', suggester)
    app.add_route('/{idx_name}/articles/similar', similar)
    app.add_route('/{idx_name}/favorites', favorites)
    app.add_route('/{idx_name}/favorites/{article_id}', favorites)

    return app