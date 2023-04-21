import logging
from datetime import datetime
from xml.dom import minidom

from dicttoxml import dicttoxml
from fastapi import APIRouter
from fastapi import Header, Query
from starlette.requests import Request
from starlette.responses import Response
from swarm_sdk.sdk import SwarmClient

from settings import MONGODB, SWARM_SERVER_URL

router = APIRouter(prefix="", tags=["objects"])


def get_owner_objects(bucket, owner, prefix=None, limit=1000, skip=0):
    query = {"Owner": owner, "Bucket": bucket}
    skip = skip or 0
    limit = 1000 if limit is None else limit
    if prefix:
        query["Key"] = {"$regex": f"^{prefix}"}
    yield from MONGODB.objects.find(query, {"_id": 0, "Content": 0}).skip(skip).limit(limit)


@router.put("/{bucket}/{key:path}")
async def create_object(
    bucket: str,
    key: str,
    request: Request,
    owner: str = Header(alias="x-amz-security-token"),
):
    logging.warning(f"Creating object {bucket}/{key}")
    content = await request.body()
    content_type = request.headers.get("Content-Type")
    swarm_client = SwarmClient(batch_id=owner, server_url=SWARM_SERVER_URL)
    swarm_upload_data = swarm_client.upload(content, content_type=content_type, name=key)
    swarm_upload_data["SwarmServerUrl"] = SWARM_SERVER_URL
    MONGODB.objects.insert_one(
        {
            "_id": {"Bucket": bucket, "Key": key},
            "Bucket": bucket,
            "Key": key,
            "Owner": owner,
            "CreationDate": datetime.now(),
            "SwarmData": swarm_upload_data,
        }
    )
    content = dicttoxml({}, attr_type=False, custom_root="CreateBucketConfiguration")
    return Response(content=content, media_type="application/xml")


@router.get("/{bucket}/{key:path}")
async def get_object(
    bucket: str,
    key: str,
    owner: str = Header(alias="x-amz-security-token"),
):
    data = MONGODB.objects.find_one(
        {
            "_id": {"Bucket": bucket, "Key": key},
            "Owner": owner,
        }
    )
    if not data:
        return Response(status_code=404)
    swarm_client = SwarmClient(server_url=data["SwarmData"]["SwarmServerUrl"])
    content = swarm_client.download(data["SwarmData"]["reference"])

    return Response(content=content, media_type="application/octet-stream")


@router.head("/{bucket}/{key:path}")
async def head_object(
    bucket: str,
    key: str,
    owner: str = Header(alias="x-amz-security-token"),
):
    data = MONGODB.objects.find_one(
        {
            "_id": {"Bucket": bucket, "Key": key},
            "Owner": owner,
        }
    )
    if data:
        return Response(status_code=200)
    return Response(status_code=404)


@router.delete("/{bucket}/{key:path}")
async def delete_object(
    bucket: str,
    key: str,
    owner: str = Header(alias="x-amz-security-token"),
):
    # TODO: delete from swarm?
    MONGODB.objects.delete_one(
        {
            "_id": {"Bucket": bucket, "Key": key},
            "Owner": owner,
        }
    )
    return Response(status_code=204)


@router.get("/{bucket}")
async def list_objects(
    bucket: str,
    request: Request,
    prefix: str = None,
    owner: str = Header(alias="x-amz-security-token"),
    max_keys: int = Query(alias="max-keys", default=1000),
    continuation_token: int = Query(alias="continuation-token", default=None),
):
    continuation_token = continuation_token or 0
    data = get_owner_objects(bucket, owner, prefix=prefix, limit=max_keys, skip=continuation_token)
    root = minidom.Document()
    xml = root.createElement("ListBucketResult")
    root.appendChild(xml)
    counter = 0
    for obj in data:
        xml.appendChild(root.createElement("Contents"))
        xml.lastChild.appendChild(root.createElement("Key")).appendChild(root.createTextNode(obj["Key"]))
        xml.lastChild.appendChild(root.createElement("LastModified")).appendChild(
            root.createTextNode(obj["CreationDate"].isoformat())
        )
        counter += 1
    if counter == max_keys:
        xml.appendChild(root.createElement("ContinuationToken")).appendChild(
            root.createTextNode(continuation_token + counter)
        )
    return Response(content=root.toprettyxml(), media_type="application/octet-stream")
