from datetime import datetime

from pydantic import BaseModel, Field


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
    created_at: datetime = Field(None)
    updated_at: datetime = Field(None)


class BatchRequest(BaseModel):
    amount: int
    depth: int
    label: str


class BatchTaskRequest(BaseModel):
    task_id: str
    message: str
