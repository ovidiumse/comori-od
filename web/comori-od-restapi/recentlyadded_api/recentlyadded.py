import simplejson as json
import logging
from cachetools import LRUCache
from datetime import datetime, timedelta
from aggregates_api import FieldAggregator
from api_utils import *
from authors_api import AuthorsHandler

LOGGER_ = logging.getLogger(__name__)


class RecentlyAddedBooksHandler(FieldAggregator):
    def __init__(self, es, authorsHandler: AuthorsHandler):
        FieldAggregator.__init__(self, es, 'book', ['author', 'volume'])

        self.authorsHandler_ = authorsHandler
        self.cache_ = LRUCache(10)

    @req_handler("Handling recently added books GET", __name__)
    def on_get(self, req, resp, idx_name):
        lastMonth = (datetime.utcnow() - timedelta(days=30)).date()
        since = datetime.strptime(req.params['since'], '%Y-%m-%d').date() if 'since' in req.params else lastMonth
        limit = int(req.params['limit']) if 'limit' in req.params else 20

        LOGGER_.info(f"Getting {limit} recently added books since {since}")

        cache_key = f'recentlyaddedbooks_{since}_{limit}'
        response = self.cache_.get(cache_key)
        if response:
            resp.status = falcon.HTTP_200
            resp.body = response
        else:
            LOGGER_.info("Computing recently added books...")

            results = self.getValues(idx_name, req, order={'min_insert_ts': 'asc'})
            authorsByName = self.authorsHandler_.getAuthorsByName(idx_name)

            def collect_authors(buckets):
                authors = []
                for bucket in buckets:
                    if bucket['key'] in authorsByName:
                        author_info = authorsByName[bucket['key']]
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
                    'authors': collect_authors(bucket['authors']['buckets']),
                    'volume': collect_keys(bucket['volumes']['buckets'])[0]
                })

            books = sorted(books, key=lambda b: b['date_added'], reverse=True)[:limit]

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(books)

            self.cache_[cache_key] = resp.body