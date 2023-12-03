from fastapi import APIRouter

from models.data_transfer import DataTransfer

from settings import MONGODB

router = APIRouter(prefix="/data-transfer", tags=["data-transfer"])


@router.get("", response_model=list[DataTransfer])
async def list_objects(
    skip: int = 0,
    limit: int = 100,
    sort: str = None,
    sort_direction: int = 1,
):
    data = list(MONGODB.data_transfer.find(skip=skip, limit=limit, sort=sort and [(sort, sort_direction)]))
    return data
