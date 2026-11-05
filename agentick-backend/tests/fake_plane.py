"""Plane at the httpx boundary: the session cookie decides the user; the bot key always works."""

import json

import httpx

from app.integrations.plane import PlaneClient

OK = {"Cookie": "session-id=ok"}
LIMITED = {
    "Cookie": "session-id=limited"
}  # signed in, but Plane does not let this user see the work item
INGEST = {"Authorization": "Bearer ingest-token"}


class FakePlane:
    def __init__(self, patch_fails: bool = False):
        self.calls, self.priority, self.patch_fails = [], "medium", patch_fails

        def handler(request: httpx.Request) -> httpx.Response:
            path, cookie = request.url.path, request.headers.get("cookie")
            self.calls.append((request.method, path, request.content))
            if path == "/api/users/me/":
                signed_in = cookie in ("session-id=ok", "session-id=limited")
                return (
                    httpx.Response(200, json={"display_name": "dung"})
                    if signed_in
                    else httpx.Response(401)
                )
            if path.startswith("/api/workspaces/"):  # Plane's internal API: the access check
                return httpx.Response(200 if cookie == "session-id=ok" else 403, json={})
            if request.method == "PATCH":
                if self.patch_fails:
                    return httpx.Response(500)
                self.priority = json.loads(request.content)["priority"]
            return httpx.Response(200, json={"priority": self.priority})

        self.client = PlaneClient(
            "http://plane", "bot", "ws", transport=httpx.MockTransport(handler)
        )

    def patches(self) -> list[str]:
        return [json.loads(c[2])["priority"] for c in self.calls if c[0] == "PATCH"]
