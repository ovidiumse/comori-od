import falcon
import simplejson as json
import logging
import urllib
from elasticsearch import Elasticsearch, TransportError, helpers
from falcon.http_status import HTTPStatus

es = Elasticsearch(hosts=[{'host': "localhost", 'port': 9200}])


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
            es.indices.delete(index=idx_name)
            resp.status = falcon.HTTP_200
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})

    def on_get(self, req, resp, idx_name):
        try:
            mapping = es.indices.get_mapping(index=idx_name)
            settings = es.indices.get(index=idx_name)
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({'settings': settings, 'mapping': mapping})
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})

    def on_post(self, req, resp, idx_name):
        data = json.loads(req.stream.read())

        try:
            if es.indices.exists(idx_name):
                es.indices.delete(index=idx_name)

            es.indices.create(index=idx_name, body=data['settings'])
            es.indices.put_mapping(index=idx_name, body=data['mappings'])
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({})
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})


class Articles(object):
    def index(self, idx_name, article):
        try:
            es.index(index=idx_name, body=json.dumps(article))
        except Exception as ex:
            logging.error("Indexing {} failed!".format(article), exc_info=True)
            return False
        return True

    def query(self, idx_name, params):
        limit = params['limit'] if 'limit' in params else 100
        offset = params['offset'] if 'offset' in params else 0

        return es.search(index=idx_name,
                         body={
                             'query': {
                                 'simple_query_string': {
                                     'query': urllib.parse.unquote(params['q']),
                                     "fields": ['title', 'title.folded', 'verses', 'verses.folded'],
                                     "default_operator": "and"
                                 }
                             },
                             '_source': {
                                 'excludes': ['verses']
                             },
                             'highlight': {
                                 'fields': {
                                     'title': {
                                         'matched_fields': ['title', 'title_folded'],
                                         'type': 'fvh'
                                     },
                                     'verses': {
                                         'matched_fields': ['verses', 'verses.folded'],
                                         'type': 'fvh'
                                     },
                                 }
                             },
                             'size': limit,
                             'from': offset
                         })

    def getById(self, idx_name, params):
        return es.get(index=idx_name, id=params['id'])

    def on_get(self, req, resp, idx_name, doc_type):
        try:
            if 'q' in req.params:
                results = self.query(idx_name, req.params)
            else:
                results = self.getById(idx_name, req.params)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(results)
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})

    def on_post(self, req, resp, idx_name, doc_type):
        articles = json.loads(req.stream.read())
        indexed = 0

        try:
            for a in articles:
                a['_index'] = idx_name
            indexed, _ = helpers.bulk(es, articles, stats_only=True)
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
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})


class Titles(object):
    def on_get(self, req, resp, idx_name):
        try:
            results = es.search(index=idx_name,
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
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})


class TitlesCompletion(object):
    def on_get(self, req, resp, idx_name):
        try:
            results = es.search(index=idx_name,
                                body={
                                    'query': {
                                        'match_phrase_prefix': {
                                            'title.completion': req.params['prefix']
                                        }
                                    },
                                    '_source': {
                                        'excludes': ['verses']
                                    },
                                })
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(results)
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})


class Suggester(object):
    def on_get(self, req, resp, idx_name):
        try:
            results = es.search(
                index=idx_name,
                body={
                    'suggest': {
                        'text': req.params['q'],
                        'simple_phrase': {
                            'phrase': {
                                'field': 'verses.suggesting',
                                'size': 1,
                                'gram_size': 4,
                                'max_errors': 4,
                                'direct_generator': [{
                                    'field': 'verses.suggesting',
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
                                        "field_name": "verses.folded"
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
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})


class Similar(object):
    def on_get(self, req, resp, idx_name, doc_type):
        try:
            results = es.search(index=idx_name,
                                body={
                                    'query': {
                                        'more_like_this': {
                                            'fields': ["verses", "verses.folded"],
                                            'like': [{
                                                '_id': req.params['id']
                                            }],
                                            'min_term_freq': 3,
                                            'min_word_length': 4,
                                            'minimum_should_match': '50%'
                                        },
                                    },
                                    '_source': {
                                        'excludes': ['verses']
                                    },
                                    'size': 4
                                })
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(results)
        except TransportError as ex:
            resp.status = "{}".format(ex.status_code)
            resp.body = json.dumps({'exception': ex.error, 'info': ex.info})
        except Exception as ex:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({'exception': str(ex)})


logging.basicConfig(level=logging.INFO)

app = falcon.API(middleware=[HandleCORS()])

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