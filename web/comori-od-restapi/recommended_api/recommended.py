import logging
import falcon
import simplejson as json
from datetime import datetime, timedelta
from mongoclient import MongoClient
from mobileappsvc import MobileAppService
from api_utils import req_handler

ES = None
LOGGER_ = logging.getLogger(__name__)

class RecommendedHandler(MongoClient, MobileAppService):
    def __init__(self,  es, authorsByName={}):
        MobileAppService.__init__(self)
        
        global ES
        ES = es

        self.authorsByName = authorsByName

    def removeInternalFields(self, item):
        del item['_id']
        del item['uid']
        return item

    @req_handler("Getting recommended articles", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting recommended articles from {idx_name} with req {json.dumps(req.params, indent=2)}")

        limit = int(req.params['limit']) if 'limit' in req.params else 10

        auth = self.authorize(req.get_header("Authorization", required=True))
        readArticles = [
            self.removeInternalFields(read)
            for read in self.getCollection(idx_name, 'readArticles').find({'uid': self.getUserId(auth)})
        ]

        if not readArticles:
            resp.status = falcon.HTTP_200
            resp.body = json.dumps([])
            return

        readArticles = sorted(readArticles, key=lambda a: a['timestamp'], reverse=True)
        lastReadTimestamp = datetime.strptime(readArticles[0]['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
        aWeekBeforeLastRead = lastReadTimestamp - timedelta(days=7)
        maxReadArticleCandidatesCnt = 5
        readArticles = [read for read in readArticles
                        if read['timestamp'] > f"{aWeekBeforeLastRead.isoformat()}Z"][:maxReadArticleCandidatesCnt]

        readIds = [read['id'] for read in readArticles]
        likes = [{'_id': id} for id in readIds]
        query_body = {
            'query': {
                'more_like_this': {
                    'fields': ["title", "verses.text", "verses.text.folded"],
                    'like': likes,
                    'min_term_freq': 10,
                    'min_word_length': 4,
                    'minimum_should_match': '80%',
                    'max_query_terms': 50
                },
            },
            '_source': {
                'excludes': ['verses', 'body', 'bible-refs']
            },
            'size': limit + len(readArticles)
        }

        response = ES.search(index=idx_name, body=query_body)
        hits = response['hits']['hits']

        # filter out already read articles
        sources = []
        for hit in hits:
            if hit['_id'] in readIds:
                continue

            source = hit['_source']
            source['_id'] = hit['_id']
            source['_score'] = hit['_score']
            if source['author'] in self.authorsByName:
                author_info = self.authorsByName[source['author']]
                for k, v in author_info.items():
                    if 'url' in k:
                        source[f'author-{k}'] = v

            sources.append(source)

        sources = sources[:limit]

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(sources)