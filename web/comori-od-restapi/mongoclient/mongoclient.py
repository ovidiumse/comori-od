import os
import logging
import pymongo
from api_utils import timeit

LOGGER_ = logging.getLogger(__name__)

class MongoClient(object):
    dbsByIndexName = {}

    @timeit("Connecting to MongoDB", __name__)
    def getClient(self, idx_name):
        LOGGER_.info(f"Creating Mongo db connection for {idx_name}...")
        return pymongo.MongoClient('comori-od-mongo',
                            username=os.environ.get("MONGO_USERNAME"),
                            password=os.environ.get("MONGO_PASSWORD"))

    @timeit("Getting database by index", __name__)
    def getDb(self, idx_name):
        if idx_name not in self.dbsByIndexName:
            db = self.dbsByIndexName[idx_name] = self.getClient(idx_name)[f"comori_{idx_name}"]
            self.createIndexes(idx_name, db)
            return db

        return self.dbsByIndexName[idx_name]

    @timeit("Getting collection", __name__)
    def getCollection(self, idx_name, name):
        return self.getDb(idx_name)[name]

    @timeit("Creating indexes", __name__)
    def createIndexes(self, idx_name, db):
        LOGGER_.info(f"Creating indexes for {idx_name}...")

        db['favorites'].create_index([('uid', pymongo.ASCENDING)], unique=False)
        db['markups'].create_index([('uid', pymongo.ASCENDING)], unique=False)
        db['readArticles'].create_index([('uid', pymongo.ASCENDING)], unique=False)