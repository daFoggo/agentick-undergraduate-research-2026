from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Liveness check",
    operation_id="getHealth",
)
async def get_health() -> dict[str, str]:
    return {"status": "ok"}
