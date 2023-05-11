from pprint import pprint

import pytest
import xmltodict

from tests.conftest import HEADERS, TOKEN


@pytest.mark.skip()
def test_list_buckets_api_wo_token(api):
    response = api.get("/")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"][0]["loc"] == ["header", "x-amz-security-token"]
    # assert data["detail"][0]["msg"] == "field required"


def test_list_buckets_api(api):
    response = api.get("/", headers=HEADERS)
    assert response.is_success
    # convert xml to dict
    data = xmltodict.parse(response.content)
    assert data["ListAllMyBucketsResult"]["Owner"]["ID"] == TOKEN
    # assert data["ListAllMyBucketsResult"]["Buckets"] is None


def test_list_buckets_api_and_create_bucket(api):
    response = api.get("/", headers=HEADERS)
    assert response.is_success
    # convert xml to dict
    data = xmltodict.parse(response.content)
    assert data["ListAllMyBucketsResult"]["Owner"]["ID"] == TOKEN
    # assert data["ListAllMyBucketsResult"]["Buckets"] is None

    # create bucket
    bucket_name = "test"
    response = api.put(f"/{bucket_name}/", headers=HEADERS)
    assert response.is_success

    # list buckets
    response = api.get("/", headers=HEADERS)
    assert response.is_success
    # convert xml to dict
    data = xmltodict.parse(response.content)
    pprint(data)
    assert data["ListAllMyBucketsResult"]["Owner"]["ID"] == TOKEN
    # assert data["ListAllMyBucketsResult"]["Buckets"] is not None


@pytest.mark.skip()
def test_create_bucket_and_delete_bucket(api):
    # create bucket

    for i in range(3):
        response = api.put(f"/test_{i}/", headers=HEADERS)
        assert response.is_success

    # list buckets
    response = api.get("/", headers=HEADERS)
    assert response.is_success
    # convert xml to dict
    data = xmltodict.parse(response.content)
    assert data["ListAllMyBucketsResult"]["Owner"]["ID"] == TOKEN
    assert data["ListAllMyBucketsResult"]["Buckets"] is not None
    assert len(data["ListAllMyBucketsResult"]["Buckets"]["item"]) == 3

    response = api.delete(f"/test_0/", headers=HEADERS)
    assert response.is_success

    # list buckets
    response = api.get("/", headers=HEADERS)
    assert response.is_success
    # convert xml to dict
    data = xmltodict.parse(response.content)
    assert len(data["ListAllMyBucketsResult"]["Buckets"]["item"]) == 2
    assert not any([item["Name"] == "test_0" for item in data["ListAllMyBucketsResult"]["Buckets"]["item"]])
