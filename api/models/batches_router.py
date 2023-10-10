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
