import logging
import falcon
import simplejson as json
from mongoclient import MongoClient
from mobileappsvc import MobileAppService
from api_utils import req_handler

LOGGER_ = logging.getLogger(__name__)

class ReadArticlesHandler(MongoClient, MobileAppService):
    def removeInternalFields(self, item):
        del item['_id']
        del item['uid']
        return item

    @req_handler("Getting read articles", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting read articles from {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))            
        readArticles = [self.removeInternalFields(read) for read in self.getCollection(idx_name, 'readArticles').find({
            'uid': self.getUserId(auth)
        })]      
        
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(readArticles)

    @req_handler("Adding read article", __name__)
    def on_post(self, req, resp, idx_name):
        LOGGER_.info(f"Adding read article to {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))   
        data = json.loads(req.stream.read())
        if not isinstance(data, dict):
            raise falcon.HTTPInvalidParam("Input should be a dictionary!")

        data["_id"] = self.getDocumentId(auth, data['id'])
        data['uid'] = self.getUserId(auth)

        self.getCollection(idx_name, 'readArticles').insert_one(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(self.removeInternalFields(data))

    @req_handler("Updating read article", __name__)
    def on_patch(self, req, resp, idx_name, article_id):
        LOGGER_.info(f"Updating read article {article_id} to {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))   
        data = json.loads(req.stream.read())
        if not isinstance(data, dict):
            raise falcon.HTTPInvalidParam("Input should be a dictionary!")

        _id = self.getDocumentId(auth, article_id)
        if 'id' in data:
            del data['id']

        result = self.getCollection(idx_name, 'readArticles').update_one({
            '_id': _id, 
            'uid': self.getUserId(auth)}, 
            {'$set': data})

        if result.modified_count == 0:
            raise falcon.HTTPNotFound()

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"UpdatedCnt": result.modified_count})


class BulkReadArticlesHandler(MongoClient, MobileAppService):
    def removeInternalFields(self, item):
        del item['_id']
        del item['uid']
        return item
        
    @req_handler("Adding read articles in bulk", __name__)
    def on_post(self, req, resp, idx_name):
        LOGGER_.info(f"Adding read articles in bulk to {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))   
        readArticles = json.loads(req.stream.read())
        if not isinstance(readArticles, list):
            raise falcon.HTTPInvalidParam("Input should be an array!")

        if not readArticles:
            raise falcon.HTTPInvalidParam("The list of read articles is empty!")

        for data in readArticles:
            data["_id"] = self.getDocumentId(auth, data['id'])
            data['uid'] = self.getUserId(auth)

        result = self.getCollection(idx_name, 'readArticles').insert_many(readArticles)
        if len(result.inserted_ids) == 0:
            raise falcon.HTTPInternalServerError("Inserting read articles failed!")

        resp.status = falcon.HTTP_201
        resp.body = json.dumps({"InsertedCnt": len(result.inserted_ids)})

    @req_handler("Updating read articles in bulk", __name__)
    def on_patch(self, req, resp, idx_name):
        LOGGER_.info(f"Updating read articles in bulk to {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))   
        readArticles = json.loads(req.stream.read())
        if not isinstance(readArticles, list):
            raise falcon.HTTPInvalidParam("Input should be an array of objects!")
            
        if not readArticles:
            raise falcon.HTTPInvalidParam("The list of read articles is empty!")

        updatedCnt = 0
        for read in readArticles:   
            _id = self.getDocumentId(auth, read['id'])
            del read['id']
            result = self.getCollection(idx_name, 'readArticles').update_one({
                '_id': _id, 
                'uid': self.getUserId(auth)}, 
                {'$set': read})

            updatedCnt += result.modified_count

        if updatedCnt == 0 and len(readArticles) > 0:
            raise falcon.HTTPNotFound()

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"UpdatedCnt": updatedCnt})