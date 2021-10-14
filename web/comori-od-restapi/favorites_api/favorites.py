import falcon
import simplejson as json
import logging
from mongoclient import MongoClient
from mobileappsvc import MobileAppService
from api_utils import req_handler

LOGGER_ = logging.getLogger(__name__)

class FavoritesHandler(MongoClient, MobileAppService):

    def removeInternalFields(self, item):
        del item['uid']
        del item['_id']
        return item

    @req_handler("Getting favorites", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting favorites from {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))            
        favs = [self.removeInternalFields(fav) for fav in self.getCollection(idx_name, 'favorites').find({
            'uid': self.getUserId(auth)
        })]

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(favs)

    @req_handler("Deleting favorite", __name__)
    def on_delete(self, req, resp, idx_name, article_id):
        LOGGER_.info(
            f"Removing favorite from {idx_name} with id {article_id} and req {json.dumps(req.params, indent=2)}"
        )

        auth = self.authorize(req.get_header("Authorization"))   
        favid = self.getDocumentId(auth, article_id)

        LOGGER_.info(f"Removing favorite {favid} from {idx_name}...")
        response = self.getCollection(idx_name, 'favorites').delete_one({'_id': favid, 'uid': self.getUserId(auth)})
        if response.deleted_count < 1: 
            raise falcon.HTTPNotFound()

        resp.status = falcon.HTTP_200

    @req_handler("Adding favorite", __name__)
    def on_post(self, req, resp, idx_name):
        LOGGER_.info(f"Adding favorite to {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))   
        data = json.loads(req.stream.read())

        data['_id'] = self.getDocumentId(auth, data['id'])
        data['uid'] = self.getUserId(auth)
        data['timestamp'] = self.fmtUtcNow()

        self.getCollection(idx_name, 'favorites').insert_one(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(self.removeInternalFields(data))