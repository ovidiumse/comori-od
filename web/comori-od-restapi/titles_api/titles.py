import falcon
import simplejson as json
import logging
from api_utils import req_handler, parseFilters, buildQueryAggregations

ES = None
LOGGER_ = logging.getLogger(__name__)

class TitlesHandler(object):
    def __init__(self, es):
        global ES
        if ES is None:
            ES = es

    @req_handler("Getting titles", __name__)
    def on_get(self, req, resp, idx_name):
        filters = parseFilters(req)
        LOGGER_.info(f"Quering titles from {idx_name} with req {json.dumps(req.params, indent=2)}")

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

        response = ES.search(index=idx_name, body=query_body)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response.body)


class TitlesCompletionHandler(object):
    def __init__(self, es):
        global ES
        if ES is None:
            ES = es

    @req_handler("Getting title completions", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting title completion from {idx_name} with req {json.dumps(req.params, indent=2)}")

        results = ES.search(index=idx_name,
                            body={
                                'query': {
                                    'multi_match': {
                                        'query': req.params['prefix'],
                                        'type': 'bool_prefix',
                                        "fields": [
                                            "title.completion",
                                            "title.completion._2gram",
                                            "title.completion._3gram",
                                            "title.completion_stemmed_folded",
                                            "title.completion_stemmed_folded._2gram",
                                            "title.completion_stemmed_folded._3gram"
                                            "title.completion_folded_stemmed",
                                            "title.completion_folded_stemmed._2gram",
                                            "title.completion_folded_stemmed._3gram"
                                        ]
                                    }
                                },
                                '_source': {
                                    'excludes': ['verses', 'body', 'bible-refs']
                                },
                            })
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(results.body)