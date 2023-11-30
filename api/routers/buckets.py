import logging
from datetime import datetime
from uuid import uuid4

from dicttoxml import dicttoxml
from fastapi import APIRouter, Depends
from starlette.responses import Response

from service.bucket_service import get_owner_data, get_owner_buckets
from settings import MONGODB
from utils.auth import extract_aws_token
from models.auth import Auth

router = APIRouter(prefix="", tags=["buckets"])


# List all buckets
@router.get("/")
def list_buckets(
    auth: Auth = Depends(extract_aws_token),
):
    data = {"Owner": get_owner_data(auth.batch_id), "Buckets": get_owner_buckets(auth.batch_id)}
    content = dicttoxml(data, attr_type=False, custom_root="ListAllMyBucketsResult")
    return Response(content=content, media_type="application/xml")


@router.put("/{bucket}")
def create_bucket(
    bucket: str,
    auth: Auth = Depends(extract_aws_token),
):
    logging.info(f"Creating bucket {bucket}")
    MONGODB.buckets.insert_one(
        {"_id": uuid4().hex, "Name": bucket, "Owner": auth.batch_id, "CreationDate": datetime.now()}
    )
    content = dicttoxml({}, attr_type=False, custom_root="CreateBucketConfiguration")
    return Response(content=content, media_type="application/xml")


@router.delete("/{bucket}")
def delete_bucket(
    bucket: str,
    auth: Auth = Depends(extract_aws_token),
):
    logging.warning(f"Deleting bucket {bucket}")
    MONGODB.buckets.delete_one(
        {
            "Name": bucket,
            "Owner": auth.batch_id,
        }
    )
    return Response(status_code=204)
