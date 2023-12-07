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
    info: BatchInfo = Field(None)
    created_at: datetime = Field(default=datetime.fromisoformat("2023-10-07T10:44:03.201000"))
    updated_at: datetime = Field(default=datetime.fromisoformat("2023-10-07T10:44:03.201000"))


class BatchRequest(BaseModel):
    amount: int
    depth: int
    label: str


class BatchExtendRequest(BaseModel):
    amount: int


class BatchTaskRequest(BaseModel):
    task_id: str
    message: str


class TaskResponse(BaseModel):
    batch_id: str
    owner: str
