from pydantic import BaseModel


class CreateBucketResponse(BaseModel):
    batch_id: str
    bucket: str
