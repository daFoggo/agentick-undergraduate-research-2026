from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import RefreshRequest, Token, UserCreate, UserRead
from app.schemas.error import ErrorDetail

router = APIRouter(prefix="/auth", tags=["auth"])

DUPLICATE_RESPONSE = {
    409: {"model": ErrorDetail, "description": "A user with this email already exists."}
}
UNAUTHORIZED_RESPONSE = {
    401: {"model": ErrorDetail, "description": "Invalid credentials or token."}
}


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    operation_id="registerUser",
    responses=DUPLICATE_RESPONSE,
)
def register(user_in: UserCreate, db: Annotated[Session, Depends(get_db)]) -> User:
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        name=user_in.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/token",
    response_model=Token,
    summary="Log in and obtain tokens",
    operation_id="login",
    responses=UNAUTHORIZED_RESPONSE,
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user = db.query(User).filter(User.email == form_data.username).one_or_none()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedError(detail="Incorrect email or password.")

    subject = str(user.id)
    return Token(
        access_token=create_access_token(
            subject, email=user.email, role=user.role, name=user.name
        ),
        refresh_token=create_refresh_token(subject),
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Exchange a refresh token for a new access token",
    operation_id="refreshToken",
    responses=UNAUTHORIZED_RESPONSE,
)
def refresh(body: RefreshRequest, db: Annotated[Session, Depends(get_db)]) -> Token:
    try:
        payload = decode_token(body.refresh_token)
    except jwt.InvalidTokenError:
        raise UnauthorizedError() from None

    if payload.get("type") != "refresh":
        raise UnauthorizedError()

    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise UnauthorizedError()

    subject = str(user.id)
    return Token(
        access_token=create_access_token(
            subject, email=user.email, role=user.role, name=user.name
        ),
        refresh_token=create_refresh_token(subject),
    )


me_router = APIRouter(tags=["auth"])


@me_router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current authenticated user",
    operation_id="getCurrentUser",
    responses=UNAUTHORIZED_RESPONSE,
)
def read_current_user(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user
