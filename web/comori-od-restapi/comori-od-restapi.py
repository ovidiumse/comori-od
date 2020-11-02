#!/usr/bin/pypy3
import re
import os
import falcon
from falcon_auth import FalconAuthMiddleware
from falcon_auth.backends import AuthBackend
import simplejson as json
import logging
import logging.config
import urllib
import yaml
import requests
from pyotp import TOTP, random_base32
from elasticsearch import Elasticsearch, TransportError, helpers
from falcon.http_status import HTTPStatus

LOGGER_ = None
ES = None


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
            ES.index(index=idx_name, body=json.dumps(article))
            return True
        except Exception as ex:
            LOGGER_.error("Indexing {} failed!".format(article), exc_info=True)
            return False

    def query(self, idx_name, req):
        limit = req.params['limit'] if 'limit' in req.params else 100
        offset = req.params['offset'] if 'offset' in req.params else 0
        q = urllib.parse.unquote(req.params['q'])

        search_fields = {
            'title': 2, 
            'title.folded': 2, 
            'verses.text': 1, 
            'verses.text.folded': 1
        }

        should_match = []
        for field, boost in search_fields.items():
            should_match.append({
                "match_phrase": {
                    field: {
                        "query": q,
                        "slop": 4,
                        "boost": boost
                    }
                }
            })

        fuzzy_query = []
        for w in re.split('[ \|\,\.\!]', q):
            fuzzy_query.append("{}~{}".format(w, int(min(3, len(w) / 4))))

        should_match.append({
            "simple_query_string": {
                "query": " ".join(fuzzy_query),
                "fields": ["title^2", "title.folded^2", "verses.text", "verses.text.folded"],
                "default_operator": "AND",
                "analyzer": "folding_stop",
                "boost": 0.001
            }
        })

        query_body = {
            'query': {
                'bool': {
                    'should': should_match,
                },
            },
            '_source': {
                'excludes': ['verses', 'bible-refs']
            },
           'highlight': {
                'fields': {
                    'title': {
                        "matched_fields": ["title", "title.folded"],
                        'type': 'fvh'
                    },
                    'verses.text': {
                        "matched_fields": ["verses.text", "verses.text.folded"],
                        'type': 'fvh'
                    }
                },
                "order": "score"
            },
            'size': limit,
            'from': offset
        }

        return ES.search(index=idx_name, body=query_body)

    def getById(self, idx_name, req):
        return ES.get(index=idx_name, id=req.params['id'])

    def getRandomArticle(self, idx_name, req):
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

    def on_get(self, req, resp, idx_name, doc_type):
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

    def on_post(self, req, resp, idx_name, doc_type):
        articles = json.loads(req.stream.read())
        indexed = 0

        try:
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
            logging.error("Posting articles failed! Error: {}".format(ex), exc_info=True)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})
            logging.error("Posting articles failed! Error: {}".format(ex), exc_info=True)


class Titles(object):
    def on_get(self, req, resp, idx_name):
        try:
            results = ES.search(index=idx_name,
                                body={
                                    'suggest': {
                                        'article-suggest': {
                                            'prefix': req.params['prefix'],
                                            'completion': {
                                                'field': 'title.completion'
                                            }
                                        }
                                    },
                                    '_source': {
                                        'excludes': ['verses']
                                    },
                                    'size': 10
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


class TitlesCompletion(object):
    def on_get(self, req, resp, idx_name):
        try:
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
    def on_get(self, req, resp, idx_name, doc_type):
        try:
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
                                        'excludes': ['verses.text']
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


class TotpAuthBackend(AuthBackend):
    def __init__(self):
        key = os.environ['API_TOTP_KEY'] if os.environ['API_TOTP_KEY'] else random_base32()
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
                       http_auth=(os.environ["ELASTIC_USER"],
                                  os.environ["ELASTIC_PASSWORD"]))

    logging.info("Cfg: {}".format(json.dumps(cfg, indent=2)))

    totpAuth = TotpAuthBackend()
    authMiddleware = FalconAuthMiddleware(totpAuth, None, ["OPTIONS", "GET"])
    app = falcon.API(middleware=[HandleCORS(), authMiddleware])

    index = Index()
    articles = Articles()
    titles = Titles()
    titlesCompletion = TitlesCompletion()
    suggester = Suggester()
    similar = Similar()

    app.add_route('/{idx_name}', index)
    app.add_route('/{idx_name}/{doc_type}', articles)
    app.add_route('/{idx_name}/titles', titles)
    app.add_route('/{idx_name}/titles/completion', titlesCompletion)
    app.add_route('/{idx_name}/suggest/', suggester)
    app.add_route('/{idx_name}/{doc_type}/similar', similar)

    return app
