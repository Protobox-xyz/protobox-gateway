import logging
from datetime import datetime
from xml.dom import minidom

import uvicorn
from dicttoxml import dicttoxml
from fastapi import FastAPI, Query, Header
from starlette.requests import Request
from starlette.responses import Response

from settings import MONGODB

app = FastAPI()

api = FastAPI(title="Protobox API")
app.mount("/api", api)


def get_owner_data(owner):
    return {
        "ID": owner,
        "DisplayName": owner
    }


def get_owner_buckets(owner):
    yield from MONGODB.buckets.find({"Owner": owner})


def get_owner_objects(bucket, owner, prefix=None):
    query = {
        "Owner": owner,
        "Bucket": bucket,
    }
    if prefix:
        query["Key"] = {"$regex": f"^{prefix}"}
    yield from MONGODB.objects.find(query,
                                    {"_id": 0, "Content": 0})


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
        "_id": {"Bucket": bucket, "Key": key},
        "Bucket": bucket,
        "Key": key,
        "Owner": owner,
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
        "_id": {"Bucket": bucket, "Key": key},
        "Owner": owner,
    })
    return Response(content=data["Content"], media_type="application/octet-stream")


@api.delete("/{bucket}/{key}")
async def delete_object(
        bucket: str,
        key: str,
        owner: str = Header(alias="x-amz-security-token"),
):
    MONGODB.objects.delete_one({
        "_id": {"Bucket": bucket, "Key": key},
        "Owner": owner,
    })
    return Response(status_code=204)


@api.get("/{bucket}")
async def list_objects(
        bucket: str,
        prefix: str = None,
        owner: str = Header(alias="x-amz-security-token"),
):
    data = get_owner_objects(bucket, owner, prefix=prefix)
    root = minidom.Document()
    xml = root.createElement('ListBucketResult')
    root.appendChild(xml)
    for obj in data:
        xml.appendChild(root.createElement('Contents'))
        xml.lastChild.appendChild(root.createElement('Key')).appendChild(root.createTextNode(obj["Key"]))
        xml.lastChild.appendChild(root.createElement('LastModified')).appendChild(root.createTextNode(obj["CreationDate"].isoformat()))
    return Response(content=root.toprettyxml(), media_type="application/octet-stream")


@api.put("/{bucket}")
def create_bucket(
        bucket: str,
        owner: str = Header(alias="x-amz-security-token"),
):
    logging.warning(f"Creating bucket {bucket}")
    MONGODB.buckets.insert_one({
        "_id": bucket,
        "Name": bucket,
        "Owner": owner,
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
        "Owner": owner,
    })
    return Response(status_code=204)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
