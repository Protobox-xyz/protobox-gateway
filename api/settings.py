import os

from pymongo import MongoClient

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
MONGODB_CLIENT = MongoClient(MONGODB_CONNECTION_STRING)
MONGODB = MONGODB_CLIENT.protobox