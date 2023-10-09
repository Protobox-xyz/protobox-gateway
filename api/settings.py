import os

from pymongo import MongoClient

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
MONGODB_CLIENT = MongoClient(MONGODB_CONNECTION_STRING)
MONGODB = MONGODB_CLIENT.protobox

SWARM_SERVER_URL_BZZ = os.environ.get("SWARM_SERVER_URL_BZZ", "http://localhost:1633/")
SWARM_SERVER_URL_STAMP = os.environ.get("SWARM_SERVER_URL_STAMP", "http://localhost:1635/")

SING_IN_MESSAGE = "Sign in to Protobox"
