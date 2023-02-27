import simplejson as json
from cachetools import LRUCache
from collections import defaultdict
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
        self.volumesAggregator_ = FieldAggregator(es, 'volume', ['author'])
        self.booksAggregator_ = FieldAggregator(es, 'book', ['author'])
        self.cache_ = LRUCache(100)

        self.authors_by_name_ = None
        self.books_by_author_ = None
        self.volumes_by_author_ = None

    @timeit("Getting books by author", __name__)
    def getBooksByAuthor(self, idx_name, req):
        if self.books_by_author_:
            return self.books_by_author_

        self.books_by_author_ = defaultdict(list)
        response = self.booksAggregator_.getValues(idx_name, req)
        for bucket in response['aggregations']['books']['buckets']:
            author = ",".join([b['key'] for b in bucket['authors']['buckets']])
            self.books_by_author_[author].append(bucket['key'])

        return self.books_by_author_

    @timeit("Getting volumes by author", __name__)
    def getVolumesByAuthor(self, idx_name, req):
        if self.volumes_by_author_:
            return self.volumes_by_author_

        self.volumes_by_author_ = defaultdict(list)
        response = self.volumesAggregator_.getValues(idx_name, req)
        for bucket in response['aggregations']['volumes']['buckets']:
            author = ",".join([b['key'] for b in bucket['authors']['buckets']])
            self.volumes_by_author_[author].append(bucket['key'])
        
        return self.volumes_by_author_

    @timeit("Getting authors by name", __name__)
    def getAuthorsByName(self, idx_name):
        if self.authors_by_name_:
            return self.authors_by_name_
        
        col = self.getCollection(idx_name, 'authors')
        self.authors_by_name_ = {}
        authors = [self.removeInternalFields(a) for a in col.find({})]
        for a in authors:
            self.authors_by_name_[a['name']] = a

        return self.authors_by_name_

    @timeit("Adding authors info", __name__)
    def addAuthorInfo(self, idx_name, response):
        authors_by_name = self.getAuthorsByName(idx_name)

        authors_added = False
        buckets = response['aggregations']['authors']['buckets']
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
            response['aggregations']['authors']['buckets'] = buckets

    @timeit("Filtering author volumes", __name__)
    def filterAuthorVolumes(self, idx_name, req, response):
        volumes_by_author = self.getVolumesByAuthor(idx_name, req)

        for author_bucket in response['aggregations']['authors']['buckets']:
            if 'volumes' in author_bucket:
                author_bucket['volumes']['buckets'] = [b for b in author_bucket['volumes']['buckets'] if b['key'] in volumes_by_author[author_bucket['key']]]

    @timeit("Filtering author books", __name__)
    def filterAuthorBooks(self, idx_name, req, response):
        books_by_author = self.getBooksByAuthor(idx_name, req)

        for author_bucket in response['aggregations']['authors']['buckets']:
            if 'books' in author_bucket:
                author_bucket['books']['buckets'] = [b for b in author_bucket['books']['buckets'] if b['key'] in books_by_author[author_bucket['key']]]

    @timeit("Sorting authors", __name__)
    def sortAuthors(self, response):
        response['aggregations']['authors']['buckets'] = sorted(response['aggregations']['authors']['buckets'], key=lambda item: (item['position'], item.get('doc_count', 0)))

    @req_handler("Handling authors GET", __name__)
    def on_get(self, req, resp, idx_name):
        cache_key = req.url
        cached_response = self.cache_.get(cache_key)
        if cached_response:
            resp.status = falcon.HTTP_200
            resp.body = cached_response
        else:
            response = self.getValues(idx_name, req)

            self.addAuthorInfo(idx_name, response)
            self.filterAuthorVolumes(idx_name, req, response)
            self.filterAuthorBooks(idx_name, req, response)
            self.sortAuthors(response)        

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(response)
            self.cache_[cache_key] = resp.body
    
    @req_handler("Handling authors POST", __name__)
    def on_post(self, req, resp, idx_name):
        # clear cached authors
        LOGGER_.info("Clearing cached authors...")
        self.authors_by_name_ = None
        self.books_by_author_ = None
        self.volumes_by_author_ = None
        self.cache_.clear()

        authors = json.loads(req.stream.read())

        author_names = set()
        for a in authors:
            author_names.add(a['name'])

        LOGGER_.info(f"Indexing {len(authors)} authors into {idx_name}...")

        modifiedCnt = 0
        upsertedCnt = 0
        deletedCnt = 0

        col = self.getCollection(idx_name, 'authors')
        db_authors = [a for a in col.find({})]
        for a in db_authors:
            if a['name'] not in author_names:
                response = col.delete_one({'_id': a['_id']})
                deletedCnt += response.deleted_count
        
        for a in authors:
            result = col.update_one({'name': a['name']}, {'$set': a}, upsert=True)
            modifiedCnt += result.modified_count
            upsertedCnt += 1 if result.upserted_id else 0

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'modifiedCnt': modifiedCnt, 'upsertedCnt': upsertedCnt, 'deletedCnt': deletedCnt})