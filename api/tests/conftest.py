import pytest
from starlette.testclient import TestClient


@pytest.fixture
def api():
    from api.app import app

    with TestClient(app) as client:
        yield client
