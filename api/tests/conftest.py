import uuid
from unittest.mock import patch

import mongomock
import pytest
from starlette.testclient import TestClient

import settings

settings.MONGODB = mongomock.MongoClient().protobox

TOKEN = "0x18a22dc629c07c02cbba3942ce3b977db76d23bc08e722eb6be42a5b6d6d7a8d02e271a6e88895a8662d5339d33efc8ca442299a01e5b5becc3145b5f01eea5c1c"
HEADERS = {"x-amz-security-token": TOKEN}


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


class MockedSwarmClient:
    def __init__(self, *args, **kwargs):
        ...

    def upload(self, *args, **kwargs):
        return {"reference": uuid.uuid4().hex}


@pytest.fixture(autouse=True)
def mock_swarm_client():
    with patch("routers.objects.SwarmClient", new=MockedSwarmClient):
        yield
