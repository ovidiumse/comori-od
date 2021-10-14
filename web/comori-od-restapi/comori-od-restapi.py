#!/usr/bin/pypy3
import os
import falcon
from falcon_auth import FalconAuthMiddleware
from falcon_auth.backends import AuthBackend
import simplejson as json
import logging
import logging.config
import yaml
import pytz
from pyotp import TOTP, random_base32
from elasticsearch import Elasticsearch
from falcon.http_status import HTTPStatus
from dotenv import load_dotenv
from index_api import IndexHandler
from articles_api import ArticlesHandler, FieldAggregator, SearchTermSuggester, SimilarArticlesHandler
from content_api import ContentHandler
from titles_api import TitlesHandler, TitlesCompletionHandler
from favorites_api import FavoritesHandler
from markups_api import MarkupsHandler
from tags_api import TagsHandler
from recommended_api import RecommendedHandler
from readarticles_api import ReadArticlesHandler, BulkReadArticlesHandler
from api_utils import timeit

LOGGER_ = logging.getLogger(__name__)
ES = None
UTC = pytz.timezone('UTC')

class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
        if req.method == 'OPTIONS':
            raise HTTPStatus(falcon.HTTP_200, body='\n')


class TotpAuthBackend(AuthBackend):
    def __init__(self):
        key = os.environ['API_TOTP_KEY'] if os.environ.get('API_TOTP_KEY') else random_base32()
        LOGGER_.info("TOTP key: {}".format(key))
        self.totp = TOTP(key)
        self.auth_header_prefix = "Token"

    def _extract_credentials(self, req):
        auth = req.get_header('Authorization')
        return self.parse_auth_token_from_request(auth_header=auth)

    def authenticate(self, req, resp, resource):
        try:
            token = self._extract_credentials(req)
            if not token or not self.totp.verify(token, None, 120):
                raise falcon.HTTPUnauthorized(title='401 Unauthorized',
                                            description='Invalid Token',
                                            challenges=None)
        except Exception as ex:
            LOGGER_.error("Authorization handling failed! Error: {}".format(ex), exc_info=True)
            raise

    def get_auth_token(self, user_payload):
        """
        Extracts token from the `user_payload`
        """
        token = user_payload.get('token') or None
        if not token:
            raise ValueError('`user_payload` must provide api token')

        return '{auth_header_prefix} {token}'.format(
            auth_header_prefix=self.auth_header_prefix, token=token)


@timeit("Initializing service", __name__)
def load_app(cfg_filepath, dotenv_filePath = None):
    log_cfg = {}
    with open('logging_cfg.yaml', 'r') as log_conf_file:
        log_cfg = yaml.full_load(log_conf_file)

    logging.config.dictConfig(log_cfg)

    LOGGER_.info("Initializing svc...")

    cfg = {}
    with open(cfg_filepath, 'r') as cfg_file:
        cfg = yaml.full_load(cfg_file)

    if dotenv_filePath:
        load_dotenv(dotenv_filePath)

    global ES
    ES = Elasticsearch(hosts=[cfg['es']],
                       http_auth=(os.getenv("ELASTIC_USER", "elastic"),
                                  os.getenv("ELASTIC_PASSWORD", "")), 
                       timeout=30)

    LOGGER_.info("Cfg: {}".format(json.dumps(cfg, indent=2)))

    totpAuth = TotpAuthBackend()
    authMiddleware = FalconAuthMiddleware(totpAuth, None, ["OPTIONS", "GET"])
    app = falcon.API(middleware=[HandleCORS(), authMiddleware])

    index = IndexHandler(ES)
    articles = ArticlesHandler(ES)
    content = ContentHandler(ES)
    authors = FieldAggregator(ES, 'author', ['type', 'book'])
    types = FieldAggregator(ES, 'type', [])
    volumes = FieldAggregator(ES, 'volume', ['author'])
    books = FieldAggregator(ES, 'book', ['author', 'volume'])
    titles = TitlesHandler(ES)
    titlesCompletion = TitlesCompletionHandler(ES)
    searchTermSuggester = SearchTermSuggester(ES)
    similar = SimilarArticlesHandler(ES)
    favorites = FavoritesHandler()
    markups = MarkupsHandler()
    tags = TagsHandler()
    recommended = RecommendedHandler(ES)
    readArticles = ReadArticlesHandler()
    bulkReadArticles = BulkReadArticlesHandler()

    app.add_route('/{idx_name}', index)
    app.add_route('/{idx_name}/articles', articles)
    app.add_route('/{idx_name}/authors', authors)
    app.add_route('/{idx_name}/authors/{value}', authors)
    app.add_route('/{idx_name}/types', types)
    app.add_route('/{idx_name}/types/{value}', types)
    app.add_route('/{idx_name}/volumes', volumes)
    app.add_route('/{idx_name}/volumes/{value}', volumes)
    app.add_route('/{idx_name}/books', books)
    app.add_route('/{idx_name}/books/{value}', books)
    app.add_route('/{idx_name}/content', content)
    app.add_route('/{idx_name}/titles', titles)
    app.add_route('/{idx_name}/titles/completion', titlesCompletion)
    app.add_route('/{idx_name}/suggest/', searchTermSuggester)
    app.add_route('/{idx_name}/articles/similar', similar)
    app.add_route('/{idx_name}/favorites', favorites)
    app.add_route('/{idx_name}/favorites/{article_id}', favorites)
    app.add_route('/{idx_name}/markups', markups)
    app.add_route('/{idx_name}/markups/{markup_id}', markups)
    app.add_route('/{idx_name}/tags', tags)
    app.add_route('/{idx_name}/recommended', recommended)
    app.add_route('/{idx_name}/readarticles', readArticles)
    app.add_route('/{idx_name}/readarticles/{article_id}', readArticles)
    app.add_route('/{idx_name}/readarticles/bulk', bulkReadArticles)

    return app
