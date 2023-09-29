import logging

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from routers.buckets import router as buckets_router
from routers.objects import router as objects_router
from routers.health import router as health_router
from routers.objects_json import router as objects_json_router

app = FastAPI(title="Protobox API", docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url="/api/redoc")

app.include_router(objects_json_router)
app.include_router(health_router)
app.include_router(buckets_router)
app.include_router(objects_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    logging.error(f"{request.headers}")
    content = {"message": "Validation Error", "errors": exc.errors()}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
