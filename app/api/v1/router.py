from fastapi import APIRouter

from app.api.v1.routers.poll import router as poll_router

api_router = APIRouter()
api_router.include_router(poll_router)
