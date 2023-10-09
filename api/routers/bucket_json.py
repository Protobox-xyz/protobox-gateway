import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from starlette.responses import Response

from models.auth import Auth
from service.bucket_service import get_owner_data, get_owner_buckets
from settings import MONGODB
from utils.auth import extract_token

router = APIRouter(prefix="/api/json/buckets", tags=["buckets-json"])


# List all buckets
@router.get("/", response_model=dict)
def list_buckets(
    auth: Auth = Depends(extract_token),
):
    data = {"Owner": get_owner_data(auth.batch_id), "Buckets": get_owner_buckets(auth.batch_id)}
    return data


@router.put("/{bucket}")
def create_bucket(
    bucket: str,
    auth: Auth = Depends(extract_token),
):
    logging.warning(f"Creating bucket {bucket}")
    MONGODB.buckets.insert_one({"_id": bucket, "Name": bucket, "Owner": auth.batch_id, "CreationDate": datetime.now()})
    return Response(status_code=201)


@router.delete("/{bucket}")
def delete_bucket(
    bucket: str,
    auth: Auth = Depends(extract_token),
):
    logging.warning(f"Deleting bucket {bucket}")
    MONGODB.buckets.delete_one(
        {
            "_id": bucket,
            "Owner": auth.batch_id,
        }
    )
    return Response(status_code=204)
