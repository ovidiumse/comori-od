import re
import falcon
import logging
import urllib
import simplejson as json
from cachetools import LRUCache
from elasticsearch import helpers
from datetime import datetime, timezone
from api_utils import *

LOGGER_ = logging.getLogger(__name__)

class ArticlesHandler(object):
    def __init__(self, es):
        self.doc_cnt = None
        self._es = es
        self.cache_ = LRUCache(10000)

    @timeit("Indexing article", __name__)
    def index(self, idx_name, article):
        try:
            LOGGER_.info(f"Indexing article {article['title']} from {article['book']} into {idx_name}...")

            self._es.index(index=idx_name, body=json.dumps(article))
            return True
        except Exception as ex:
            LOGGER_.error("Indexing {} failed!".format(article), exc_info=True)
            return False

    @timeit("Articles query", __name__)
    def query(self, idx_name, req):
        limit = int(req.params['limit']) if 'limit' in req.params else 100
        offset = int(req.params['offset']) if 'offset' in req.params else 0
        q = urllib.parse.unquote(req.params['q']).strip()

        include_aggs = 'include_aggs' in req.params
        include_unmatched = 'include_unmatched' in req.params

        filters = parseFilters(req)
        LOGGER_.info(f"Quering {idx_name} with req {json.dumps(req.params, indent=2)}")

        should_match = buildShouldMatch(q)
        should_match_highlight = buildShouldMatchHighlight(q)

        query_body = {
            'query': buildQuery(should_match, filters),
            '_source': {
                'excludes': ['verses', 'body', 'bible-refs']
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
                    'body': {
                        "matched_fields": ["body", "body.folded", "body.stemmed_folded", "body.folded_stemmed"],
                        'type': 'fvh'
                    }
                },
                "boundary_scanner": "chars",
                "number_of_fragments": 4,
                "fragment_size": 1000,
                "order": "none"
            },
            'sort': ['_score', {'title.keyword': 'asc'}, {'book': 'asc'}],
            'size': limit,
            'from': offset
        }

        if include_aggs:
            query_body['aggs'] = buildQueryAggregations(include_unmatched)

        # print("Query: {}".format(json.dumps(query_body, indent=2)))

        resp = self._es.search(index=idx_name, body=query_body, timeout="1m")
        return resp.body

    @timeit("Getting highlighted article by id", __name__)
    def getHighlightedById(self, idx_name, req):
        LOGGER_.info(f"Getting highlighted article from {idx_name} with request {json.dumps(req.params, indent=2)}")

        highlight = req.params["highlight"]
        should_match_highlight = buildShouldMatchHighlight(highlight)
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
                'excludes': ['verses', 'body', 'bible-refs']
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
        search_response = self._es.search(index=idx_name, body=query_body, timeout="1m")
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

        resp = self._es.get(index=idx_name, id=req.params['id'])
        return resp.body

    @timeit("Getting article", __name__)
    def getArticle(self, idx_name, req):
        if "highlight" in req.params:
            return self.getHighlightedById(idx_name, req)
        else:
            return self.getById(idx_name, req)

    @timeit("Getting doc count", __name__)
    def getDocCnt(self, idx_name):
        if not self.doc_cnt or idx_name not in self.doc_cnt:
            LOGGER_.info(f"Getting doc count from {idx_name}")

            if not self.doc_cnt:
                self.doc_cnt = {}

            resp = self._es.search(index=idx_name,
                         body={
                             'query': {
                                 'match_all': {}
                             },
                             "sort": [{"_insert_idx": "asc"}, {"book": "asc"}],
                             'size': 1,
                             'from': 0
                         })

            self.doc_cnt[idx_name] = resp["hits"]["total"]["value"]

        return self.doc_cnt[idx_name]

    def getDaysSinceEpoch(self):
        epoch_date = datetime(1970, 1, 1).date()
        today = datetime.now(timezone.utc).date()
        return (today - epoch_date).days

    @timeit("Getting random article", __name__)
    def getDailyArticle(self, idx_name, req):
        LOGGER_.info(f"Getting daily article from {idx_name} with request {json.dumps(req.params, indent=2)}")

        daysSinceEpoch = self.getDaysSinceEpoch()
        docCount = self.getDocCnt(idx_name)
        LOGGER_.info(f"Days since epoch: {daysSinceEpoch}, doc count: {docCount}, day index: {daysSinceEpoch % docCount}")

        limit = int(req.params['limit']) if 'limit' in req.params else 1
        offset = int(req.params['offset']) if 'offset' in req.params else daysSinceEpoch % docCount

        resp = self._es.search(index=idx_name,
                         body={
                             'query': {
                                 'match_all': {}
                             },
                             "sort": [{"_insert_idx": "asc"}, {"book": "asc"}],
                             'size': limit,
                             'from': offset
                         })
        return resp.body

    @req_handler("Handling articles GET", __name__)
    def on_get(self, req, resp, idx_name, id=None):
        cache_key = req.url
        cached_response = self.cache_.get(cache_key)
        if cached_response:
            resp.status = falcon.HTTP_200
            resp.body = cached_response
        else:
            LOGGER_.info(f"Making articles query for {req.url}")

            if 'q' in req.params:
                response = self.query(idx_name, req)
            elif 'id' in req.params:
                response = self.getArticle(idx_name, req)
            elif id is not None:
                # this is a replacement for the nginx data files
                # for localhost testing (where nginx is not used)
                req.params['id'] = id
                response = self.getArticle(idx_name, req)
                response['_source']['_id'] = response['_id']
                response = response['_source']
            else:
                response = self.getDailyArticle(idx_name, req)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(response)
            self.cache_[cache_key] = resp.body

    @req_handler("Handling articles POST", __name__)
    def on_post(self, req, resp, idx_name):
        articles = json.loads(req.stream.read())

        indexed = 0

        LOGGER_.info(f"Indexing {len(articles)} articles into {idx_name}...")

        for a in articles:
            a['_index'] = idx_name

        indexed, _ = helpers.bulk(self._es, articles, stats_only=True)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'total': len(articles), 'indexed': indexed})


class SearchTermSuggester(object):
    def __init__(self, es):
        self._es = es

    @req_handler("Getting search suggestions", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(
            f"Getting search suggestions from {idx_name} with req {json.dumps(req.params, indent=2)}"
        )

        results = self._es.search(index=idx_name,
                            body={
                                'suggest': {
                                    'text': req.params['q'].strip(),
                                    'simple_phrase': {
                                        'phrase': {
                                            'field':
                                            'body.suggesting',
                                            'size': 1,
                                            'gram_size': 4,
                                            'max_errors': 4,
                                            'direct_generator': [{
                                                'field': 'body.suggesting',
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
                                                    "field_name": "body.folded"
                                                },
                                                "prune": True
                                            }
                                        }
                                    }
                                }
                            })
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(results.body)


class SimilarArticlesHandler(object):
    def __init__(self, es):
        self._es = es

    @req_handler("Getting similar articles", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting similar documents from {idx_name} with req {json.dumps(req.params, indent=2)}")

        results = self._es.search(index=idx_name,
                            body={
                                'query': {
                                    'more_like_this': {
                                        'fields': ["title", "body", "body.folded"],
                                        'like': [{
                                            '_id': req.params['id']
                                        }],
                                        'min_term_freq': 10,
                                        'min_word_length': 4,
                                        'minimum_should_match': '80%',
                                        'max_query_terms': 50
                                    },
                                },
                                '_source': {
                                    'excludes': ['verses', 'body', 'bible-refs']
                                },
                                'size': 4
                            })

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(results.body)
