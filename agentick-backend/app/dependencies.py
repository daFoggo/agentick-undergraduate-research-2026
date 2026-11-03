from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/token")


async def get_token_header(x_token: Annotated[str, Header()]) -> None:
    if x_token != settings.internal_admin_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="X-Token header invalid"
        )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError:
        raise UnauthorizedError() from None

    if payload.get("type") != "access":
        raise UnauthorizedError()

    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise UnauthorizedError()
    return user


def require_role(role: str):
    def _check_role(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role != role:
            raise ForbiddenError()
        return user

    return _check_role
