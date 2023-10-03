import logging

from fastapi import APIRouter, Body
from service.bucket_service import create_batch
from settings import MONGODB
from models.batches_router import BatchResponse

router = APIRouter(prefix="/api/json/batches", tags=["batches"])


@router.put("", response_model=BatchResponse)
async def handle_create_batch(signature: str = Body(..., embed=True)):
    logging.warning(f"Creating batch")
    return await create_batch(signature)


@router.get("", response_model=BatchResponse | None)
async def handle_get_batch(batch_id: str):
    logging.warning(f"getting batch id {batch_id}")
    return MONGODB.batches.find_one({"batch_id": batch_id})
