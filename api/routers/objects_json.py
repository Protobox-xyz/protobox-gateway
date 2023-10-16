from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from swarm_sdk.sdk import SwarmClient

from service.bucket_service import create_bucket, get_owner_objects, is_owner, get_object_data

from settings import MONGODB
from utils.auth import extract_signature

router = APIRouter(prefix="/api/json/buckets/{bucket_id}/objects", tags=["objects-json"])


@router.post("/{key:path}", status_code=201)
async def handle_create_object(
    bucket_id: str,
    key: str,
    request: Request,
    owner_address=Depends(extract_signature),
):
    bucket_info = MONGODB.buckets.find_one({"_id": bucket_id})

    if not bucket_info or not await is_owner(owner_address, bucket_info["Owner"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid bucket owner")

    await create_bucket(bucket=bucket_id, key=key, request=request, owner=bucket_info["Owner"])


@router.get("/{key:path}")
async def get_object(
    bucket_id: str,
    key: str,
    # owner_address=Depends(extract_signature),
):
    data = await get_object_data(bucket_id, key)

    swarm_client = SwarmClient(server_url=data["SwarmData"]["SwarmServerUrl"])
    stream_content = swarm_client.download(data["SwarmData"]["reference"])
    return StreamingResponse(content=stream_content)


@router.head("/{key:path}")
async def head_object(
    bucket_id: str,
    key: str,
    owner_address=Depends(extract_signature),
):
    await get_object_data(bucket_id, key, owner_address)

    return Response(status_code=200)


@router.delete("/{key:path}")
async def delete_object(
    bucket_id: str,
    key: str,
    owner_address=Depends(extract_signature),
):
    await get_object_data(bucket_id, key, owner_address)

    MONGODB.objects.delete_one({"_id": {"Bucket": bucket_id, "Key": key}})
    return Response(status_code=204)


@router.get("", response_model=list[dict])
async def list_objects(
    bucket_id: str,
    prefix: str = "",
    owner_address: str = Depends(extract_signature),
):
    data = await get_owner_objects(bucket_id, owner_address, prefix=prefix)
    return data
