from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api_router import api_router
from app.core.config import settings
from app.dependencies import get_token_header
from app.internal import admin

openapi_tags = [
    {"name": "health", "description": "Service liveness and readiness checks."},
    {"name": "items", "description": "CRUD operations over items."},
    {"name": "admin", "description": "Internal administrative operations, requires `X-Token` header."},
]

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Agentick backend API.",
    openapi_tags=openapi_tags,
    contact={"name": "Agentick", "email": "anhdungvk01@gmail.com"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(
    admin.router,
    prefix=settings.api_v1_prefix + "/admin",
    dependencies=[Depends(get_token_header)],
    responses={400: {"description": "Invalid X-Token header"}},
)
