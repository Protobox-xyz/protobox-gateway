from datetime import datetime

from enum import Enum

from pydantic import BaseModel


class Action(str, Enum):
    DOWNLOAD = "Download"
    UPLOAD = "Upload"


class DataTransfer(BaseModel):
    action: Action
    application: str | None
    batch_id: str | None
    bucket_id: str | None
    content_length: str | None
    content_type: str | None
    created_at: datetime
    updated_at: datetime
    key: str | None
