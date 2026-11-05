from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DataError, IntegrityError

from app.api_router import api_router
from app.core.config import settings
from app.core.exceptions import DuplicatedError

openapi_tags = [
    {"name": "health", "description": "Service liveness and readiness checks."},
    {
        "name": "alerts",
        "description": "Sprint-risk alerts and the human decision on them.",
    },
    {
        "name": "cases",
        "description": "Finished cases similar to a work item, shown as a reference.",
    },
]

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Sprint-risk services next to Plane; this backend calls out to Plane.",
    openapi_tags=openapi_tags,
    contact={"name": "Agentick", "email": "anhdungvk01@gmail.com"},
    license_info={"name": "MIT"},
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(IntegrityError)
async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
    error = DuplicatedError()
    return JSONResponse(status_code=error.status_code, content={"detail": error.detail})


@app.exception_handler(DataError)
async def handle_data_error(request: Request, exc: DataError) -> JSONResponse:
    # Mirror FastAPI's own 422 shape (HTTPValidationError) so clients only
    # ever parse one structure for "request body failed validation".
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "loc": ["body"],
                    "msg": "Request data is not valid for this field.",
                    "type": "value_error",
                }
            ]
        },
    )


app.include_router(api_router, prefix=settings.api_v1_prefix)
