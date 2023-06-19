import logging
import falcon
import simplejson as json
from datetime import datetime, timedelta
from mongoclient import MongoClient
from mobileappsvc import MobileAppService
from api_utils import req_handler

LOGGER_ = logging.getLogger(__name__)

class RecommendedHandler(MongoClient, MobileAppService):
    def __init__(self,  es):
        MongoClient.__init__(self)
        MobileAppService.__init__(self)

        self.es_ = es

    def removeInternalFields(self, item):
        del item['_id']
        del item['uid']
        return item

    @req_handler("Getting recommended articles", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting recommended articles from {idx_name} with req {json.dumps(req.params, indent=2)}")

        limit = int(req.params['limit']) if 'limit' in req.params else 10

        auth = self.authorize(req.get_header("Authorization", required=True))
        uid = self.getUserId(auth)

        readArticles = [
            self.removeInternalFields(read)
            for read in self.getCollection(idx_name, 'readArticles').find({'uid': uid})
        ]

        if not readArticles:
            LOGGER_.info(f"No read articles for user {uid}!")
            resp.status = falcon.HTTP_200
            resp.body = json.dumps([])
            return

        readArticles = sorted(readArticles, key=lambda a: a['timestamp'], reverse=True)
        readIds = [read['id'] for read in readArticles]
        
        def filterAlreadyRead(hits):
            sources = []
            for hit in hits:
                if hit['_id'] in readIds:
                    continue

                source = hit['_source']
                source['_id'] = hit['_id']
                source['_score'] = hit['_score']
                sources.append(source)

            return sources
            
        recommended_by_id = {}
        recommended = []
        for read in readArticles:
            query_body = {
                'query': {
                    'more_like_this': {
                        'fields': ["body", "body.folded"],
                        'like': [{'_id': read['id']}],
                        'min_term_freq': 1,
                        'min_word_length': 4,
                        'minimum_should_match': '80%',
                        'max_query_terms': 20
                    },
                },
                '_source': {
                    'excludes': ['verses', 'body', 'bible-refs']
                },
                'size': limit + len(readArticles)
            }

            response = self.es_.search(index=idx_name, body=query_body)
            hits = response['hits']['hits']
            unread_hits = filterAlreadyRead(hits)

            recommended_by_id[read['id']] = {'recommended': len(hits), 'read': len(hits) - len(unread_hits)}
            recommended += unread_hits

            if len(recommended) >= limit:
                recommended = recommended[:limit]
                break

        LOGGER_.info(f"User {uid} has {len(recommended)} recommended articles: \n{json.dumps(recommended_by_id, indent=2)}")
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(recommended)