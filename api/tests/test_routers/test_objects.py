import os

import asyncio
import pytest
from datetime import datetime

import xmltodict

from routers.objects import MONGODB
from tests.conftest import HEADERS, TOKEN


@pytest.mark.asyncio
def test_object_creation(api, mocker):
    swarm_client = mocker.patch("routers.objects.SwarmClient")
    swarm_client_instance = swarm_client.return_value
    f = asyncio.Future()
    f.set_result({"hash": "test"})
    swarm_client_instance.upload.return_value = f

    bucket = "test"
    key = "test.txt"
    headers = {**HEADERS, "Content-Type": "test/plain"}
    with open("tests/data/text_file.txt", "rb") as f:
        response = api.put(f"/{bucket}/{key}", data=f.read(), headers=headers)
    assert response.is_success
    # convert xml to dict
    # data = xmltodict.parse(response.content)
    obj = MONGODB.objects.find_one({"_id": {"Bucket": bucket, "Key": key}})
    assert obj is not None
    assert obj["Key"] == key
    assert obj["Owner"] == TOKEN


class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


def test_read_object(api, mocker):
    bucket = "test"
    key = "test.txt"
    ref = "9821"
    MONGODB.objects.insert_one(
        {
            "_id": {"Bucket": bucket, "Key": key},
            "Bucket": bucket,
            "Key": key,
            "Owner": TOKEN,
            "LastModified": datetime.now(),
            "SwarmData": {"reference": ref, "SwarmServerUrl": "http://localhost:8500"},
        }
    )

    swarm_client = mocker.patch("routers.objects.SwarmClient")
    swarm_client_instance = swarm_client.return_value
    with open("tests/data/text_file.txt", "rb") as f:
        swarm_client_instance.download.return_value = AsyncIterator(f.readlines())

    response = api.get(f"/{bucket}/{key}_0", headers=HEADERS)
    assert response.is_error

    response = api.get(f"/{bucket}/{key}", headers=HEADERS)
    assert response.is_success
    with open("tests/data/text_file.txt", "rb") as f:
        assert f.read() == response.content


def test_delete_object(api):
    bucket = "test"
    key = "test.txt"
    MONGODB.objects.insert_one(
        {
            "_id": {"Bucket": bucket, "Key": key},
            "Bucket": bucket,
            "Key": key,
            "Owner": TOKEN,
        }
    )

    response = api.delete(f"/{bucket}/{key}", headers=HEADERS)
    assert response.is_success
    assert MONGODB.objects.find_one({"_id": {"Bucket": bucket, "Key": key}, "Owner": TOKEN}) is None


def test_head_object(api):
    bucket = "test"
    key = "test.txt"
    MONGODB.objects.insert_one(
        {
            "_id": {"Bucket": bucket, "Key": key},
            "Bucket": bucket,
            "Key": key,
            "Owner": TOKEN,
        }
    )

    response = api.head(f"/{bucket}/{key}", headers=HEADERS)
    assert response.is_success

    response = api.head(f"/{bucket}/{key}_1", headers=HEADERS)
    assert response.is_error


def test_list_object(api):
    bucket = "test"
    for i in range(3):
        MONGODB.objects.insert_one(
            {
                "_id": {"Bucket": "test", "Key": f"{i}_test.txt"},
                "Bucket": "test",
                "Key": f"{i}_test.txt",
                "Owner": TOKEN,
                "CreationDate": datetime.now(),
            }
        )

    response = api.get(f"/{bucket}", headers=HEADERS)
    assert response.is_success
    data = xmltodict.parse(response.content)
    assert len(data["ListBucketResult"]["Contents"]) == 3

    response = api.get(f"/{bucket}", params={"prefix": "0_"}, headers=HEADERS)
    assert response.is_success
    data = xmltodict.parse(response.content)
    # data.ListBucketResult.Contents should be list, but it is parsed as dict,
    # so if type is dict it means there is only one item in list
    assert type(data["ListBucketResult"]["Contents"]) == dict
