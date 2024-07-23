import os
import re
import falcon
import logging
import urllib
import simplejson as json
from collections import defaultdict
from cachetools import LRUCache
from elasticsearch import helpers
from datetime import datetime, timezone
from odrefs_api import OdRefsHandler
from api_utils import *

LOGGER_ = logging.getLogger(__name__)

class BibleArticlesHandler(object):
    def __init__(self, es):
        self.doc_cnt = None
        self._es = es
        self.cache_ = LRUCache(10000)

    @timeit("Indexing Bible article", __name__)
    def index(self, article):
        try:
            LOGGER_.info(f"Indexing article {article['title']} from {article['book']} into Bible...")

            self._es.index(index='bible', body=json.dumps(article))
            return True
        except Exception as ex:
            LOGGER_.error("Indexing {} failed!".format(article), exc_info=True)
            return False

    @timeit("Bible query", __name__)
    def query(self, req):
        limit = int(req.params['limit']) if 'limit' in req.params else 100
        offset = int(req.params['offset']) if 'offset' in req.params else 0
        q = urllib.parse.unquote(req.params['q']).strip()

        include_aggs = 'include_aggs' in req.params
        include_unmatched = 'include_unmatched' in req.params

        filters = parseFilters(req)
        LOGGER_.info(f"Quering Bible with req {json.dumps(req.params, indent=2)}")

        should_match = buildShouldMatch(q)
        should_match_highlight = buildShouldMatchHighlight(q)

        query_body = {
            'query': buildQuery(should_match, filters),
            '_source': {
                'excludes': ['verses', 'body', 'references']
            },
            'highlight': {
                'highlight_query': {
                    'bool': {
                        'should': should_match_highlight
                    }
                },
                'fields': {
                    'title': {
                        "matched_fields": ["title", "title.folded", "title.stemmed_folded", "title.folded_stemmed"],
                        'type': 'fvh'
                    },
                    'body': {
                        "matched_fields": ["body", "body.folded", "body.stemmed_folded", "body.folded_stemmed"],
                        'type': 'fvh'
                    }
                },
                "boundary_scanner": "chars",
                "number_of_fragments": 4,
                "fragment_size": 1000,
                "order": "none"
            },
            'sort': ['_score', {'title.keyword': 'asc'}, {'book': 'asc'}],
            'size': limit,
            'from': offset
        }


        if include_aggs:
            query_body['aggs'] = buildQueryAggregations(include_unmatched)

        # print("Query: {}".format(json.dumps(query_body, indent=2)))

        resp = self._es.search(index='bible', body=query_body, timeout="1m")
        return resp.body

    @timeit("Getting Bible highlighted article by id", __name__)
    def getHighlightedById(self, req):
        LOGGER_.info(f"Getting highlighted article from Bible with request {json.dumps(req.params, indent=2)}")

        highlight = req.params["highlight"]
        should_match_highlight = buildShouldMatchHighlight(highlight)
        query_body = {
            "query": {
                "bool": {
                    "must": [{
                        "term": {
                            "_id": req.params["id"]
                        }
                    }]
                }
            },
            '_source': {
                'excludes': ['verses', 'body', 'references']
            },
            'highlight': {
                'highlight_query': {
                    'bool': {
                        'should': should_match_highlight
                    }
                },
                'fields': {
                    'title': {
                        "matched_fields": ["title", "title.folded", "title.stemmed_folded", "title.folded_stemmed"],
                        'type': 'fvh'
                    },
                    'body': {
                        "matched_fields":
                        ["body", "body.folded", "body.stemmed_folded", "body.folded_stemmed"],
                        'type': 'fvh'
                    }
                },
                "number_of_fragments": 1000,
                "fragment_size": 10000
            },
        }

        removeHighlightTags = lambda text : re.sub(r'\<\/?em.*?\>', '', text)

        get_response = self.getById(req)
        search_response = self._es.search(index='bible', body=query_body, timeout="1m")
        if search_response["hits"]["total"]["value"] != 1:
            return get_response

        hit = search_response["hits"]["hits"][0]
        if "highlight" not in hit:
            return get_response

        highlight = hit["highlight"]
        if "body" not in highlight:
            return get_response

        highlighted_verses = highlight["body"]

        source = get_response["_source"]
        highlighted_title = highlight["title"][0] if "title" in highlight else None
        if highlighted_title and removeHighlightTags(highlighted_title) == source["title"]:
            source["title"] = highlighted_title

        source_verses = source["verses"]

        lastIndex = 0
        for highlightIndex in range(0, len(highlighted_verses)):
            for verseIndex in range(lastIndex, len(source_verses)):
                highlighted_verse = highlighted_verses[highlightIndex]
                verse = source_verses[verseIndex]
                for chunkIndex in range(0, len(verse)):
                    chunk = verse[chunkIndex]

                    if removeHighlightTags(highlighted_verse) == chunk['text']:
                        lastIndex = verseIndex
                        verse[chunkIndex]['text'] = highlighted_verse
                        break

        return get_response

    @timeit("Getting article by id", __name__)
    def getById(self, req):
        LOGGER_.info(f"Getting article from Bible with request {json.dumps(req.params, indent=2)}")

        resp = self._es.get(index='bible', id=req.params['id'])
        return resp

    @timeit("Getting Bible article", __name__)
    def getArticle(self, req):
        if "highlight" in req.params:
            return self.getHighlightedById(req)
        else:
            return self.getById(req)

    @timeit("Getting doc count", __name__)
    def getDocCnt(self):
        if not self.doc_cnt:
            LOGGER_.info(f"Getting doc count from Bible")

            resp = self._es.search(index='bible',
                         body={
                             'query': {
                                 'match_all': {}
                             },
                             "sort": [{"_insert_idx": "asc"}],
                             'size': 1,
                             'from': 0
                         })

            self.doc_cnt = resp["hits"]["total"]["value"]

        return self.doc_cnt

    def getDaysSinceEpoch(self):
        epoch_date = datetime(1970, 1, 1).date()
        today = datetime.now(timezone.utc).date()
        return (today - epoch_date).days

    @timeit("Getting Bible random article", __name__)
    def getDailyArticle(self, req):
        LOGGER_.info(f"Getting daily article from Bible with request {json.dumps(req.params, indent=2)}")

        daysSinceEpoch = self.getDaysSinceEpoch()
        docCount = self.getDocCnt()
        LOGGER_.info(f"Days since epoch: {daysSinceEpoch}, doc count: {docCount}, day index: {daysSinceEpoch % docCount}")

        limit = int(req.params['limit']) if 'limit' in req.params else 1
        offset = int(req.params['offset']) if 'offset' in req.params else daysSinceEpoch % docCount

        resp = self._es.search(index='bible',
                         body={
                             'query': {
                                 'match_all': {}
                             },
                             "sort": [{"_insert_idx": "asc"}, {"book": "asc"}],
                             'size': limit,
                             'from': offset
                         })
        return resp

    @req_handler("Handling Bible articles GET", __name__)
    def on_get(self, req, resp, id=None):
        cache_key = req.url
        cached_response = self.cache_.get(cache_key)
        if cached_response:
            resp.status = falcon.HTTP_200
            resp.text = cached_response
        else:
            LOGGER_.info(f"Making Bible articles query for {req.url}")

            if 'q' in req.params:
                response = self.query(req)
            elif 'id' in req.params:
                response = self.getArticle(req)
            elif id is not None:
                # this is a replacement for the nginx data files
                # for localhost testing (where nginx is not used)
                req.params['id'] = id
                response = self.getArticle(req)
                response['_source']['_id'] = response['_id']
                response = response['_source']
            else:
                response = self.getDailyArticle(req)

            resp.status = falcon.HTTP_200
            resp.text = json.dumps(response)
            self.cache_[cache_key] = resp.text

    @req_handler("Handling Bible articles POST", __name__)
    def on_post(self, req, resp):
        articles = json.loads(req.stream.read())

        indexed = 0

        LOGGER_.info(f"Indexing {len(articles)} articles into Bible...")

        for a in articles:
            a['_index'] = 'bible'

        indexed, _ = helpers.bulk(self._es, articles, stats_only=True)

        resp.status = falcon.HTTP_200
        resp.text = json.dumps({'total': len(articles), 'indexed': indexed})


