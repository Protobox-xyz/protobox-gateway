import logging
from datetime import datetime

import uvicorn
from dicttoxml import dicttoxml
from fastapi import FastAPI, Query
from starlette.requests import Request
from starlette.responses import Response

from settings import MONGODB

app = FastAPI()

api = FastAPI(title="DLS API")
app.mount("/api", api)


def get_owner(request: Request):
    return request.headers.get('x-amz-security-token')


def get_owner_data(request: Request):
    owner = get_owner(request)
    return {
        "ID": owner,
        "DisplayName": owner
    }


def get_owner_buckets(request: Request):
    owner = get_owner(request)
    yield from MONGODB.buckets.find({"owner": owner})


# List all buckets
@api.get("/")
def list_buckets(request: Request):
    data = {
        "Owner": get_owner_data(request),
        "Buckets": get_owner_buckets(request)
    }
    content = dicttoxml(data, attr_type=False, custom_root="ListAllMyBucketsResult")
    return Response(content=content, media_type="application/xml")


# List all objects in a bucket
@api.get("/{folder}")
def read_root(
        bucket: str = "app",  # TODO - get from request header
        delimiter: str | None = None,
        encoding_type: str | None = Query(alias="encoding-type"),
        marker: str | None = None,
        max_keys: str | None = Query(alias="max-keys"),
        prefix: str | None = None,
):
    return {}


@api.put("/{bucket}")
def create_bucket(
        bucket: str,
        request: Request,
):
    print(request.headers)
    logging.warning(f"Creating bucket {bucket}")
    MONGODB.buckets.insert_one({
        "_id": bucket,
        "Name": bucket,
        "owner": get_owner(request),
        "CreationDate": datetime.now()
    })
    content = dicttoxml({}, attr_type=False, custom_root="CreateBucketConfiguration")
    return Response(content=content, media_type="application/xml")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
