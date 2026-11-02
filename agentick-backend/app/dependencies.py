from typing import Annotated

from fastapi import Header, HTTPException, status

from app.core.config import settings


async def get_token_header(x_token: Annotated[str, Header()]) -> None:
    if x_token != settings.internal_admin_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="X-Token header invalid"
        )
