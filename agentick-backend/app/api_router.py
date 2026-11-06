from fastapi import APIRouter

from app.routers import alerts, assistant, cases, health, insights, plans

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(alerts.router)
api_router.include_router(assistant.router)
api_router.include_router(cases.router)
api_router.include_router(insights.router)
api_router.include_router(plans.router)
