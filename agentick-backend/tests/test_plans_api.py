import uuid

import pytest
from pydantic import SecretStr

from app.core.config import settings
from app.dependencies import get_plane
from app.main import app
from tests.fake_plane import INGEST, LIMITED, OK, FakePlane

PROJECT, CYCLE, NEXT = (str(uuid.uuid4()) for _ in range(3))


def item(key="ISP-1", why="risk", score=0.8):
    return {
        "work_item_id": str(uuid.uuid4()),
        "issue_key": key,
        "score": score,
        "why": why,
        "cause": "pulled_away",
        "reason": "The owner closed three other issues this week.",
    }


def plan(**over):
    body = {
        "project_id": PROJECT,
        "cycle_id": CYCLE,
        "next_cycle_id": NEXT,
        "sprint_name": "Sprint 12",
        "mark": 0.5,
        "open_count": 8,
        "history_sprints": 6,
        "unfinished_share": 0.5,
        "expected_unfinished": 4.0,
        "budget": 4,
        "items": [item("ISP-1"), item("ISP-2", "follows", 0.3)],
    }
    return body | over


@pytest.fixture(autouse=True)
def _ingest_token(monkeypatch):
    monkeypatch.setattr(settings, "ingest_token", SecretStr("ingest-token"))


def use_plane(projects):
    fake = FakePlane()
    fake.projects = projects
    app.dependency_overrides[get_plane] = lambda: fake.client
    return fake


def test_the_job_publishes_a_plan_and_a_viewer_of_the_project_reads_it(client):
    use_plane([PROJECT])
    assert client.put("/api/v1/plans", json=plan(), headers=INGEST).json() == {"stored": 2}
    got = client.get("/api/v1/plans", headers=OK).json()
    assert len(got) == 1 and got[0]["sprint_name"] == "Sprint 12" and got[0]["budget"] == 4
    assert [i["issue_key"] for i in got[0]["items"]] == ["ISP-1", "ISP-2"]  # in the order published
    assert got[0]["items"][1]["why"] == "follows"


def test_publishing_needs_the_ingest_token(client):
    use_plane([PROJECT])
    assert client.put("/api/v1/plans", json=plan()).status_code == 401
    assert (
        client.put("/api/v1/plans", json=plan(), headers={"Authorization": "Bearer x"}).status_code
        == 401
    )


def test_a_new_run_replaces_the_plan_of_the_same_cycle(client):
    use_plane([PROJECT])
    client.put("/api/v1/plans", json=plan(), headers=INGEST)
    client.put("/api/v1/plans", json=plan(items=[item("ISP-9")], budget=1), headers=INGEST)
    got = client.get("/api/v1/plans", headers=OK).json()
    assert len(got) == 1 and [i["issue_key"] for i in got[0]["items"]] == ["ISP-9"]


def test_only_plans_of_projects_the_viewer_sees_are_listed(client):
    use_plane([str(uuid.uuid4())])  # Plane lists some other project for this user
    client.put("/api/v1/plans", json=plan(), headers=INGEST)
    assert client.get("/api/v1/plans", headers=OK).json() == []


def test_listing_filters_by_cycle_and_needs_a_session(client):
    use_plane([PROJECT])
    client.put("/api/v1/plans", json=plan(), headers=INGEST)
    other = plan(cycle_id=str(uuid.uuid4()))
    client.put("/api/v1/plans", json=other, headers=INGEST)
    assert len(client.get(f"/api/v1/plans?cycle_id={CYCLE}", headers=OK).json()) == 1
    assert client.get("/api/v1/plans").status_code == 401
    assert client.get("/api/v1/plans", headers=LIMITED).status_code == 403


def test_a_plan_with_no_items_or_a_bad_share_is_refused(client):
    use_plane([PROJECT])
    assert client.put("/api/v1/plans", json=plan(items=[]), headers=INGEST).status_code == 422
    assert (
        client.put("/api/v1/plans", json=plan(unfinished_share=1.5), headers=INGEST).status_code
        == 422
    )


def published(client, plane_projects=None, n=3):
    """A plan with n items, read back as the signed-in user: (plan, fake Plane)."""
    fake = use_plane(plane_projects or [PROJECT])
    items = [item(f"ISP-{i}") for i in range(n)]
    client.put("/api/v1/plans", json=plan(items=items), headers=INGEST)
    return client.get("/api/v1/plans", headers=OK).json()[0], fake


def ids(p, state=None):
    return [i["work_item_id"] for i in p["items"] if state in (None, i["state"])]


def decide(client, p, decision, work_item_ids=None):
    body = {"decision": decision, "work_item_ids": work_item_ids}
    return client.post(f"/api/v1/plans/{p['id']}/decision", json=body, headers=OK)


def test_approving_the_plan_moves_every_item_to_the_next_cycle_and_notes_it(client):
    p, fake = published(client)
    got = decide(client, p, "approve").json()
    assert {i["state"] for i in got["items"]} == {"applied"} and got["errors"] == {}
    assert [cycle for cycle, _ in fake.moves] == [NEXT] * 3
    assert sorted(b["issues"][0] for _, b in fake.moves) == sorted(ids(p))
    assert len(fake.comments) == 3 and "approved the sprint plan" in fake.comments[0]


def test_only_the_chosen_items_move_and_a_dismissal_leaves_plane_alone(client):
    p, fake = published(client)
    one, two, _ = ids(p)
    got = decide(client, p, "approve", [one]).json()
    assert [i["state"] for i in got["items"]] == ["applied", "pending", "pending"]
    assert len(fake.moves) == 1
    got = decide(client, p, "reject", [two]).json()
    assert [i["state"] for i in got["items"]] == ["applied", "dismissed", "pending"]
    assert len(fake.moves) == 1  # a dismissal changes nothing in Plane


def test_an_item_plane_refuses_stays_pending_and_the_rest_still_move(client):
    p, fake = published(client)
    bad = ids(p)[1]
    fake.fail_items = {bad}
    got = decide(client, p, "approve").json()
    assert [i["state"] for i in got["items"]] == ["applied", "pending", "applied"]
    assert list(got["errors"]) == [bad]
    fake.fail_items = set()
    assert decide(client, p, "approve").json()["errors"] == {}  # the retry moves only that one
    assert len(fake.moves) == 3


def test_undo_puts_a_moved_item_back_in_its_cycle_and_reopens_a_dismissed_one(client):
    p, fake = published(client)
    one, two, _ = ids(p)
    decide(client, p, "approve", [one])
    decide(client, p, "reject", [two])
    got = client.post(f"/api/v1/plans/{p['id']}/undo", json={}, headers=OK).json()
    assert {i["state"] for i in got["items"]} == {"pending"}
    assert [cycle for cycle, _ in fake.moves] == [NEXT, CYCLE]  # moved, then back


def test_deciding_twice_or_naming_a_stranger_is_refused(client):
    p, _ = published(client)
    assert decide(client, p, "approve").status_code == 200
    assert decide(client, p, "approve").status_code == 409  # nothing is pending any more
    assert decide(client, p, "approve", [str(uuid.uuid4())]).status_code == 404


def test_a_user_who_cannot_see_the_project_cannot_decide(client):
    p, fake = published(client)
    fake.projects.clear()
    assert decide(client, p, "approve").status_code == 403
    assert fake.moves == []


def test_a_decided_plan_is_not_replaced_by_a_new_run(client):
    p, _ = published(client)
    decide(client, p, "reject", ids(p)[:1])
    assert client.put("/api/v1/plans", json=plan(), headers=INGEST).status_code == 409
    assert len(client.get("/api/v1/plans", headers=OK).json()[0]["items"]) == 3
