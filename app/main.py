import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings

logger = logging.getLogger("radar_api")

app = FastAPI(title="radar-api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.error("%s: %s", exc.__class__.__name__, exc)
    return JSONResponse(status_code=500, content={"status": "ERROR", "data": str(exc)})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "OK"}
