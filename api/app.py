import logging
from datetime import datetime

import uvicorn
from dicttoxml import dicttoxml
from fastapi import FastAPI, Query, Header
from starlette.requests import Request
from starlette.responses import Response

from settings import MONGODB

app = FastAPI()

api = FastAPI(title="DLS API")
app.mount("/api", api)


def get_owner_data(owner):
    return {
        "ID": owner,
        "DisplayName": owner
    }


def get_owner_buckets(owner):
    yield from MONGODB.buckets.find({"owner": owner})


# List all buckets
@api.get("/")
def list_buckets(owner: str = Header(alias="x-amz-security-token"), ):
    data = {
        "Owner": get_owner_data(owner),
        "Buckets": get_owner_buckets(owner)
    }
    content = dicttoxml(data, attr_type=False, custom_root="ListAllMyBucketsResult")
    return Response(content=content, media_type="application/xml")


@api.put("/{bucket}/{key}")
async def create_object(
        bucket: str,
        key: str,
        request: Request,
        owner: str = Header(alias="x-amz-security-token"),
):
    logging.warning(f"Creating object {bucket}/{key}")
    content = await request.body()
    MONGODB.objects.insert_one({
        "_id": {"bucket": bucket, "key": key},
        "bucket": bucket,
        "key": key,
        "owner": owner,
        "CreationDate": datetime.now(),
        "Content": content
    })
    content = dicttoxml({}, attr_type=False, custom_root="CreateBucketConfiguration")
    return Response(content=content, media_type="application/xml")


@api.get("/{bucket}/{key}")
async def get_object(
        bucket: str,
        key: str,
        owner: str = Header(alias="x-amz-security-token"),
):
    data = MONGODB.objects.find_one({
        "_id": {"bucket": bucket, "key": key},
        "owner": owner,
    })
    return Response(content=data["Content"], media_type="application/octet-stream")


@api.put("/{bucket}")
def create_bucket(
        bucket: str,
        owner: str = Header(alias="x-amz-security-token"),
):
    logging.warning(f"Creating bucket {bucket}")
    MONGODB.buckets.insert_one({
        "_id": bucket,
        "Name": bucket,
        "owner": owner,
        "CreationDate": datetime.now()
    })
    content = dicttoxml({}, attr_type=False, custom_root="CreateBucketConfiguration")
    return Response(content=content, media_type="application/xml")


@api.delete("/{bucket}")
def delete_bucket(
        bucket: str,
        owner: str = Header(alias="x-amz-security-token"),
):
    logging.warning(f"Deleting bucket {bucket}")
    MONGODB.buckets.delete_one({
        "_id": bucket,
        "owner": owner,
    })
    return Response(status_code=204)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
