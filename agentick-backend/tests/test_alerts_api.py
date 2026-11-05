import threading
import uuid

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import settings
from app.dependencies import get_plane
from app.main import app
from tests.fake_plane import INGEST, LIMITED, OK, FakePlane

W1 = str(uuid.uuid4())
ALERT = {
    "work_item_id": W1,
    "project_id": str(uuid.uuid4()),
    "issue_key": "IS-1",
    "comment_id": str(uuid.uuid4()),
    "rank": 2,
    "size": 15,
    "score": 0.83,
    "status": "in progress",
    "inactive_days": 5.9,
    "changes": ["04/03/2020 09:25 — Trạng thái: New → In Progress"],
}


@pytest.fixture
def plane(monkeypatch):
    monkeypatch.setattr(settings, "ingest_token", SecretStr("ingest-token"))
    fake = FakePlane()
    app.dependency_overrides[get_plane] = lambda: fake.client
    yield fake
    app.dependency_overrides.pop(get_plane, None)


@pytest.fixture
def seeded(client: TestClient, plane: FakePlane) -> TestClient:
    assert client.put("/api/v1/alerts", json=[ALERT], headers=INGEST).status_code == 200
    return client


def test_ingest_requires_the_service_token(client, plane):
    assert client.put("/api/v1/alerts", json=[ALERT]).status_code == 401
    assert (
        client.put(
            "/api/v1/alerts", json=[ALERT], headers={"Authorization": "Bearer nope"}
        ).status_code
        == 401
    )


def test_ingest_replaces_an_alert_of_the_same_work_item(seeded):
    seeded.put("/api/v1/alerts", json=[{**ALERT, "rank": 9}], headers=INGEST)
    assert seeded.get(f"/api/v1/alerts/{W1}", headers=OK).json()["rank"] == 9


def test_reading_needs_a_plane_session_that_may_see_the_item(seeded):
    assert seeded.get(f"/api/v1/alerts/{W1}").status_code == 401
    assert (
        seeded.get(f"/api/v1/alerts/{W1}", headers={"Cookie": "session-id=other"}).status_code
        == 401
    )
    assert seeded.get(f"/api/v1/alerts/{W1}", headers=LIMITED).status_code == 403
    assert seeded.get(f"/api/v1/alerts/{uuid.uuid4()}", headers=OK).status_code == 404


def test_a_work_item_id_that_is_not_a_uuid_is_a_422(seeded):
    assert seeded.get("/api/v1/alerts/not-a-uuid", headers=OK).status_code == 422


def test_pending_alert_is_readable(seeded):
    body = seeded.get(f"/api/v1/alerts/{W1}", headers=OK).json()
    assert body["state"] == "pending" and body["rank"] == 2 and body["changes"] == ALERT["changes"]


def test_approve_raises_priority_and_can_be_undone(seeded, plane):
    r = seeded.post(f"/api/v1/alerts/{W1}/decision", json={"decision": "approve"}, headers=OK)
    assert (
        r.status_code == 200
        and r.json()["state"] == "approved"
        and r.json()["decided_by"] == "dung"
    )
    assert plane.priority == "high"
    assert (
        seeded.post(
            f"/api/v1/alerts/{W1}/decision", json={"decision": "approve"}, headers=OK
        ).status_code
        == 409
    )
    r = seeded.post(f"/api/v1/alerts/{W1}/undo", headers=OK)
    assert r.json()["state"] == "pending" and plane.priority == "medium"
    assert seeded.post(f"/api/v1/alerts/{W1}/undo", headers=OK).status_code == 409


def test_dismiss_changes_nothing_in_plane_and_can_be_undone(seeded, plane):
    r = seeded.post(f"/api/v1/alerts/{W1}/decision", json={"decision": "reject"}, headers=OK)
    assert r.json()["state"] == "dismissed" and plane.patches() == []
    assert seeded.post(f"/api/v1/alerts/{W1}/undo", headers=OK).json()["state"] == "pending"


def test_a_failed_plane_update_leaves_the_alert_pending(client, monkeypatch):
    monkeypatch.setattr(settings, "ingest_token", SecretStr("ingest-token"))
    fake = FakePlane(patch_fails=True)
    app.dependency_overrides[get_plane] = lambda: fake.client
    try:
        client.put("/api/v1/alerts", json=[ALERT], headers=INGEST)
        assert (
            client.post(
                f"/api/v1/alerts/{W1}/decision", json={"decision": "approve"}, headers=OK
            ).status_code
            == 502
        )
        assert client.get(f"/api/v1/alerts/{W1}", headers=OK).json()["state"] == "pending"
    finally:
        app.dependency_overrides.pop(get_plane, None)


def test_two_approvals_at_once_keep_the_real_previous_priority(seeded, plane):
    """Without a row lock both callers pass the "still pending" check; the loser records High as the
    previous priority and Undo then restores the wrong value."""
    codes = []

    def approve():
        codes.append(
            seeded.post(
                f"/api/v1/alerts/{W1}/decision", json={"decision": "approve"}, headers=OK
            ).status_code
        )

    threads = [threading.Thread(target=approve) for _ in range(2)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert sorted(codes) == [200, 409]
    seeded.post(f"/api/v1/alerts/{W1}/undo", headers=OK)
    assert plane.priority == "medium"


def test_a_long_change_line_from_real_data_is_accepted(client, plane):
    """TAWOS Sprint changes list every sprint an issue went through; real lines reach 700 chars."""
    long_line = "14/09/2018 14:17 — Sprint: " + ", ".join(f"EV 18.{n}" for n in range(60))
    assert 600 < len(long_line) < 1000
    body = {**ALERT, "changes": [long_line]}
    assert client.put("/api/v1/alerts", json=[body], headers=INGEST).status_code == 200
