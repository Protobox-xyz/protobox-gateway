from fastapi import APIRouter, Depends, HTTPException
from fastapi import Query
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from swarm_sdk.sdk import SwarmClient

from service.bucket_service import create_bucket, get_owner_objects, is_owner

from settings import MONGODB
from utils.auth import extract_signature

router = APIRouter(prefix="/api/json/buckets/{bucket_id}/objects", tags=["objects-json"])


@router.post("/{key:path}", status_code=201)
async def handle_create_object(
    bucket_id: str,
    key: str,
    batch_id: str,
    request: Request,
    owner_address=Depends(extract_signature),
):
    if not await is_owner(owner_address, batch_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid batch owner")

    await create_bucket(bucket=bucket_id, key=key, request=request, owner=batch_id)


@router.get("/{key:path}")
async def get_object(
    bucket_id: str,
    key: str,
    owner_address=Depends(extract_signature),
):
    data = MONGODB.objects.find_one({"_id": {"Bucket": bucket_id, "Key": key}})

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bucket Not Found")

    if not await is_owner(owner_address, data["Owner"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid batch owner")

    swarm_client = SwarmClient(server_url=data["SwarmData"]["SwarmServerUrl"])
    stream_content = swarm_client.download(data["SwarmData"]["reference"])
    return StreamingResponse(content=stream_content)


@router.head("/{key:path}")
async def head_object(
    bucket_id: str,
    key: str,
    owner_address=Depends(extract_signature),
):
    data = MONGODB.objects.find_one({"_id": {"Bucket": bucket_id, "Key": key}})

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bucket Not Found")

    if not await is_owner(owner_address, data["Owner"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid batch owner")

    return Response(status_code=200)


@router.delete("/{key:path}")
async def delete_object(
    bucket_id: str,
    key: str,
    owner_address=Depends(extract_signature),
):
    data = MONGODB.objects.find_one({"_id": {"Bucket": bucket_id, "Key": key}})

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bucket Not Found")

    if not await is_owner(owner_address, data["Owner"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid batch owner")

    MONGODB.objects.delete_one({"_id": {"Bucket": bucket_id, "Key": key}})
    return Response(status_code=204)


@router.get("", response_model=list[dict])
async def list_objects(
    bucket_id: str,
    prefix: str = None,
    limit: int = Query(default=1000),
    skip: int = Query(default=0),
    owner_address: str = Depends(extract_signature),
):
    data = await get_owner_objects(bucket_id, owner_address, prefix=prefix, limit=limit, skip=skip)
    return data
