import falcon
import logging
import simplejson as json
from api_utils import req_handler, timeit, parseFilters

ES = None
LOGGER_ = logging.getLogger(__name__)

class ContentHandler(object):
    def __init__(self, es):
        global ES
        ES = es

    @req_handler("Handling content GET", __name__)
    def on_get(self, req, resp, idx_name):
        filters = parseFilters(req)
        LOGGER_.info(f"Quering contents from {idx_name} with req {json.dumps(req.params, indent=2)}")

        limit = int(req.params['limit']) if 'limit' in req.params else 10000
        offset = int(req.params['offset']) if 'offset' in req.params else 0

        query_body = {
            'query': {
                'bool': {
                    'filter': filters
                }
            },
            'size': limit,
            'from': offset,
            'sort': [{'_insert_idx': {'order': 'asc'}}]
        }

        response = ES.search(index=idx_name, body=query_body)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)