from pydantic import BaseModel


class CreateBucketRequest(BaseModel):
    batch_id: str
    bucket: str
