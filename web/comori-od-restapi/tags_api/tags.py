import logging
import falcon
import simplejson as json
from collections import defaultdict
from mongoclient import MongoClient
from mobileappsvc import MobileAppService
from api_utils import req_handler

LOGGER_ = logging.getLogger(__name__)

class TagsHandler(MongoClient, MobileAppService):

    @req_handler("Getting tags", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting tags from {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))            
        mkups = [mkup for mkup in self.getCollection(idx_name, 'markups').find({'uid': self.getUserId(auth)})]
        favs = [fav for fav in self.getCollection(idx_name, 'favorites').find({'uid': self.getUserId(auth)})]

        tagsByFreq = defaultdict(int)
        def process(items):
            for item in items:
                for tag in item['tags']:
                    tagsByFreq[tag] += 1
            
        process(mkups)
        process(favs)            
        
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(tagsByFreq)