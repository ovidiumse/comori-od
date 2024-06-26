import falcon
import simplejson as json
import logging
from cachetools import LRUCache
from collections import defaultdict
from bson.objectid import ObjectId
from mongoclient import MongoClient
from mobileappsvc import MobileAppService
from api_utils import req_handler

LOGGER_ = logging.getLogger(__name__)

def make_cache():
    return LRUCache(10)

class MarkupsHandler(MongoClient, MobileAppService):
    def __init__(self):
        MongoClient.__init__(self)
        MobileAppService.__init__(self)

        self.cache_ = defaultdict(make_cache)

    def removeInternalFields(self, markup):
        del markup['uid']
        return markup

    @req_handler("Getting markups", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting markups from {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))
        user_id = self.getUserId(auth)

        user_cache = self.cache_.get(user_id)
        cache_key = req.url
        cached_response = user_cache.get(cache_key) if user_cache else None
        if cached_response:
            resp.status = falcon.HTTP_200
            resp.body = cached_response
        else:
            LOGGER_.info(f"Looking up markups for uid {user_id}...")
            mkups = [
                self.removeInternalFields(markup)
                for markup in self.getCollection(idx_name, 'markups').find({'uid': user_id})
            ]

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(mkups)
            self.cache_[user_id][cache_key] = resp.body

    @req_handler("Deleting markup", __name__)
    def on_delete(self, req, resp, idx_name, markup_id):
        LOGGER_.info(
            f"Removing markup from {idx_name} with id {markup_id} and req {json.dumps(req.params, indent=2)}"
        )

        auth = self.authorize(req.get_header("Authorization"))

        user_id = self.getUserId(auth)
        user_cache = self.cache_.get(user_id)
        if user_cache:
            LOGGER_.info(f"Clearing markups cache for uid {user_id}")
            user_cache.clear()

        col = self.getCollection(idx_name, 'markups')

        LOGGER_.info(f"Attempting to remove markup {markup_id} from {idx_name}...")
        result = col.delete_one({'_id': markup_id, 'uid': user_id})
        if result.deleted_count == 0:
            raise falcon.HTTPNotFound()

        resp.status = falcon.HTTP_200

    @req_handler("Adding markup", __name__)
    def on_post(self, req, resp, idx_name):
        LOGGER_.info(f"Adding markup to {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))
        user_id = self.getUserId(auth)
        user_cache = self.cache_.get(user_id)
        if user_cache:
            LOGGER_.info(f"Clearing markups cache for uid {user_id}")
            user_cache.clear()

        data = json.loads(req.stream.read())
        data["_id"] = str(ObjectId())
        data['uid'] = self.getUserId(auth)
        data['timestamp'] = self.fmtUtcNow()

        self.getCollection(idx_name, 'markups').insert_one(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(self.removeInternalFields(data))