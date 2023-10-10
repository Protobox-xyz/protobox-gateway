import logging

from fastapi import APIRouter, Depends
from service.batch_service import create_batch, get_owner_batches, get_batch_info
from settings import MONGODB
from models.batches_router import BatchResponse
from utils.auth import extract_signature

router = APIRouter(prefix="/api/json/batches", tags=["batches"])


@router.post("", response_model=BatchResponse)
async def handle_create_batch(owner: str = Depends(extract_signature)):
    logging.info(f"Creating batch")
    return await create_batch(owner)


@router.get("/{batch_id}", response_model=BatchResponse | None)
async def handle_get_batch(batch_id: str, owner: str = Depends(extract_signature)):
    logging.info(f"getting batch id {batch_id}, requesting {owner}")
    batch = MONGODB.batches.find_one({"batch_id": batch_id})
    batch["info"] = await get_batch_info(batch_id=batch_id)
    return batch


@router.get("", response_model=list[BatchResponse])
async def handle_get_list_batches(owner: str = Depends(extract_signature)):
    return await get_owner_batches(owner)
