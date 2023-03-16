import uvicorn
from fastapi import FastAPI

from routers.buckets import router as buckets_router
from routers.objects import router as objects_router
from routers.health import router as health_router

app = FastAPI()

api = FastAPI(title="Protobox API")
app.mount("/api", api)

api.include_router(buckets_router)
api.include_router(objects_router)
api.include_router(health_router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
