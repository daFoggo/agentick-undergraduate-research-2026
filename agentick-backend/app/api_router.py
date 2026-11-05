from fastapi import APIRouter

from app.routers import alerts, cases, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(alerts.router)
api_router.include_router(cases.router)
