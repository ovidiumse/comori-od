import simplejson as json
from unidecode import unidecode
from api_utils import *

LOGGER_ = logging.getLogger(__name__)
ES = None

class FieldAggregator():
    def __init__(self, es, fieldName, aggs):
        global ES
        if ES is None:
            ES = es

        self.fieldName = fieldName
        self.aggs = aggs

    @timeit("Aggregating values", __name__)
    def getValues(self, idx_name, req):
        LOGGER_.info(f"Getting {self.fieldName}s from {idx_name} with req {json.dumps(req.params, indent=2)}")

        include_unmatched = 'include_unmatched' in req.params

        q = urllib.parse.unquote(req.params['q']) if 'q' in req.params else None
        filters = parseFilters(req)

        query_body = {
            'query': buildQuery(buildShouldMatch(q), filters),
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
                        },
                        'min_date_added': {
                            'min': {
                                'field': 'date_added'
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