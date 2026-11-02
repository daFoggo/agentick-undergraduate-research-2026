from fastapi import APIRouter

router = APIRouter()


@router.post("", operation_id="adminAction", tags=["admin"])
async def update_admin() -> dict[str, str]:
    return {"status": "ok"}
