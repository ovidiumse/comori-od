import falcon
import simplejson as json
import logging
from cachetools import LRUCache
from api_utils import req_handler, parseFilters, buildQueryAggregations

LOGGER_ = logging.getLogger(__name__)

class TitlesHandler(object):
    def __init__(self, es):
        self.es_ = es
        self.cache_ = LRUCache(100)

    @req_handler("Getting titles", __name__)
    def on_get(self, req, resp, idx_name):
        filters = parseFilters(req)
        LOGGER_.info(f"Quering titles from {idx_name} with req {json.dumps(req.params, indent=2)}")

        cache_key = req.url
        cached_response = self.cache_.get(cache_key)
        if cached_response:
            resp.status = falcon.HTTP_200
            resp.text = cached_response
        else:
            LOGGER_.info(f"Looking up titles for {req.url}")
            limit = int(req.params['limit']) if 'limit' in req.params else 100
            offset = int(req.params['offset']) if 'offset' in req.params else 0
            include_aggs = 'include_aggs' in req.params

            query_body = {
                'query': {
                    'bool': {
                        'filter': filters
                    }
                },
                '_source': {
                    'excludes': ['verses', 'body', 'bible-refs'],
                },
                'size': limit,
                'from': offset,
                'sort': [{'_insert_idx': {'order': 'asc'}}]
            }

            if include_aggs:
                query_body['aggs'] = buildQueryAggregations(False)

            response = self.es_.search(index=idx_name, body=query_body)
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(response.body)
            self.cache_[cache_key] = resp.text


class TitlesCompletionHandler(object):
    def __init__(self, es):
        self.es_ = es
        self.cache_ = LRUCache(1000)

    @req_handler("Getting title completions", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting title completion from {idx_name} with req {json.dumps(req.params, indent=2)}")

        cache_key = req.url
        cached_response = self.cache_.get(cache_key)
        if cached_response:
            resp.status = falcon.HTTP_200
            resp.text = cached_response
        else:
            results = self.es_.search(index=idx_name,
                                body={
                                    'query': {
                                        'multi_match': {
                                            'query': req.params['prefix'].strip(),
                                            'type': 'bool_prefix',
                                            "fields": [
                                                "title.completion",
                                                "title.completion._2gram",
                                                "title.completion._3gram",
                                                "title.completion_stemmed_folded",
                                                "title.completion_stemmed_folded._2gram",
                                                "title.completion_stemmed_folded._3gram",
                                                "title.completion_folded_stemmed",
                                                "title.completion_folded_stemmed._2gram",
                                                "title.completion_folded_stemmed._3gram"
                                            ]
                                        }
                                    },
                                    '_source': {
                                        'excludes': ['verses', 'body', 'bible-refs']
                                    },
                                    'sort': [{'_insert_idx': {'order': 'asc'}}]
                                })
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(results.body)
            self.cache_[cache_key] = resp.text