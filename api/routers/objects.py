import logging
from datetime import datetime
from xml.dom import minidom

from dicttoxml import dicttoxml
from fastapi import APIRouter
from fastapi import Header
from starlette.requests import Request
from starlette.responses import Response

from settings import MONGODB, SWARM_SERVER_URL, SWARM_BATCH_ID
from swarm_sdk.sdk import SwarmClient

router = APIRouter(prefix="", tags=["objects"])


def get_owner_objects(bucket, owner, prefix=None):
    query = {
        "Owner": owner,
        "Bucket": bucket,
    }
    if prefix:
        query["Key"] = {"$regex": f"^{prefix}"}
    yield from MONGODB.objects.find(query, {"_id": 0, "Content": 0})


@router.put("/{bucket}/{key}")
async def create_object(
    bucket: str,
    key: str,
    request: Request,
    owner: str = Header(alias="x-amz-security-token"),
):
    logging.warning(f"Creating object {bucket}/{key}")
    content = await request.body()
    content_type = request.headers.get("Content-Type")
    swarm_client = SwarmClient(SWARM_BATCH_ID, server_url=SWARM_SERVER_URL)
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


@router.get("/{bucket}/{key}")
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
    swarm_client = SwarmClient(server_url=data["SwarmData"]["SwarmServerUrl"])
    content = swarm_client.download(data["SwarmData"]["reference"])

    return Response(content=content, media_type="application/octet-stream")


@router.head("/{bucket}/{key}")
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


@router.delete("/{bucket}/{key}")
async def delete_object(
    bucket: str,
    key: str,
    owner: str = Header(alias="x-amz-security-token"),
):
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
    prefix: str = None,
    owner: str = Header(alias="x-amz-security-token"),
):
    data = get_owner_objects(bucket, owner, prefix=prefix)
    root = minidom.Document()
    xml = root.createElement("ListBucketResult")
    root.appendChild(xml)
    for obj in data:
        xml.appendChild(root.createElement("Contents"))
        xml.lastChild.appendChild(root.createElement("Key")).appendChild(root.createTextNode(obj["Key"]))
        xml.lastChild.appendChild(root.createElement("LastModified")).appendChild(
            root.createTextNode(obj["CreationDate"].isoformat())
        )
    return Response(content=root.toprettyxml(), media_type="application/octet-stream")
