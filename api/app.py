import uvicorn
from fastapi import FastAPI

from routers.buckets import router as buckets_router
from routers.objects import router as objects_router
from routers.health import router as health_router

app = FastAPI(title="Protobox API", docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url="/api/redoc")

app.include_router(buckets_router)
app.include_router(objects_router)
app.include_router(health_router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
