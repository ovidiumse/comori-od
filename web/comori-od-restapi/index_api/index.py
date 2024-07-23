import falcon
import logging
import simplejson as json
from api_utils import req_handler

LOGGER_ = logging.getLogger(__name__)
ES = None

class IndexHandler(object):
    def __init__(self, es):
        global ES
        ES = es

    @req_handler("Deleting index", __name__)
    def on_delete(self, req, resp, idx_name):
        resp.content_type = 'application/json'

        LOGGER_.info(f"Deleting index {idx_name}...")

        ES.indices.delete(index=idx_name)
        resp.status = falcon.HTTP_200

    @req_handler("Getting index settings & mappings", __name__)
    def on_get(self, req, resp, idx_name):
        LOGGER_.info(f"Getting data for index {idx_name}...")

        mapping = ES.indices.get_mapping(index=idx_name)
        settings = ES.indices.get(index=idx_name)
        resp.status = falcon.HTTP_200
        resp.text = json.dumps({'settings': settings, 'mapping': mapping})

    @req_handler("Creating index", __name__)
    def on_post(self, req, resp, idx_name):
        data = json.loads(req.stream.read())

        LOGGER_.info(f"Creating index {idx_name} with data {json.dumps(data, indent=1)}")

        if ES.indices.exists(index=idx_name):
            ES.indices.delete(index=idx_name)

        ES.indices.create(index=idx_name, body=data['settings'])
        ES.indices.put_mapping(index=idx_name, body=data['mappings'])
        resp.status = falcon.HTTP_200