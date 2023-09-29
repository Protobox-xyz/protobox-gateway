from fastapi import APIRouter, Depends
from fastapi import Query
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from swarm_sdk.sdk import SwarmClient

from service.bucket_service import create_bucket, get_owner_objects

from settings import MONGODB
from utils.auth import extract_token

router = APIRouter(prefix="/api/json", tags=["objects-json"])


@router.put("/{bucket}/{key:path}", status_code=201)
async def handle_create_object(
    bucket: str,
    key: str,
    request: Request,
    owner: str = Depends(extract_token),
):
    await create_bucket(bucket=bucket, key=key, request=request, owner=owner)


@router.get("/{bucket}/{key:path}")
async def get_object(
    bucket: str,
    key: str,
):
    data = MONGODB.objects.find_one({"_id": {"Bucket": bucket, "Key": key}})
    if not data:
        return Response(status_code=404)
    swarm_client = SwarmClient(server_url=data["SwarmData"]["SwarmServerUrl"])
    stream_content = swarm_client.download(data["SwarmData"]["reference"])
    return StreamingResponse(content=stream_content)


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
    owner: str = Depends(extract_token),
):
    MONGODB.objects.delete_one(
        {
            "_id": {"Bucket": bucket, "Key": key},
            "Owner": owner,
        }
    )
    return Response(status_code=204)


@router.get("/{bucket}", response_model=list[dict])
async def list_objects(
    bucket: str,
    prefix: str = None,
    owner: str = Depends(extract_token),
    max_keys: int = Query(alias="max-keys", default=1000),
    continuation_token: int = Query(alias="continuation-token", default=None),
):
    continuation_token = continuation_token or 0
    data = get_owner_objects(bucket, owner, prefix=prefix, limit=max_keys, skip=continuation_token)
    return data
