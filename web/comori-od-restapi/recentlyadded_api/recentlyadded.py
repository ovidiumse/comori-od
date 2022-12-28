from pymongo.message import _do_batched_insert
import simplejson as json
from datetime import datetime, timedelta
from aggregates_api import FieldAggregator
from api_utils import *

class RecentlyAddedBooksHandler(FieldAggregator):
    def __init__(self, es, authorsByName={}):
        FieldAggregator.__init__(self, es, 'book', ['author', 'volume'])

        self.authorsByName = authorsByName

    @req_handler("Handling recently added books GET", __name__)
    def on_get(self, req, resp, idx_name):
        lastMonth = (datetime.utcnow() - timedelta(days=30)).date()
        since = datetime.strptime(req.params['since'], '%Y-%m-%d').date() if 'since' in req.params else lastMonth
        limit = int(req.params['limit']) if 'limit' in req.params else 10
        include_author_photo = 'include_author_photo' in req.params

        results = self.getValues(idx_name, req, order={'min_insert_ts': 'asc'})

        def collect_authors(buckets):
            authors = []
            for bucket in buckets:
                if bucket['key'] in self.authorsByName:
                    author_info = self.authorsByName[bucket['key']]
                    author_data = {}
                    for k, v in author_info.items():
                        if k == 'name' or 'url' in k:
                            author_data[k] = v
                    authors.append(author_data)

            return authors

        def collect_keys(buckets):
            keys = []
            for bucket in buckets:
                keys.append(bucket['key'])

            return keys

        books = []
        book_buckets = [book for book in results['aggregations']['books']['buckets']]
        for bucket in book_buckets:
            date_added = datetime.strptime(bucket['min_date_added']['value_as_string'], '%Y-%m-%dT%H:%M:%S.%fZ')
            if date_added.date() <= since:
                continue

            books.append({
                'name': bucket['key'],
                'date_added': date_added.date().isoformat(),
                'doc_count': bucket['doc_count'],
                'authors': collect_authors(bucket['authors']['buckets']) if include_author_photo else collect_keys(bucket['authors']['buckets']),
                'volume': collect_keys(bucket['volumes']['buckets'])[0]
            })

        books = sorted(books, key=lambda b: b['date_added'], reverse=True)[:limit]

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(books)