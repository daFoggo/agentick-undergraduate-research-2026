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
    def __init__(self, patch_fails: bool = False, cycle_fails: bool = False):
        self.calls, self.priority, self.patch_fails = [], "medium", patch_fails
        self.cycle_fails = cycle_fails
        self.moves: list[tuple[str, dict]] = []  # (cycle id, body) of every cycle-issues POST
        self.comments: list[str] = []  # html of every comment the bot posted
        self.deleted: list[str] = []  # ids of comments the bot deleted
        self.projects: list[str] = []  # project ids Plane lists for the signed-in user
        self.fail_items: set[str] = set()  # work items Plane refuses to move to a cycle

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
            if path == "/api/workspaces/ws/projects/":
                return (
                    httpx.Response(200, json=[{"id": p} for p in self.projects])
                    if cookie == "session-id=ok"
                    else httpx.Response(403)
                )
            if path.startswith("/api/workspaces/"):  # Plane's internal API: the access check
                return httpx.Response(200 if cookie == "session-id=ok" else 403, json={})
            if request.method == "POST" and "/cycles/" in path and path.endswith("/cycle-issues/"):
                body = json.loads(request.content)
                if self.cycle_fails or self.fail_items & set(body["issues"]):
                    return httpx.Response(400)  # Plane refuses a cycle that has finished
                self.moves.append((path.split("/cycles/")[1].split("/")[0], body))
                return httpx.Response(200, json={})
            if request.method == "POST" and path.endswith("/comments/"):
                self.comments.append(json.loads(request.content)["comment_html"])
                return httpx.Response(201, json={"id": f"c{len(self.comments)}"})
            if request.method == "DELETE" and "/comments/" in path:
                self.deleted.append(path.rstrip("/").rsplit("/", 1)[-1])
                return httpx.Response(204)
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
