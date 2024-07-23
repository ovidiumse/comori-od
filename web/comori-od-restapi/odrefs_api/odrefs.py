import simplejson as json
from elasticsearch import Elasticsearch, helpers
from collections import defaultdict
from api_utils import *

LOGGER_ = logging.getLogger(__name__)

class OdRefsHandler(object):    
    def __init__(self):
        try:
            self._odRefs = self._fromJsonFile("data/od-refs.json")
            self._bibleRootNameByAlias = self._fromJsonFile("data/bible-root-names.json")
            LOGGER_.info(f"Loaded {len(self._odRefs)} OD refs")
        except Exception as e:
            LOGGER_.error(f"{e}", exc_info=True)

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

    def getRefsByKey(self, key):
        normalizedKey = self._normalizeBibleRef(key)
        return self._odRefs.get(normalizedKey, [])

    @req_handler("Handling od-refs GET", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Making od-refs query for {req.url}")

        q = req.params['q']
        refs = self.getRefsByKey(q)

        resp.status = falcon.HTTP_200
        resp.text = json.dumps(refs)