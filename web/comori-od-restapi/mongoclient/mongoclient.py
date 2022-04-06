import os
import logging
import pymongo
from api_utils import timeit

LOGGER_ = logging.getLogger(__name__)

class MongoClient(object):
    dbsByIndexName = {}
    allowedDbs = ["od", "odbeta"]
    currentHost = os.getenv("VIRTUAL_HOST")

    @timeit("Connecting to MongoDB", __name__)
    def getClient(self, idx_name):
        allowed = False
        
        if not self.currentHost:
            allowed = idx_name in self.allowedDbs
        elif self.currentHost == "api.comori-od.ro":
            allowed = idx_name in self.allowedDbs
        elif self.currentHost == "testapi.comori-od.ro":
            allowed = idx_name == "odbeta"

        if not allowed:
            raise Exception("Database access not allowed!")

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
        db['authors'].create_index([('name', pymongo.ASCENDING)], unique=True)