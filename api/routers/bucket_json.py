import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import Response

from models.bucket_json import CreateBucketRequest
from service.bucket_service import get_user_buckets, is_owner
from settings import MONGODB
from utils.auth import extract_signature

from uuid import uuid4

router = APIRouter(prefix="/api/json/buckets", tags=["buckets-json"])


# List all buckets
@router.get("", response_model=list)
async def list_buckets(
    owner_address: str = Depends(extract_signature),
):
    return await get_user_buckets(owner_address)


@router.post("")
async def create_bucket(
    response: CreateBucketRequest,
    owner_address: str = Depends(extract_signature),
):
    logging.warning(f"Creating bucket {owner_address}")

    if not await is_owner(owner_address, response.batch_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid batch owner")

    MONGODB.buckets.insert_one(
        {"_id": uuid4().hex, "Name": response.bucket, "Owner": response.batch_id, "CreationDate": datetime.now()}
    )
    return Response(status_code=201)


@router.delete("/{bucket_id}")
async def delete_bucket(
    bucket_id: str,
    owner_address: str = Depends(extract_signature),
):
    logging.info(f"Deleting bucket {bucket_id}")

    bucket = MONGODB.buckets.find_one({"_id": bucket_id})

    if not await is_owner(owner_address, bucket["Owner"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid batch owner")

    MONGODB.buckets.delete_one({"_id": bucket_id})
    return Response(status_code=204)
