from pydantic import BaseModel


class TTLResponse(BaseModel):
    time_in_minutes: int
    amount: int


class PriceResponse(BaseModel):
    bzz_amount: int
    amount: int
