from datetime import datetime

from enum import Enum

from pydantic import BaseModel


class Action(str, Enum):
    DOWNLOAD = "Download"
    UPLOAD = "Upload"


class DataTransfer(BaseModel):
    action: Action
    application: str
    batch_id: str
    bucket_id: str
    content_length: str
    content_type: str
    created_at: datetime
    updated_at: datetime
    key: str
