from pydantic import BaseModel


class BatchRequest(BaseModel):
    batch_id: str
    owner: str
    _id: str
