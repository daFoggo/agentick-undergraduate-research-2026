from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Header, Request

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.security import valid_bearer
from app.integrations.plane import SESSION_COOKIE, PlaneClient


@lru_cache
def get_plane() -> PlaneClient:
    return PlaneClient(
        settings.plane_base_url,
        settings.plane_api_key.get_secret_value(),
        settings.plane_workspace_slug,
    )


def require_ingest_token(authorization: Annotated[str | None, Header()] = None) -> None:
    """The offline job that publishes alerts and cases proves itself with a shared bearer token."""
    if not valid_bearer(authorization, settings.ingest_token.get_secret_value()):
        raise UnauthorizedError()


def get_plane_session(request: Request) -> str:
    """A user is whoever Plane says owns this session cookie; no accounts are kept here."""
    session = request.cookies.get(SESSION_COOKIE)
    if not session:
        raise UnauthorizedError("Not signed in to Plane.")
    return session


PlaneDep = Annotated[PlaneClient, Depends(get_plane)]
PlaneSession = Annotated[str, Depends(get_plane_session)]
