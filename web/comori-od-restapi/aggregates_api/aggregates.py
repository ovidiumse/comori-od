import simplejson as json
from cachetools import LRUCache
from unidecode import unidecode
from api_utils import *

LOGGER_ = logging.getLogger(__name__)

class FieldAggregator():
    def __init__(self, es, fieldName, aggs, authorsHandler=None):
        self.es_ = es
        self.fieldName = fieldName
        self.aggs = aggs
        self.authorsHandler_ = authorsHandler
        self.cache_ = LRUCache(1000)

    @timeit("Aggregating values", __name__)
    def getValues(self, idx_name, req, order=None):
        LOGGER_.info(f"Getting {self.fieldName}s from {idx_name} with req {json.dumps(req.params, indent=2)}")

        include_unmatched = 'include_unmatched' in req.params

        q = urllib.parse.unquote(req.params['q']).strip() if 'q' in req.params else None
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

        if order:
            query_body['aggs'][f'{self.fieldName}s']['terms']['order'] = order

        for agg in self.aggs:
            aggs_body = query_body['aggs'][f'{self.fieldName}s']['aggs']
            aggs_body[f'{agg}s'] = {'terms': {'field': agg, 'size': 100}}

        resp = self.es_.search(index=idx_name, body=query_body, timeout="1m")
        data = resp.body
        authorsByName = self.authorsHandler_.getAuthorsByName(idx_name) if self.authorsHandler_ else None

        if authorsByName:
            for bucket in data['aggregations'][f'{self.fieldName}s']['buckets']:
                if 'authors' in bucket:
                    for author_bucket in bucket['authors']['buckets']:
                        if author_bucket['key'] in authorsByName:
                            author_info = authorsByName[author_bucket['key']]
                            for k, v in author_info.items():
                                if 'url' in k:
                                    author_bucket[k] = v

        return data

    @req_handler("Aggregated fields GET", __name__)
    def on_get(self, req, resp, idx_name):
        cache_key = req.url
        cached_response = self.cache_.get(cache_key)
        if cached_response:
            resp.status = falcon.HTTP_200
            resp.text = cached_response
        else:
            LOGGER_.info(f"Computing aggregated values for {req.url}")
            results = self.getValues(idx_name, req, order={'min_insert_ts': 'asc'})
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(results)
            self.cache_[cache_key] = resp.text

    @req_handler("Deleting content", __name__)
    def on_delete(self, req, resp, idx_name, value):
        LOGGER_.info(f"Clearing cache for {req.url}")
        self.cache_.clear()

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

        self.es_.delete_by_query(index=idx_name, body=query)
        resp.status = falcon.HTTP_200