class BibleBookHandler(object):
    @req_handler("Handling Bible books GET", __name__)
    def on_get(self, req, resp):
        response = {
            "Vechiul Testament": [
                { 'name': 'Geneza', 'shortName': 'Gen', 'chapters': 50 },
                { 'name': 'Exodul', 'shortName': 'Exod', 'chapters': 40 },
                { 'name': 'Leviticul', 'shortName': 'Lev', 'chapters': 27},
                { 'name': 'Numeri', 'shortName': 'Num', 'chapters': 36},
                { 'name': 'Deuteronomul', 'shortName': 'Deut', 'chapters': 34},
                { 'name': 'Iosua', 'shortName': 'Ios', 'chapters': 24},
                { 'name': 'Judecatorii', 'shortName': 'Jud', 'chapters': 21},
                { 'name': 'Rut', 'shortName': 'Rut', 'chapters': 4},
                { 'name': '1 Samuel', 'shortName': '1 Sam', 'chapters': 31},
                { 'name': '2 Samuel', 'shortName': '2 Sam', 'chapters': 24},
                { 'name': '1 Imparati', 'shortName': '1 Imp', 'chapters': 22},
                { 'name': '2 Imparati', 'shortName': '2 Imp', 'chapters': 25},
                { 'name': '1 Cronici', 'shortName': '1 Cron', 'chapters': 29},
                { 'name': '2 Cronici', 'shortName': '2 Cron', 'chapters': 36},
                { 'name': 'Ezra', 'shortName': 'Ezra', 'chapters': 10},
                { 'name': 'Neemia', 'shortName': 'Neem', 'chapters': 13},
                { 'name': 'Estera', 'shortName': 'Estera', 'chapters': 10},
                { 'name': 'Iov', 'shortName': 'Iov', 'chapters': 42},
                { 'name': 'Psalmii', 'shortName': 'Ps', 'chapters': 150},
                { 'name': 'Proverbele', 'shortName': 'Prov', 'chapters': 31},
                { 'name': 'Eclesiastul', 'shortName': 'Ecl', 'chapters': 12},
                { 'name': 'Cantarea Cantarilor', 'shortName': 'Cant', 'chapters': 8},
                { 'name': 'Isaia', 'shortName': 'Isa', 'chapters': 66},
                { 'name': 'Ieremia', 'shortName': 'Ier', 'chapters': 52},
                { 'name': 'Plangerile Lui Ieremia', 'shortName': 'Plang', 'chapters': 5},
                { 'name': 'Ezechiel', 'shortName': 'Ezec', 'chapters': 48},
                { 'name': 'Daniel', 'shortName': 'Dan', 'chapters': 12},
                { 'name': 'Osea', 'shortName': 'Osea', 'chapters': 14},
                { 'name': 'Ioel', 'shortName': 'Ioel', 'chapters': 3},
                { 'name': 'Amos', 'shortName': 'Amos', 'chapters': 9},
                { 'name': 'Obadia', 'shortName': 'Obad', 'chapters': 1},
                { 'name': 'Iona', 'shortName': 'Iona', 'chapters': 4},
                { 'name': 'Mica', 'shortName': 'Mica', 'chapters': 7},
                { 'name': 'Naum', 'shortName': 'Naum', 'chapters': 3},
                { 'name': 'Habacuc', 'shortName': 'Hab', 'chapters': 3},
                { 'name': 'Tefania', 'shortName': 'Tef', 'chapters': 3},
                { 'name': 'Hagai', 'shortName': 'Hag', 'chapters': 2},
                { 'name': 'Zaharia', 'shortName': 'Zah', 'chapters': 14},
                { 'name': 'Maleahi', 'shortName': 'Mal', 'chapters': 4}
            ],
            "Noul Testament": [
                { 'name': 'Matei', 'shortName': 'Mat', 'chapters': 28},
                { 'name': 'Marcu', 'shortName': 'Marc', 'chapters': 16},
                { 'name': 'Luca', 'shortName': 'Luca', 'chapters': 24},
                { 'name': 'Ioan', 'shortName': 'Ioan', 'chapters': 21},
                { 'name': 'Faptele Apostolilor', 'shortName': 'Fapte', 'chapters': 28},
                { 'name': 'Romani', 'shortName': 'Rom', 'chapters': 16},
                { 'name': '1 Corinteni', 'shortName': '1 Cor', 'chapters': 16},
                { 'name': '2 Corinteni', 'shortName': '2 Cor', 'chapters': 13},
                { 'name': 'Galateni', 'shortName': 'Gal', 'chapters': 6},
                { 'name': 'Efeseni', 'shortName': 'Efes', 'chapters': 6},
                { 'name': 'Filipeni', 'shortName': 'Fil', 'chapters': 4},
                { 'name': 'Coloseni', 'shortName': 'Col', 'chapters': 4},
                { 'name': '1 Tesaloniceni', 'shortName': '1 Tes', 'chapters': 5},
                { 'name': '2 Tesaloniceni', 'shortName': '2 Tes', 'chapters': 3},
                { 'name': '1 Timotei', 'shortName': '1 Tim', 'chapters': 6},
                { 'name': '2 Timotei', 'shortName': '2 Tim', 'chapters': 4},
                { 'name': 'Tit', 'shortName': 'Tit', 'chapters': 3},
                { 'name': 'Filimon', 'shortName': 'Filim', 'chapters': 1},
                { 'name': 'Evrei', 'shortName': 'Evr', 'chapters': 13},
                { 'name': 'Iacov', 'shortName': 'Iac', 'chapters': 5},
                { 'name': '1 Petru', 'shortName': '1 Pet', 'chapters': 5},
                { 'name': '2 Petru', 'shortName': '2 Pet', 'chapters': 3},
                { 'name': '1 Ioan', 'shortName': '1 Ioan', 'chapters': 5},
                { 'name': '2 Ioan', 'shortName': '2 Ioan', 'chapters': 1},
                { 'name': '3 Ioan', 'shortName': '3 Ioan', 'chapters': 1},
                { 'name': 'Iuda', 'shortName': 'Iuda', 'chapters': 1},
                { 'name': 'Apocalipsa', 'shortName': 'Apoc', 'chapters': 22}
            ]
        }

        resp.status = falcon.HTTP_200
        resp.text = json.dumps(response)

