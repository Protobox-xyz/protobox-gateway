from pydantic import BaseModel


class BatchResponse(BaseModel):
    batch_id: str
    owner: str
    _id: str
