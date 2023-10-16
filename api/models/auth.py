from pydantic import BaseModel


class Auth(BaseModel):
    batch_id: str
    owner_address: str
