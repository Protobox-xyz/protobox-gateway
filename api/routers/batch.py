import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from starlette import status
from starlette.responses import Response


from service.batch_service import create_batch_task, get_owner_batches, get_batch_info
from settings import MONGODB
from models.batches_router import BatchResponse, BatchRequest, BatchTaskRequest
from utils.auth import extract_signature

router = APIRouter(prefix="/api/json/batches", tags=["batches"])


@router.post("", response_model=BatchTaskRequest, status_code=status.HTTP_202_ACCEPTED)
async def handle_create_batch(
    background_task: BackgroundTasks, request: BatchRequest, owner: str = Depends(extract_signature)
):
    logging.info(f"Creating batch")

    task_id = uuid4().hex
    background_task.add_task(create_batch_task, task_id, owner, request)
    MONGODB.tasks.insert_one({"_id": task_id, "finished": False})

    return BatchTaskRequest(task_id=task_id, message="starting processing..")


@router.get("/task/{task_id}", response_model=BatchResponse)
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
