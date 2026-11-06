import httpx

from app.core.exceptions import (
    ExternalServiceError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)

SESSION_COOKIE = "session-id"


class PlaneClient:
    """Plane REST wrapper. Callers only ever see AppError subclasses, never httpx types.

    Two identities: the bot (API key, for writes) and the signed-in user (their Plane session
    cookie, only to find out who they are and whether Plane lets them see a work item).
    The bot key is never sent on user calls.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        workspace: str,
        transport: httpx.BaseTransport | None = None,
    ):
        self._workspace, self._key = workspace, api_key
        self._http = httpx.Client(base_url=base_url, timeout=15, transport=transport)

    def _send(
        self, method: str, path: str, headers: dict, json: dict | None = None
    ) -> httpx.Response:
        try:
            return self._http.request(method, path, headers=headers, json=json)
        except httpx.HTTPError as exc:
            raise ExternalServiceError("Plane is unreachable.") from exc

    def _bot(self, method: str, path: str, json: dict | None = None) -> dict:
        response = self._send(
            method, f"/api/v1/workspaces/{self._workspace}{path}", {"X-API-Key": self._key}, json
        )
        if response.status_code == 404:
            raise NotFoundError("Not found in Plane.")
        if response.is_error:
            raise ExternalServiceError(f"Plane returned {response.status_code}.")
        return response.json() if response.content else {}

    def _user(self, path: str, session: str) -> dict:
        response = self._send("GET", path, {"Cookie": f"{SESSION_COOKIE}={session}"})
        if response.status_code == 401:
            raise UnauthorizedError("Not signed in to Plane.")
        if response.status_code in (403, 404):
            raise ForbiddenError()
        if response.is_error:
            raise ExternalServiceError(f"Plane returned {response.status_code}.")
        return response.json()

    def user_name(self, session: str) -> str:
        me = self._user("/api/users/me/", session)
        return me.get("display_name") or me.get("email") or "a reviewer"

    def assert_can_view(self, session: str, project_id: str, work_item_id: str) -> None:
        self._user(
            f"/api/workspaces/{self._workspace}/projects/{project_id}/issues/{work_item_id}/",
            session,
        )

    def get_work_item(self, project_id: str, work_item_id: str) -> dict:
        return self._bot("GET", f"/projects/{project_id}/work-items/{work_item_id}/")

    def update_work_item(self, project_id: str, work_item_id: str, fields: dict) -> dict:
        return self._bot("PATCH", f"/projects/{project_id}/work-items/{work_item_id}/", fields)

    def add_comment(self, project_id: str, work_item_id: str, html: str) -> dict:
        return self._bot(
            "POST",
            f"/projects/{project_id}/work-items/{work_item_id}/comments/",
            {"comment_html": html},
        )

    def delete_comment(self, project_id: str, work_item_id: str, comment_id: str) -> None:
        self._bot(
            "DELETE", f"/projects/{project_id}/work-items/{work_item_id}/comments/{comment_id}/"
        )

    def move_to_cycle(self, project_id: str, work_item_id: str, cycle_id: str) -> None:
        """Adding to a cycle takes the item out of its old one; Plane refuses a finished cycle."""
        self._bot(
            "POST",
            f"/projects/{project_id}/cycles/{cycle_id}/cycle-issues/",
            {"issues": [work_item_id]},
        )
