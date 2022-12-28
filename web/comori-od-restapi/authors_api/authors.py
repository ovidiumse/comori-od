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

        self._authors_by_name = None

    def getAuthorsByName(self, idx_name):
        if self._authors_by_name:
            return self._authors_by_name
        
        col = self.getCollection(idx_name, 'authors')
        self._authors_by_name = {}
        authors = [self.removeInternalFields(a) for a in col.find({})]
        for a in authors:
            self._authors_by_name[a['name']] = a

        return self._authors_by_name

    @req_handler("Handling authors GET", __name__)
    def on_get(self, req, resp, idx_name):
        results = self.getValues(idx_name, req)
        
        authors_by_name = self.getAuthorsByName(idx_name)

        buckets = results['aggregations']['authors']['buckets']

        authors_added = False
        for name, data in authors_by_name.items():
            found = False
            for bucket in buckets:
                if bucket['key'] == name:
                    found = True
                    for k, v in data.items():
                        bucket[k] = v
            if not found:
                authors_added = True
                if 'key' not in data:
                    data['key'] = name
                buckets.append(data)

        if authors_added:
            results['aggregations']['authors']['buckets'] = buckets

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