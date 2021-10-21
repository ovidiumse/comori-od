import simplejson as json
from mongoclient import MongoClient
from aggregates_api import FieldAggregator
from api_utils import *

LOGGER_ = logging.getLogger(__name__)

class AuthorsHandler(MongoClient, FieldAggregator):
    def removeInternalFields(self, item):
        del item['_id']
        return item

    def __init__(self, es):
        FieldAggregator.__init__(self, es, 'author', ['volume', 'type', 'book'])

    @req_handler("Handling authors GET", __name__)
    def on_get(self, req, resp, idx_name):
        results = self.getValues(idx_name, req)
        
        col = self.getCollection(idx_name, 'authors')
        authorsByName = {}
        authors = [self.removeInternalFields(a) for a in col.find({})]
        for a in authors:
            authorsByName[a['name']] = a

        buckets = results['aggregations']['authors']['buckets']
        for b in buckets:
            if b['key'] in authorsByName:
                a = authorsByName[b['key']]
                for k, v in a.items():
                    b[k] = v

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(results)
    
    @req_handler("Handling authors POST", __name__)
    def on_post(self, req, resp, idx_name):
        authors = json.loads(req.stream.read())

        LOGGER_.info(f"Indexing {len(authors)} authors into {idx_name}...")

        modifiedCnt = 0
        upsertedCnt = 0
        col = self.getCollection(idx_name, 'authors')
        for a in authors:
            result = col.update_one({'name': a['name']}, {'$set': a}, upsert=True)
            modifiedCnt += result.modified_count
            upsertedCnt += 1 if result.upserted_id else 0

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'modifiedCnt': modifiedCnt, 'upsertedCnt': upsertedCnt})