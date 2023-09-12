import logging
import falcon
import simplejson as json
import math
from collections import defaultdict
from cachetools import LRUCache, TTLCache
from datetime import datetime, timedelta
from mongoclient import MongoClient
from mobileappsvc import MobileAppService
from api_utils import req_handler
from authors_api import AuthorsHandler

LOGGER_ = logging.getLogger(__name__)

def make_cache():
    return LRUCache(10)

READ_ARTICLES_CACHE = defaultdict(make_cache)

class ReadArticlesHandler(MongoClient, MobileAppService):
    def removeInternalFields(self, item):
        del item['_id']
        del item['uid']
        return item

    @req_handler("Getting read articles", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting read articles from {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))

        user_id = self.getUserId(auth)
        client_cache = READ_ARTICLES_CACHE.get(user_id)
        cache_key = f"{req.url}"
        cached_response = client_cache.get(cache_key) if client_cache else None
        if cached_response:
            resp.status = falcon.HTTP_200
            resp.body = cached_response
        else:
            readArticles = [
                self.removeInternalFields(read)
                for read in self.getCollection(idx_name, 'readArticles').find({'uid': user_id})
            ]

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(readArticles)
            READ_ARTICLES_CACHE[user_id][cache_key] = resp.body

    @req_handler("Adding read article", __name__)
    def on_post(self, req, resp, idx_name):
        LOGGER_.info(f"Adding read article to {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))
        user_id = self.getUserId(auth)
        if user_id in READ_ARTICLES_CACHE:
            LOGGER_.info(f"Clearing read articles cache for uid {user_id}...")
            READ_ARTICLES_CACHE[user_id].clear()

        data = json.loads(req.stream.read())
        if not isinstance(data, dict):
            raise falcon.HTTPInvalidParam("Input should be a dictionary!")

        data["_id"] = self.getDocumentId(auth, data['id'])
        data['uid'] = user_id

        self.getCollection(idx_name, 'readArticles').insert_one(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(self.removeInternalFields(data))

    @req_handler("Updating read article", __name__)
    def on_patch(self, req, resp, idx_name, article_id):
        LOGGER_.info(f"Updating read article {article_id} to {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))
        user_id = self.getUserId(auth)
        if user_id in READ_ARTICLES_CACHE:
            LOGGER_.info(f"Clearing read articles cache for uid {user_id}...")
            READ_ARTICLES_CACHE[user_id].clear()

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
        user_id = self.getUserId(auth)
        if user_id in READ_ARTICLES_CACHE:
            LOGGER_.info(f"Clearing read articles cache for uid {user_id}...")
            READ_ARTICLES_CACHE[user_id].clear()

        readArticles = json.loads(req.stream.read())
        if not isinstance(readArticles, list):
            raise falcon.HTTPInvalidParam("Input should be an array!")

        if not readArticles:
            raise falcon.HTTPInvalidParam("The list of read articles is empty!")

        for data in readArticles:
            data["_id"] = self.getDocumentId(auth, data['id'])
            data['uid'] = user_id

        result = self.getCollection(idx_name, 'readArticles').insert_many(readArticles)
        if len(result.inserted_ids) == 0:
            raise falcon.HTTPInternalServerError("Inserting read articles failed!")

        resp.status = falcon.HTTP_201
        resp.body = json.dumps({"InsertedCnt": len(result.inserted_ids)})

    @req_handler("Updating read articles in bulk", __name__)
    def on_patch(self, req, resp, idx_name):
        LOGGER_.info(f"Updating read articles in bulk to {idx_name} with req {json.dumps(req.params, indent=2)}")

        auth = self.authorize(req.get_header("Authorization"))
        user_id = self.getUserId(auth)
        if user_id in READ_ARTICLES_CACHE:
            LOGGER_.info(f"Clearing read articles cache for uid {user_id}...")
            READ_ARTICLES_CACHE[user_id].clear()

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
                'uid': user_id},
                {'$set': read})

            updatedCnt += result.modified_count

        if updatedCnt == 0 and len(readArticles) > 0:
            raise falcon.HTTPNotFound()

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"UpdatedCnt": updatedCnt})

class TrendingArticlesHandler(MongoClient, MobileAppService):
    def __init__(self, authorsHandler: AuthorsHandler):
        super(TrendingArticlesHandler, self).__init__()

        self.authorsHandler_ = authorsHandler

    def removeInternalFields(self, item):
        del item['_id']
        del item['uid']
        return item

    @req_handler("Getting trending articles", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting trending articles from {idx_name} with req {json.dumps(req.params, indent=2)}")
        limit = int(req.params['limit']) if 'limit' in req.params else 10

        auth = self.authorize(req.get_header("Authorization", required=True))
        uid = self.getUserId(auth)

        LOGGER_.info("Computing treding articles...")

        today = datetime.utcnow()
        last30Days = today - timedelta(days=30)
        readArticles = [
            self.removeInternalFields(read) for read in self.getCollection(idx_name, 'readArticles').find(
                {'timestamp': {
                    '$gt': f"{last30Days.isoformat()}Z"
                }})
        ]

        userReadArticles = [
            self.removeInternalFields(read)
            for read in self.getCollection(idx_name, 'readArticles').find({'uid': uid})
        ]

        userReadIds = [read['id'] for read in userReadArticles]

        def filterAlreadyRead(articles):
            unreadArticles = []
            for article in articles:
                if article['id'] in userReadIds:
                    continue

                unreadArticles.append(article)

            return unreadArticles

        readStatsById = {}
        for read in readArticles:
            if read['id'] in readStatsById:
                readStats = readStatsById[read['id']]
            else:
                readStats = readStatsById[read['id']] = {'reach': 0, 'views': 0}

            outputKeys = ['id', 'author', 'book', 'volume', 'title']
            for key in read:
                if key not in outputKeys:
                    continue
                readStats[key] = read[key]

            readStats['reach'] += 1
            readStats['views'] += read['count']

        for _, stats in readStatsById.items():
            stats['score'] = stats['reach'] + math.sqrt(stats['views'] - stats['reach'])

        trendingArticles = [stats for _, stats in readStatsById.items() if stats['reach'] > 1]
        trendingArticles = sorted(trendingArticles, key=lambda x: x['score'], reverse=True)
        trendingArticles = filterAlreadyRead(trendingArticles)

        LOGGER_.info(f"User {uid} has {len(trendingArticles)} unread trending articles: \n{json.dumps(trendingArticles[:limit], indent=2)}")

        trendingArticles = trendingArticles[:limit]

        authorsByName = self.authorsHandler_.getAuthorsByName(idx_name)
        for article in trendingArticles:
            if article['author'] in authorsByName:
                author_info = authorsByName[article['author']]
                for k, v in author_info.items():
                    if 'url' in k:
                        article[f'author-{k}'] = v

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(trendingArticles)