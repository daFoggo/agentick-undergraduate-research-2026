from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core import security
from app.core.config import settings


def test_hash_password_does_not_return_the_plain_password() -> None:
    hashed = security.hash_password("correct-password")
    assert hashed != "correct-password"


def test_verify_password_accepts_the_matching_plain_password() -> None:
    hashed = security.hash_password("correct-password")
    assert security.verify_password("correct-password", hashed) is True


def test_verify_password_rejects_a_wrong_password() -> None:
    hashed = security.hash_password("correct-password")
    assert security.verify_password("wrong-password", hashed) is False


def test_access_token_decodes_to_the_subject_and_type() -> None:
    token = security.create_access_token(subject="42")
    payload = security.decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"


def test_refresh_token_decodes_to_the_subject_and_type() -> None:
    token = security.create_refresh_token(subject="42")
    payload = security.decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"


def test_decode_token_rejects_an_expired_token() -> None:
    expired_payload = {
        "sub": "42",
        "type": "access",
        "exp": datetime.now(UTC) - timedelta(minutes=1),
    }
    token = jwt.encode(expired_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    with pytest.raises(jwt.ExpiredSignatureError):
        security.decode_token(token)


def test_decode_token_rejects_a_token_signed_with_a_different_secret() -> None:
    token = jwt.encode(
        {"sub": "42", "type": "access"}, "a-different-secret", algorithm=settings.jwt_algorithm
    )
    with pytest.raises(jwt.InvalidTokenError):
        security.decode_token(token)
