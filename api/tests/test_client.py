import boto3
import botocore.config


def test_client():
    session = boto3.session.Session()
    client = session.client(
        's3',
        config=botocore.config.Config(
            s3={'addressing_style': 'path'}
        ),
        endpoint_url='http://localhost:8000/api/',
        aws_session_token="test",
        aws_secret_access_key="test",
        aws_access_key_id="test",
    )
    buckets = client.list_buckets()
    assert len(buckets["Buckets"]) == 0

    client.create_bucket(Bucket="test")

    buckets = client.list_buckets()
    assert len(buckets["Buckets"]) == 1
