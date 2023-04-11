from uuid import uuid4

import boto3
import botocore.config
import pytest
from botocore.credentials import Credentials
from botocore.exceptions import ClientError

ENDPOINT_URL = "https://s3.protobox.xyz/api/"
BATCH_ID = "9f151ded49c44b529b98f42d7565002aa876b78298e4bccc39782c2ad709ccc7"


def get_client():
    session = boto3.session.Session()

    return session.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        config=botocore.config.Config(s3={"addressing_style": "path"}),
        aws_session_token=BATCH_ID,
        aws_secret_access_key=BATCH_ID,
        aws_access_key_id=BATCH_ID,
    )


def get_client_v2():
    session = boto3.session.Session()
    token = uuid4().hex

    creds = Credentials("", "", token)
    first_credential_provider = session._session.get_component("credential_provider").providers
    first_credential_provider.load = lambda: creds

    client = session.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        config=botocore.config.Config(s3={"addressing_style": "path"}),
    )
    return client


@pytest.mark.skip()
def test_objects():
    client = get_client()

    new_bucket = uuid4().hex
    client.create_bucket(Bucket=new_bucket)

    data = client.list_objects(Bucket=new_bucket)
    assert "Contents" not in data or len(data["Contents"]) == 0

    data = client.list_objects_v2(Bucket=new_bucket, ContinuationToken="12", MaxKeys=1)
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


@pytest.mark.skip()
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
