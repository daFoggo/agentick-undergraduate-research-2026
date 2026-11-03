from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import bcrypt
import jwt

from app.core.config import settings


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def _create_token(
    subject: str,
    token_type: Literal["access", "refresh"],
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": datetime.now(UTC) + expires_delta,
        **(extra_claims or {}),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(
    subject: str, *, email: str | None = None, role: str | None = None, name: str | None = None
) -> str:
    # Claims beyond sub/type/exp let clients (e.g. the frontend) read who the user
    # is locally, without a network round trip, the same way the other providers'
    # tokens do. The backend never trusts these for its own authorization — every
    # request still re-reads the user from the database (app/dependencies.py).
    extra_claims = {k: v for k, v in {"email": email, "role": role, "name": name}.items() if v}
    return _create_token(
        subject,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims,
    )


def create_refresh_token(subject: str) -> str:
    return _create_token(
        subject, "refresh", timedelta(days=settings.refresh_token_expire_days)
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
