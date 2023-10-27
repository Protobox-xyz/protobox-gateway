from typing import Optional

from pydantic import BaseModel


class BatchInfo(BaseModel):
    utilization: int
    usable: bool
    label: str
    depth: int
    amount: int
    bucketDepth: int
    blockNumber: int
    immutableFlag: bool
    exists: bool
    batchTTL: int
    expired: bool


class BatchResponse(BaseModel):
    batch_id: str
    owner: str
    _id: str
    info: BatchInfo = {}


class BatchRequest(BaseModel):
    amount: int
    depth: int
    label: str


class BatchTaskRequest(BaseModel):
    task_id: str
    message: str


class BatchTaskResponse(BaseModel):
    _id: str
    finished: bool
    status_code: Optional[int]
    response: Optional[BatchResponse] | dict