class BibleChapterHandler(object):
    def __init__(self, es, odRefsHandler: OdRefsHandler):

        self._es = es
        self._odRefsHandler = odRefsHandler

        try:
            self._bibleAliases = self._fromJsonFile("data/bible-aliases.json")
            self._bibleRootNameByAlias = self._fromJsonFile("data/bible-root-names.json")
            self._reverseBibleRefs = self._fromJsonFile("data/bible-reverse-refs.json")
            self._bibleRefs = self._fromJsonFile("data/bible-refs.json")
        except Exception as e:
            LOGGER_.error(f"{e}", exc_info=True)

        self.cache_ = LRUCache(10000)

    def _fromJsonFile(self, filePath):
        with open(filePath, 'r') as input_file:
            return json.load(input_file)
    
    def _normalizeBibleRef(self, ref):
        refParts = ref.split(' ')
        refBookName, refPlace = (" ".join(refParts[:-1]), refParts[-1])
        refRootName = self._bibleRootNameByAlias.get(refBookName)
        if not refRootName:
            return None
        
        return f"{refRootName} {refPlace}"
    
    def _shortenBibleRef(self, ref):
        refParts = ref.split(' ')
        refBookName, refPlace = (" ".join(refParts[:-1]), refParts[-1])
        refBookAliases = self._bibleAliases.get(refBookName, [])
        if not refBookAliases:
            return ref
        
        refRootName = refBookAliases[0]
        return f"{refRootName} {refPlace}"

    @timeit("Adding reverse Bible refs", __name__)
    def _addReverseBibleRefs(self, response):
        bibleRefs = response['bible-refs']
        for hit in response['hits']['hits']:
            for verse in hit['_source']['verses']:
                verse['reverse-references'] = []

                existingRefs = set()
                for _, refs in verse['references'].items():
                    for ref in refs:
                        normalizedRef = self._normalizeBibleRef(ref)
                        if not normalizedRef:
                            LOGGER_.warn(f"No normalized ref found for {ref}!")
                        else:
                            existingRefs.add(normalizedRef)

                revRefs = self._reverseBibleRefs.get(verse['name'], [])
                for ref in revRefs:
                    if ref not in existingRefs:
                        shortRef = self._shortenBibleRef(ref)
                        if not shortRef:
                            LOGGER_.warn(f"No short ref found for {ref}!")
                            continue
                        
                        normalizedRef = self._normalizeBibleRef(ref)
                        if not normalizedRef:
                            LOGGER_.warn(f"No normalized ref found for {ref}!")
                            continue

                        verse['reverse-references'].append(shortRef)
                        refVerse = self._bibleRefs.get(normalizedRef)
                        if not refVerse:
                            LOGGER_.warn(f"Verse {normalizedRef} not found in the Bible!")
                        else:
                            bibleRefs[shortRef] = refVerse

        response['bible-refs'] = bibleRefs

    def _addRefs(self, response):
        bibleRefs = dict()
        for hit in response['hits']['hits']:
            for verse in hit['_source']['verses']:
                for _, refs in verse['references'].items():
                    for ref in refs:
                        normalizedRef = self._normalizeBibleRef(ref)
                        if not normalizedRef:
                            LOGGER_.warn(f"No normalized ref found for {ref}!")

                        refVerse = self._bibleRefs.get(ref)
                        if not refVerse:
                            LOGGER_.warn(f"Verse {normalizedRef} not found in the Bible!")
                        else:
                            bibleRefs[ref] = refVerse
        
        response['bible-refs'] = bibleRefs

    @timeit("Adding od-refs", __name__)
    def _addOdRefs(self, response, includeReverseBibleRefs, includeRelatedOdRefs):
        odRefs = {}
        
        for hit in response['hits']['hits']:
            for verse in hit['_source']['verses']:
                if 'od-refs' not in verse:
                    verse['od-refs'] = []
                
                verseOdRefs = self._odRefsHandler.getRefsByKey(verse['name'])
                for odRef in verseOdRefs:
                    verse['od-refs'].append(odRef['refId'])
                    odRefs[odRef['refId']] = odRef

                if includeRelatedOdRefs:
                    if 'related-od-refs' not in verse:
                        verse['related-od-refs'] = defaultdict(list)

                    for _, refs in verse['references'].items():
                        for ref in refs:
                            normalizedRef = self._normalizeBibleRef(ref)
                            if not normalizedRef:
                                LOGGER_.warn(f"No normalized ref found for {ref}!")
                            else:
                                verseOdRefs = self._odRefsHandler.getRefsByKey(normalizedRef)
                                for odRef in verseOdRefs:
                                    verse['related-od-refs'][ref].append(odRef['refId'])
                                    odRefs[odRef['refId']] = odRef

                    if includeReverseBibleRefs and 'reverse-references' in verse:
                        for ref in verse['reverse-references']:
                            normalizedRef = self._normalizeBibleRef(ref)
                            if not normalizedRef:
                                LOGGER_.warn(f"No normalized ref found for {ref}!")
                            else:
                                verseOdRefs = self._odRefsHandler.getRefsByKey(normalizedRef)
                                for odRef in verseOdRefs:
                                    verse['related-od-refs'][ref].append(odRef['refId'])
                                    odRefs[odRef['refId']] = odRef

        response['od-refs'] = odRefs

    def getChapter(self, req):
        if 'book' not in req.params:
            raise Exception("Book parameter is missing!")
        
        if 'chapter' not in req.params:
            raise Exception("Chapter parameter is missing!")
        
        includeOdRefs = 'include-od-refs' in req.params
        includeRelatedOdRefs = 'include-related-od-refs' in req.params
        includeReverseBibleRefs = 'include-reverse-bible-refs' in req.params
        
        book = req.params['book']
        chapter = req.params['chapter']

        query_body = {
            'query': {
                'bool': {
                    'filter': [
                        { 
                            'term': {
                                'book': {
                                    'value': book,
                                    'case_insensitive': True
                                }
                            }
                        },
                        {
                            'term': {
                                'chapter': chapter
                            }
                        }
                    ]
                }
            },
            "sort": [{"_insert_idx": "asc"}],
        }

        resp = self._es.search(index='bible', body=query_body)
        data = resp.body

        self._addRefs(data)
        # Add reverse bible refs first, so that we can later add od refs
        # for the reverse bible refs, if includeRelatedOdRefs flag is set
        if includeReverseBibleRefs:
            self._addReverseBibleRefs(data)

        if includeOdRefs or includeRelatedOdRefs:
            self._addOdRefs(data, includeReverseBibleRefs, includeRelatedOdRefs)

        return data

    @req_handler("Handling Bible chapter GET", __name__)
    def on_get(self, req, resp):
        cache_key = req.url
        cached_response = self.cache_.get(cache_key)
        if cached_response:
            resp.status = falcon.HTTP_200
            resp.text = cached_response
        else:
            LOGGER_.info(f"Making Bible chapter query for {req.url}")
            response = self.getChapter(req)
            
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(response)
            self.cache_[cache_key] = resp.text