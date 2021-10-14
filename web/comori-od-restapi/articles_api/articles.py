import re
import falcon
import logging
import urllib
import simplejson as json
from elasticsearch import helpers
from unidecode import unidecode
from api_utils import req_handler, timeit, parseFilters

LOGGER_ = logging.getLogger(__name__)
ES = None

class ArticlesHandler(object):
    def __init__(self, es):
        global ES
        if ES is None:
            ES = es

    @timeit("Indexing article", __name__)
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

        fields = [("title", 20), ("title.folded", 18),
                  ("verses.text", 10),
                  ("verses.text.folded", 8),
                  ("title.folded_stemmed", 4),
                  ("verses.text.folded_stemmed", 1)]

        for field, boost in fields:
            should_match.append({
                "intervals": {
                    field: {
                        "match": {
                            "query": q,
                            "max_gaps": 4,
                            "ordered": True
                        },
                        "boost": boost
                    }
                }
            })

        return should_match

    def buildShouldMatchHighlight(self, q):
        should_match_highlight = []
        should_match_highlight.append({
            "simple_query_string": {
                "query":
                "\"{}\"~{}".format(q, 4),
                "fields": [
                    "title^20", "title.folded^18",
                    "verses.text^10", "verses.text.folded^8",
                    "title.folded_stemmed^4",
                    "verses.text.folded_stemmed"
                ],
                "default_operator":
                "AND"
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

    @timeit("Articles query", __name__)
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
                        "matched_fields": ["title", "title.folded", "title.stemmed_folded", "title.folded_stemmed"],
                        'type': 'fvh'
                    },
                    'verses.text': {
                        "matched_fields":
                        ["verses.text", "verses.text.folded", "verses.text.stemmed_folded", "verses.text.folded_stemmed"],
                        'type': 'fvh'
                    }
                },
                "number_of_fragments": 6,
                "fragment_size": 100,
                "order": "score"
            },
            'sort': ['_score', {'title.keyword': 'asc'}, {'book': 'asc'}],
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
    
        # print("Query: {}".format(json.dumps(query_body, indent=2)))

        return ES.search(index=idx_name, body=query_body, timeout="1m")

    @timeit("Getting highlighted article by id", __name__)
    def getHighlightedById(self, idx_name, req):
        LOGGER_.info(f"Getting highlighted article from {idx_name} with request {json.dumps(req.params, indent=2)}")

        highlight = req.params["highlight"]
        should_match_highlight = self.buildShouldMatchHighlight(highlight)
        query_body = {
            "query": {
                "bool": {
                    "must": [{
                        "term": {
                            "_id": req.params["id"]
                        }
                    }]
                }
            },
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
                        "matched_fields": ["title", "title.folded", "title.stemmed_folded", "title.folded_stemmed"],
                        'type': 'fvh'
                    },
                    'verses.text': {
                        "matched_fields":
                        ["verses.text", "verses.text.folded", "verses.text.stemmed_folded", "verses.text.folded_stemmed"],
                        'type': 'fvh'
                    }
                },
                "number_of_fragments": 1000,
                "fragment_size": 10000
            },
        }

        removeHighlightTags = lambda text : re.sub(r'\<\/?em.*?\>', '', text)

        get_response = self.getById(idx_name, req)
        search_response = ES.search(index=idx_name, body=query_body, timeout="1m")
        if search_response["hits"]["total"]["value"] != 1:
            return get_response

        hit = search_response["hits"]["hits"][0]
        if "highlight" not in hit:
            return get_response

        highlight = hit["highlight"]
        if "verses.text" not in highlight:
            return get_response

        highlighted_verses = highlight["verses.text"]

        source = get_response["_source"]
        highlighted_title = highlight["title"][0] if "title" in highlight else None
        if highlighted_title and removeHighlightTags(highlighted_title) == source["title"]:
            source["title"] = highlighted_title

        source_verses = source["verses"]

        lastIndex = 0
        for highlightIndex in range(0, len(highlighted_verses)):
            for verseIndex in range(lastIndex, len(source_verses)):
                highlighted_verse = highlighted_verses[highlightIndex]
                verse = source_verses[verseIndex]
                for chunkIndex in range(0, len(verse)):
                    chunk = verse[chunkIndex]

                    if removeHighlightTags(highlighted_verse) == chunk['text']:
                        lastIndex = verseIndex
                        verse[chunkIndex]['text'] = highlighted_verse
                        break

        return get_response

    @timeit("Getting article by id", __name__)
    def getById(self, idx_name, req):
        LOGGER_.info(f"Getting article from {idx_name} with request {json.dumps(req.params, indent=2)}")

        return ES.get(index=idx_name, id=req.params['id'])

    @timeit("Getting article", __name__)
    def getArticle(self, idx_name, req):
        if "highlight" in req.params:
            return self.getHighlightedById(idx_name, req)
        else:
            return self.getById(idx_name, req)

    @timeit("Getting random article", __name__)
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

    @req_handler("Handling articles GET", __name__)
    def on_get(self, req, resp, idx_name):
        if 'q' in req.params:
            results = self.query(idx_name, req)
        elif 'id' in req.params:
            results = self.getArticle(idx_name, req)
        else:
            results = self.getRandomArticle(idx_name, req)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(results)

    @req_handler("Handling articles POST", __name__)
    def on_post(self, req, resp, idx_name):
        articles = json.loads(req.stream.read())
        indexed = 0

        LOGGER_.info(f"Indexing {len(articles)} into {idx_name}...")

        for a in articles:
            a['_index'] = idx_name
        indexed, _ = helpers.bulk(ES, articles, stats_only=True)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'total': len(articles), 'indexed': indexed})


class FieldAggregator(ArticlesHandler):
    def __init__(self, es, fieldName, aggs):
        super(FieldAggregator, self).__init__(es)

        self.fieldName = fieldName
        self.aggs = aggs

    @timeit("Aggregating values", __name__)
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

    @req_handler("Aggregated fields GET", __name__)
    def on_get(self, req, resp, idx_name):
        results = self.getValues(idx_name, req)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(results)

    @req_handler("Deleting content", __name__)
    def on_delete(self, req, resp, idx_name, value):
        LOGGER_.info(f"Deleting content where {self.fieldName} is {unidecode(value)} (unidecoded)...")

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
        resp.status = falcon.HTTP_200


class SearchTermSuggester(object):
    def __init__(self, es):
        global ES
        if ES is None:
            ES = es

    @req_handler("Getting search suggestions", __name__)
    def on_get(self, req, resp, idx_name):
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


class SimilarArticlesHandler(object):
    def __init__(self, es):
        global ES
        if ES is None:
            ES = es

    @req_handler("Getting similar articles", __name__)
    def on_get(self, req, resp, idx_name):
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