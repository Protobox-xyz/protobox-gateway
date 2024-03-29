from xml.dom import minidom
from dicttoxml import dicttoxml
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Query
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from swarm_sdk.sdk import SwarmClient

from service.bucket_service import create_bucket, get_owner_objects_s3, save_download_transfer

from settings import MONGODB
from utils.auth import extract_aws_token

from models.auth import Auth

router = APIRouter(prefix="", tags=["objects"])


@router.put("/{bucket}/{key:path}")
async def handle_create_object(
    bucket: str,
    key: str,
    request: Request,
    auth: Auth = Depends(extract_aws_token),
):
    bucket_info = MONGODB.buckets.find_one({"Name": bucket, "Owner": auth.batch_id})
    if not bucket_info:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid bucket owner")

    await create_bucket(
        bucket=bucket_info["_id"], key=key, request=request, owner=auth.batch_id, application=auth.application
    )

    content = dicttoxml({}, attr_type=False, custom_root="CreateBucketConfiguration")
    return Response(content=content, media_type="application/xml")


@router.get("/{bucket}/{key:path}")
async def get_object(bucket: str, key: str, auth: Auth = Depends(extract_aws_token)):
    bucket_info = MONGODB.buckets.find_one({"Name": bucket, "Owner": auth.batch_id})
    if not bucket_info:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid bucket owner")
    data = MONGODB.objects.find_one({"_id": {"Bucket": bucket_info["_id"], "Key": key}})
    if not data:
        return Response(status_code=404)

    await save_download_transfer(data, bucket_info["_id"], auth.application, key, auth.batch_id)

    swarm_client = SwarmClient(server_url=data["SwarmData"]["SwarmServerUrl"])
    stream_content = swarm_client.download(data["SwarmData"]["reference"])
    return StreamingResponse(content=stream_content, media_type=data["content_type"])


@router.head("/{bucket}/{key:path}")
async def head_object(
    bucket: str,
    key: str,
):
    data = MONGODB.objects.find_one({"_id": {"Bucket": bucket, "Key": key}})
    if not data:
        return Response(status_code=404)
    return Response(status_code=200)


@router.delete("/{bucket}/{key:path}")
async def delete_object(
    bucket: str,
    key: str,
    auth: Auth = Depends(extract_aws_token),
):
    MONGODB.objects.delete_one(
        {
            "_id": {"Bucket": bucket, "Key": key},
            "Owner": auth.batch_id,
        }
    )
    return Response(status_code=204)


@router.get("/{bucket}")
async def list_objects(
    bucket: str,
    prefix: str = "",
    auth: Auth = Depends(extract_aws_token),
    max_keys: int = Query(alias="max-keys", default=1000),
    continuation_token: int = Query(alias="continuation-token", default=None),
):
    continuation_token = continuation_token or 0
    data = await get_owner_objects_s3(bucket, auth.batch_id, prefix=prefix, limit=max_keys, skip=continuation_token)
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
        xml.lastChild.appendChild(root.createElement("Size")).appendChild(
            root.createTextNode(str(obj["content_length"]))
        )

    counter += 1
    if counter == max_keys:
        xml.appendChild(root.createElement("ContinuationToken")).appendChild(
            root.createTextNode(continuation_token + counter)
        )
    return Response(content=root.toprettyxml(), media_type="application/octet-stream")
