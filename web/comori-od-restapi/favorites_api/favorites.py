import falcon
import simplejson as json
import logging
from collections import defaultdict
from cachetools import LRUCache
from mongoclient import MongoClient
from mobileappsvc import MobileAppService
from api_utils import req_handler

LOGGER_ = logging.getLogger(__name__)

def make_cache():
    return LRUCache(10)

class FavoritesHandler(MongoClient, MobileAppService):
    def __init__(self):
        MongoClient.__init__(self)
        MobileAppService.__init__(self)

        self.cache_ = defaultdict(make_cache)

    def removeInternalFields(self, item):
        del item['uid']
        del item['_id']
        return item

    @req_handler("Getting favorites", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting favorites from {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))
        user_id = self.getUserId(auth)

        user_cache = self.cache_.get(user_id)
        cache_key = req.url
        cached_response = user_cache.get(cache_key) if user_cache else None
        if cached_response:
            resp.status = falcon.HTTP_200
            resp.body = cached_response
        else:
            LOGGER_.info(f"Looking up favorites for uid {user_id}")

            favs = [
                self.removeInternalFields(fav)
                for fav in self.getCollection(idx_name, 'favorites').find({'uid': user_id})
            ]

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(favs)
            self.cache_[user_id][cache_key] = resp.body

    @req_handler("Deleting favorite", __name__)
    def on_delete(self, req, resp, idx_name, article_id):
        LOGGER_.info(
            f"Removing favorite from {idx_name} with id {article_id} and req {json.dumps(req.params, indent=2)}"
        )

        auth = self.authorize(req.get_header("Authorization"))
        user_id = self.getUserId(auth)
        user_cache = self.cache_.get(user_id)
        if user_cache:
            LOGGER_.info(f"Clearing favorites cache for uid {user_id}")
            user_cache.clear()

        favid = self.getDocumentId(auth, article_id)

        LOGGER_.info(f"Removing favorite {favid} from {idx_name}...")
        response = self.getCollection(idx_name, 'favorites').delete_one({'_id': favid, 'uid': user_id})
        if response.deleted_count < 1:
            raise falcon.HTTPNotFound()

        resp.status = falcon.HTTP_200

    @req_handler("Adding favorite", __name__)
    def on_post(self, req, resp, idx_name):
        LOGGER_.info(f"Adding favorite to {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))
        user_id = self.getUserId(auth)
        user_cache = self.cache_.get(user_id)
        if user_cache:
            LOGGER_.info(f"Clearing favorites cache for uid {user_id}")
            user_cache.clear()

        data = json.loads(req.stream.read())

        data['_id'] = self.getDocumentId(auth, data['id'])
        data['uid'] = self.getUserId(auth)
        data['timestamp'] = self.fmtUtcNow()

        self.getCollection(idx_name, 'favorites').insert_one(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(self.removeInternalFields(data))