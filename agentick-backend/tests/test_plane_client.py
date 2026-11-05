import httpx
import pytest

from app.core.exceptions import ExternalServiceError, NotFoundError
from app.integrations.plane import PlaneClient


def client(handler):
    return PlaneClient("http://plane", "key", "ws", transport=httpx.MockTransport(handler))


def test_get_work_item_sends_the_bot_key_and_returns_json():
    def handler(request):
        assert request.headers["X-API-Key"] == "key"
        assert request.url.path == "/api/v1/workspaces/ws/projects/p1/work-items/c1/"
        return httpx.Response(200, json={"id": "c1"})

    assert client(handler).get_work_item("p1", "c1") == {"id": "c1"}


def test_missing_work_item_is_not_found():
    with pytest.raises(NotFoundError):
        client(lambda r: httpx.Response(404)).get_work_item("p1", "c1")


def test_plane_failure_never_leaks_httpx_types():
    def boom(request):
        raise httpx.ConnectError("down")

    with pytest.raises(ExternalServiceError):
        client(boom).get_work_item("p1", "c1")
    with pytest.raises(ExternalServiceError):
        client(lambda r: httpx.Response(500)).get_work_item("p1", "c1")


def test_user_calls_send_the_session_cookie_and_never_the_bot_key():
    def handler(request):
        assert request.headers["cookie"] == "session-id=abc" and "x-api-key" not in request.headers
        return httpx.Response(200, json={"display_name": "dung"})

    assert client(handler).user_name("abc") == "dung"


def test_user_without_access_is_forbidden_and_signed_out_user_is_unauthorized():
    from app.core.exceptions import ForbiddenError, UnauthorizedError

    with pytest.raises(ForbiddenError):
        client(lambda r: httpx.Response(403)).assert_can_view("abc", "p1", "w1")
    with pytest.raises(UnauthorizedError):
        client(lambda r: httpx.Response(401)).user_name("abc")
