import falcon
import simplejson as json
import logging
from mongoclient import MongoClient
from mobileappsvc import MobileAppService
from api_utils import req_handler

LOGGER_ = logging.getLogger(__name__)

class UsersHandler(MongoClient, MobileAppService):

    @req_handler("Deleting user", __name__)
    def on_delete(self, req, resp, idx_name):
        auth = self.authorize(req.get_header("Authorization"))   
        userId = self.getUserId(auth)

        LOGGER_.info(f"Removing user {userId}... with req {json.dumps(req.params, indent=2)}")

        response = {}
        LOGGER_.info(f"Removing favorites for user {userId}...")
        r = self.getCollection(idx_name, 'favorites').delete_many({'uid': userId})
        response['removed_fav_cnt'] = r.deleted_count

        LOGGER_.info(f"Removing markups for user {userId}...")
        r = self.getCollection(idx_name, 'markups').delete_many({'uid': userId})
        response['removed_markup_cnt'] = r.deleted_count

        LOGGER_.info(f"Removing readArticles for user {userId}...")
        r = self.getCollection(idx_name, 'readArticles').delete_many({'uid': userId})
        response['removed_read_articles_cnt'] = r.deleted_count

        resp.status = falcon.HTTP_200
        resp.text = json.dumps(response)