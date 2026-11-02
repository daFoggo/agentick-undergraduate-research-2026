from fastapi import APIRouter

router = APIRouter()


@router.post("", summary="Run an internal admin action", operation_id="adminAction", tags=["admin"])
async def update_admin() -> dict[str, str]:
    return {"status": "ok"}
