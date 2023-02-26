from uuid import uuid4

import boto3
import botocore.config


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

    client.put_object(Bucket=new_bucket, Key="test", Body="test")

    data = client.get_object(Bucket=new_bucket, Key="test")
    assert data["Body"].read() == b"test"


def test_buckets():
    client = get_client()
    buckets = client.list_buckets()
    assert len(buckets["Buckets"]) == 0

    new_bucket = uuid4().hex
    client.create_bucket(Bucket=new_bucket)

    buckets = client.list_buckets()
    assert len(buckets["Buckets"]) == 1

    client.delete_bucket(Bucket=new_bucket)

    buckets = client.list_buckets()
    assert len(buckets["Buckets"]) == 0
