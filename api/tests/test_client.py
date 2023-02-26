from uuid import uuid4

import boto3
import botocore.config
import pytest
from botocore.exceptions import ClientError


def get_client():
    session = boto3.session.Session()
    token = uuid4().hex
    return session.client(
        's3',
        config=botocore.config.Config(
            s3={'addressing_style': 'path'}
        ),
        endpoint_url='http://localhost:8000/api/',
        aws_session_token=token,
        aws_secret_access_key=token,
        aws_access_key_id=token,
    )


def test_objects():
    client = get_client()

    new_bucket = uuid4().hex
    client.create_bucket(Bucket=new_bucket)

    data = client.list_objects(Bucket=new_bucket)
    assert "Contents" not in data or len(data["Contents"]) == 0

    client.put_object(Bucket=new_bucket, Key="test", Body="test")

    data = client.head_object(Bucket=new_bucket, Key="test")
    assert data["ResponseMetadata"]["HTTPStatusCode"] == 200

    data = client.get_object(Bucket=new_bucket, Key="test")
    assert data["Body"].read() == b"test"

    data = client.list_objects(Bucket=new_bucket)
    assert len(data["Contents"]) == 1
    assert data["Contents"][0]["Key"] == "test"

    client.delete_object(Bucket=new_bucket, Key="test")

    with pytest.raises(ClientError):
        client.head_object(Bucket=new_bucket, Key="test")

    data = client.list_objects(Bucket=new_bucket)
    assert "Contents" not in data or len(data["Contents"]) == 0


def test_buckets():
    client = get_client()
    buckets = client.list_buckets()
    assert len(buckets["Buckets"]) == 0

    new_bucket = uuid4().hex
    client.create_bucket(Bucket=new_bucket)

    buckets = client.list_buckets()
    assert len(buckets["Buckets"]) == 1
    assert buckets["Buckets"][0]["Name"] == new_bucket

    client.delete_bucket(Bucket=new_bucket)

    buckets = client.list_buckets()
    assert len(buckets["Buckets"]) == 0
