import mongomock

import settings

settings.MONGODB = mongomock.MongoClient().protobox


import pytest
from starlette.testclient import TestClient


@pytest.fixture
def api():
    from app import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def clear_db_before_tests():
    # Code that will run before your test, for example:
    settings.MONGODB.objects.delete_many({})
    settings.MONGODB.buckets.delete_many({})
    yield
