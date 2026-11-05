import hmac


def valid_bearer(header: str | None, secret: str) -> bool:
    """Constant-time check of `Authorization: Bearer <secret>`. An empty secret never validates."""
    if not header or not secret or not header.startswith("Bearer "):
        return False
    return hmac.compare_digest(header.removeprefix("Bearer "), secret)
