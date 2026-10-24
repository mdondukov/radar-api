from fastapi import APIRouter

from app.api.v1.routers.admin import router as admin_router
from app.api.v1.routers.poll import router as poll_router

api_router = APIRouter()
api_router.include_router(poll_router)
api_router.include_router(admin_router)
