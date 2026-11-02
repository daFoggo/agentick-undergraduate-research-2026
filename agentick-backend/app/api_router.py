from fastapi import APIRouter

from app.routers import health, items

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(items.router)
