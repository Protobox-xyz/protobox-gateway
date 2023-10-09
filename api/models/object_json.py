from pydantic import BaseModel


class CreateBatchResponse(BaseModel):
    bucket: str
    owner: str
    _id: str
