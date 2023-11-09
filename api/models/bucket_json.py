from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class CreateBucketRequest(BaseModel):
    batch_id: str
    bucket: str


class SwarmData(BaseModel):
    reference: str
    SwarmServerUrl: str


class ObjectResponse(BaseModel):
    Bucket: str
    Key: str
    Owner: str
    Name: str
    CreationDate: Optional[datetime] = None
    SwarmData: Optional[SwarmData] = None
    Folder: bool
