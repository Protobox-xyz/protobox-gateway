from uuid import uuid4

import boto3
import botocore.config


def test_client():
    session = boto3.session.Session()
    token = uuid4().hex
    client = session.client(
        's3',
        config=botocore.config.Config(
            s3={'addressing_style': 'path'}
        ),
        endpoint_url='http://localhost:8000/api/',
        aws_session_token=token,
        aws_secret_access_key=token,
        aws_access_key_id=token,
    )
    buckets = client.list_buckets()
    assert len(buckets["Buckets"]) == 0

    new_bucket = uuid4().hex
    client.create_bucket(Bucket=new_bucket)

    buckets = client.list_buckets()
    assert len(buckets["Buckets"]) == 1
