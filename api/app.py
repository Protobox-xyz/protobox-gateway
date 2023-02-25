from typing import Union

from fastapi import FastAPI

app = FastAPI()

api = FastAPI(title="DLS API")
app.mount("/api", api)


@api.get("/")
def read_root():
    return {"Hello": "World"}
