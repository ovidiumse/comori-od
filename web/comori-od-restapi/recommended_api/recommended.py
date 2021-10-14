import logging
import falcon
import simplejson as json
from api_utils import req_handler

ES = None
LOGGER_ = logging.getLogger(__name__)

class RecommendedHandler(object):
    def __init__(self,  es):
        global ES
        ES = es
        
    @req_handler("Getting recommended articles", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting recommended articles from {idx_name} with req {json.dumps(req.params, indent=2)}")

        limit = req.params['limit'] if 'limit' in req.params else 1

        articles = ES.search(index=idx_name,
                        body={
                            'query': {
                                'function_score': {
                                    'random_score': {}
                                }
                            },
                            '_source': {
                                    'excludes': ['verses', 'bible-refs']
                            },
                            'size': limit,
                        })
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(articles)