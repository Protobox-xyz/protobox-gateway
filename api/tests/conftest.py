import pytest
from starlette.testclient import TestClient


@pytest.fixture
def api():
    from app import app

    with TestClient(app) as client:
        yield client
