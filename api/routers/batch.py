import logging

from fastapi import APIRouter, Depends
from service.bucket_service import create_batch
from settings import MONGODB
from models.batches_router import BatchResponse
from utils.auth import extract_signature

router = APIRouter(prefix="/api/json/batches", tags=["batches"])


@router.put("", response_model=BatchResponse)
async def handle_create_batch(owner: str = Depends(extract_signature)):
    logging.warning(f"Creating batch")
    return await create_batch(owner)


@router.get("", response_model=BatchResponse | None)
async def handle_get_batch(batch_id: str):
    logging.warning(f"getting batch id {batch_id}")
    return MONGODB.batches.find_one({"batch_id": batch_id})
