import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from starlette import status
from starlette.responses import Response

from models.pricing import TTLResponse, PriceResponse
from service.batch_service import create_batch_task, get_owner_batches, get_batch_info, extend_batch_task
from settings import MONGODB, POSTAGE_PRICE, BLOCK_TIME_SECONDS
from models.batches_router import BatchResponse, BatchRequest, BatchTaskRequest, BatchExtendRequest, TaskResponse
from utils.auth import extract_signature

router = APIRouter(prefix="/api/json/batches", tags=["batches"])


@router.get("/price", response_model=PriceResponse)
async def handle_get_ttl(time_in_minutes: int, depth: int = 20):
    amount = POSTAGE_PRICE / BLOCK_TIME_SECONDS * time_in_minutes * 60
    bzz_amount = amount * 2**depth
    return {"bzz_amount": bzz_amount, "amount": amount}


@router.get("/ttl", response_model=TTLResponse)
async def handle_get_ttl(bzz_amount: int, depth: int = 20):
    amount = bzz_amount / 2**depth
    time_in_minutes = amount * BLOCK_TIME_SECONDS / (POSTAGE_PRICE * 60)
    return {"time_in_minutes": time_in_minutes, "amount": amount}


@router.post("", response_model=BatchTaskRequest, status_code=status.HTTP_202_ACCEPTED)
async def handle_create_batch(
    background_task: BackgroundTasks, request: BatchRequest, owner: str = Depends(extract_signature)
):
    logging.info(f"Creating batch")

    task_id = uuid4().hex
    background_task.add_task(create_batch_task, task_id, owner, request)
    MONGODB.tasks.insert_one({"_id": task_id, "finished": False})

    return BatchTaskRequest(task_id=task_id, message="starting processing..")


@router.post("/{batch_id}/_extend", response_model=BatchTaskRequest, status_code=status.HTTP_202_ACCEPTED)
async def handle_extend_batch(
    background_task: BackgroundTasks,
    request: BatchExtendRequest,
    batch_id: str,
    owner: str = Depends(extract_signature),
):
    logging.info(f"Extending batch batch")

    task_id = uuid4().hex
    background_task.add_task(extend_batch_task, task_id, batch_id, owner, request)
    MONGODB.tasks.insert_one({"_id": task_id, "finished": False})

    return BatchTaskRequest(task_id=task_id, message="starting processing..")


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def handle_get_task(task_id: str, _: str = Depends(extract_signature)):
    logging.info(f"getting status")

    task_info = MONGODB.tasks.find_one({"_id": task_id})

    if not task_info["finished"]:
        return Response(status_code=status.HTTP_425_TOO_EARLY)

    if task_info["status_code"] >= 400:
        return Response(status_code=task_info["status_code"])

    return task_info["response"]


@router.get("/{batch_id}", response_model=BatchResponse | None)
async def handle_get_batch(batch_id: str, owner: str = Depends(extract_signature)):
    logging.info(f"getting batch id {batch_id}, requesting {owner}")
    batch = MONGODB.batches.find_one({"batch_id": batch_id})

    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="batch nod found")

    batch["info"] = await get_batch_info(batch_id=batch_id)
    return batch


@router.get("", response_model=list[BatchResponse])
async def handle_get_list_batches(owner: str = Depends(extract_signature)):
    return await get_owner_batches(owner)
