import logging
from datetime import datetime

from dicttoxml import dicttoxml
from fastapi import APIRouter, Depends
from starlette.responses import Response

from service.bucket_service import get_owner_data, get_owner_buckets
from settings import MONGODB
from utils.auth import extract_token

router = APIRouter(prefix="", tags=["buckets"])


# List all buckets
@router.get("/")
def list_buckets(
    owner: str = Depends(extract_token),
):
    data = {"Owner": get_owner_data(owner), "Buckets": get_owner_buckets(owner)}
    content = dicttoxml(data, attr_type=False, custom_root="ListAllMyBucketsResult")
    return Response(content=content, media_type="application/xml")


@router.put("/{bucket}")
def create_bucket(
    bucket: str,
    owner: str = Depends(extract_token),
):
    logging.warning(f"Creating bucket {bucket}")
    MONGODB.buckets.insert_one({"_id": bucket, "Name": bucket, "Owner": owner, "CreationDate": datetime.now()})
    content = dicttoxml({}, attr_type=False, custom_root="CreateBucketConfiguration")
    return Response(content=content, media_type="application/xml")


@router.delete("/{bucket}")
def delete_bucket(
    bucket: str,
    owner: str = Depends(extract_token),
):
    logging.warning(f"Deleting bucket {bucket}")
    MONGODB.buckets.delete_one(
        {
            "_id": bucket,
            "Owner": owner,
        }
    )
    return Response(status_code=204)
