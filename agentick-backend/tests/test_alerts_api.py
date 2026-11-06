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


def test_retiring_an_alert_needs_the_token_and_removes_a_pending_alert(seeded):
    assert seeded.delete(f"/api/v1/alerts/{W1}").status_code == 401
    assert seeded.delete(f"/api/v1/alerts/{W1}", headers=INGEST).status_code == 204
    assert seeded.get(f"/api/v1/alerts/{W1}", headers=OK).status_code == 404
    assert (
        seeded.delete(f"/api/v1/alerts/{W1}", headers=INGEST).status_code == 204
    )  # already gone: still fine


def test_an_alert_a_person_already_decided_on_is_not_retired(seeded):
    """The decision is the live evaluation data: the job may not delete it."""
    seeded.post(f"/api/v1/alerts/{W1}/decision", json={"decision": "reject"}, headers=OK)
    assert seeded.delete(f"/api/v1/alerts/{W1}", headers=INGEST).status_code == 409
    assert seeded.get(f"/api/v1/alerts/{W1}", headers=OK).json()["state"] == "dismissed"


NUDGE = {
    **ALERT,
    "action_type": "nudge_owner",
    "action_text": "Hi, ISP-1 has had no activity for 6 days. What is blocking it?",
}


def test_default_action_is_raising_the_priority(seeded):
    assert seeded.get(f"/api/v1/alerts/{W1}", headers=OK).json()["action_type"] == "raise_priority"


def test_approving_a_nudge_posts_the_draft_and_undo_removes_it(client, plane):
    client.put("/api/v1/alerts", json=[NUDGE], headers=INGEST)
    body = client.get(f"/api/v1/alerts/{W1}", headers=OK).json()
    assert body["action_type"] == "nudge_owner" and body["action_text"] == NUDGE["action_text"]
    plane.comments.clear()
    r = client.post(f"/api/v1/alerts/{W1}/decision", json={"decision": "approve"}, headers=OK)
    assert r.json()["state"] == "approved"
    assert any(NUDGE["action_text"] in c for c in plane.comments)
    assert plane.patches() == []  # a reminder never touches the priority
    r = client.post(f"/api/v1/alerts/{W1}/undo", headers=OK)
    assert r.json()["state"] == "pending" and plane.deleted == ["c1"]


def test_a_nudge_without_text_is_rejected(client, plane):
    bad = {**ALERT, "action_type": "nudge_owner"}
    assert client.put("/api/v1/alerts", json=[bad], headers=INGEST).status_code == 422


def test_advice_only_actions_write_nothing_but_the_audit_comment(client, plane):
    client.put("/api/v1/alerts", json=[{**ALERT, "action_type": "split"}], headers=INGEST)
    plane.comments.clear()
    r = client.post(f"/api/v1/alerts/{W1}/decision", json={"decision": "approve"}, headers=OK)
    assert r.json()["state"] == "approved" and plane.patches() == [] and len(plane.comments) == 1
    client.post(f"/api/v1/alerts/{W1}/undo", headers=OK)
    assert plane.deleted == []  # the audit comment stays as history


def test_the_mark_an_alert_was_raised_at_is_kept(client, plane):
    client.put("/api/v1/alerts", json=[{**ALERT, "mark": 0.25}], headers=INGEST)
    assert client.get(f"/api/v1/alerts/{W1}", headers=OK).json()["mark"] == 0.25
    assert (
        client.put("/api/v1/alerts", json=[{**ALERT, "mark": 1.5}], headers=INGEST).status_code
        == 422
    )
    client.put("/api/v1/alerts", json=[ALERT], headers=INGEST)
    assert (
        client.get(f"/api/v1/alerts/{W1}", headers=OK).json()["mark"] == 0.5
    )  # older jobs: the 50% mark


CYCLE, NEXT = str(uuid.uuid4()), str(uuid.uuid4())
MOVE = {**ALERT, "action_type": "move_next_cycle", "cycle_id": CYCLE, "target_cycle_id": NEXT}


def test_approving_a_move_puts_the_item_in_the_next_cycle_and_undo_brings_it_back(client, plane):
    client.put("/api/v1/alerts", json=[MOVE], headers=INGEST)
    r = client.post(f"/api/v1/alerts/{W1}/decision", json={"decision": "approve"}, headers=OK)
    assert r.json()["state"] == "approved"
    assert plane.moves == [(NEXT, {"issues": [W1]})]
    r = client.post(f"/api/v1/alerts/{W1}/undo", headers=OK)
    assert r.json()["state"] == "pending" and plane.moves[-1] == (CYCLE, {"issues": [W1]})


def test_a_move_needs_both_cycles(client, plane):
    for bad in ({**ALERT, "action_type": "move_next_cycle"}, {**MOVE, "cycle_id": None}):
        assert client.put("/api/v1/alerts", json=[bad], headers=INGEST).status_code == 422


def test_a_cycle_plane_refuses_leaves_the_alert_pending(client, monkeypatch):
    monkeypatch.setattr(settings, "ingest_token", SecretStr("ingest-token"))
    fake = FakePlane(cycle_fails=True)
    app.dependency_overrides[get_plane] = lambda: fake.client
    try:
        client.put("/api/v1/alerts", json=[MOVE], headers=INGEST)
        r = client.post(f"/api/v1/alerts/{W1}/decision", json={"decision": "approve"}, headers=OK)
        assert r.status_code == 502
        assert client.get(f"/api/v1/alerts/{W1}", headers=OK).json()["state"] == "pending"
    finally:
        app.dependency_overrides.pop(get_plane, None)


def test_the_diagnosed_cause_and_its_quote_are_kept_and_optional(client, plane):
    diagnosed = {
        **ALERT,
        "cause": "waiting_on_person",
        "evidence_quote": "waiting for review from QA",
    }
    client.put("/api/v1/alerts", json=[diagnosed], headers=INGEST)
    body = client.get(f"/api/v1/alerts/{W1}", headers=OK).json()
    assert (
        body["cause"] == "waiting_on_person"
        and body["evidence_quote"] == "waiting for review from QA"
    )
    client.put("/api/v1/alerts", json=[ALERT], headers=INGEST)
    assert client.get(f"/api/v1/alerts/{W1}", headers=OK).json()["cause"] is None
    bad = {**ALERT, "cause": "the stars"}
    assert client.put("/api/v1/alerts", json=[bad], headers=INGEST).status_code == 422


def _card(ref_key):
    ev = {
        "id": "o-1",
        "kind": "owner",
        "ts": "2020-01-05T00:00:00+00:00",
        "text": 'assignee moved OTHER-9 "secret title" In Progress -> Done',
        "ref_key": ref_key,
        "safe_text": "another issue, priority High",
    }
    mine = {
        "id": "c-1",
        "kind": "discussion",
        "ts": "2020-01-04T00:00:00+00:00",
        "text": "user#2: waiting",
    }
    return {
        "hypotheses": [
            {
                "cause": "pulled_away",
                "label": "the assignee is pulled to other work",
                "reason": 'fixed OTHER-9 "secret title"',
                "evidence": [ev, mine],
            }
        ],
        "dropped": 0,
        "unknown": False,
        "missing_info": "ask about secret title",
        "action": {"type": "nudge_owner", "text": "Hi, IS-1 looks stalled; any update?"},
    }


def test_evidence_about_an_issue_of_another_project_is_redacted_for_the_viewer(client, plane):
    client.put("/api/v1/alerts", json=[{**ALERT, "diagnosis": _card("OTHER-9")}], headers=INGEST)
    ev = client.get(f"/api/v1/alerts/{W1}", headers=OK).json()["diagnosis"]["hypotheses"][0][
        "evidence"
    ]
    assert ev[0]["text"] == "another issue, priority High" and ev[0]["ref_key"] is None
    assert ev[1]["text"] == "user#2: waiting"
    body = client.get(f"/api/v1/alerts/{W1}", headers=OK).json()["diagnosis"]
    assert "secret title" not in str(body)  # reason and missing_info are cut too
    client.put("/api/v1/alerts", json=[{**ALERT, "diagnosis": _card("IS-9")}], headers=INGEST)
    ev = client.get(f"/api/v1/alerts/{W1}", headers=OK).json()["diagnosis"]["hypotheses"][0][
        "evidence"
    ]
    assert "secret title" in ev[0]["text"]  # same project: shown in full


def test_a_diagnosis_is_optional_and_checked(client, plane):
    client.put("/api/v1/alerts", json=[ALERT], headers=INGEST)
    assert client.get(f"/api/v1/alerts/{W1}", headers=OK).json()["diagnosis"] is None
    bad = _card("IS-9")
    bad["hypotheses"][0]["evidence"] = []  # a hypothesis without evidence is not storable
    assert (
        client.put("/api/v1/alerts", json=[{**ALERT, "diagnosis": bad}], headers=INGEST).status_code
        == 422
    )


def test_notes_are_stored_and_only_known_kinds_are_accepted(client, plane):
    card = _card("IS-9") | {
        "notes": [{"kind": "sprint_overload", "text": "7 of 9 open", "event_ids": ["s-1"]}]
    }
    client.put("/api/v1/alerts", json=[{**ALERT, "diagnosis": card}], headers=INGEST)
    assert (
        client.get(f"/api/v1/alerts/{W1}", headers=OK).json()["diagnosis"]["notes"][0]["kind"]
        == "sprint_overload"
    )
    card["notes"][0]["kind"] = "lazy_team"
    assert (
        client.put(
            "/api/v1/alerts", json=[{**ALERT, "diagnosis": card}], headers=INGEST
        ).status_code
        == 422
    )


def _alert(project, key, score, **fields):
    return {
        **ALERT,
        "work_item_id": str(uuid.uuid4()),
        "project_id": project,
        "issue_key": key,
        "score": score,
    } | fields


def test_summary_counts_only_visible_projects_and_follows_decisions(client, plane):
    mine, theirs = str(uuid.uuid4()), str(uuid.uuid4())
    plane.projects = [mine]
    meta = {"model": "m1", "cost": 0.001, "error": None}
    kept = _card("IS-9") | {"meta": meta, "notes": [{"kind": "sprint_overload", "text": "x"}]}
    unk = {"hypotheses": [], "dropped": 2, "unknown": True, "meta": {**meta, "error": "bad json"}}
    a1 = _alert(mine, "IS-1", 0.9, diagnosis=kept)
    a2 = _alert(mine, "IS-2", 0.5, diagnosis=unk)
    a3 = _alert(theirs, "XX-1", 0.99, diagnosis=kept)  # another team: never counted
    client.put("/api/v1/alerts", json=[a1, a2, a3], headers=INGEST)
    client.post(
        f"/api/v1/alerts/{a1['work_item_id']}/decision", json={"decision": "approve"}, headers=OK
    )
    s = client.get("/api/v1/insights/summary", headers=OK).json()
    assert s["alerts"] == {"total": 2, "pending": 1, "approved": 1, "dismissed": 0}
    assert s["acceptance_rate"] == 1.0 and s["undone"] == 0
    assert {c["cause"]: c["n"] for c in s["causes"]} == {"pulled_away": 1, "unknown": 1}
    ai = s["ai"]
    assert (ai["diagnosed"], ai["unknown"], ai["hypotheses_kept"], ai["hypotheses_dropped"]) == (
        2,
        1,
        1,
        2,
    )
    assert (
        ai["cost_usd"] == 0.002
        and ai["calls_failed"] == 1
        and ai["notes"] == {"sprint_overload": 1}
    )
    assert ai["evidence_kinds"] == {"owner": 1, "discussion": 1}
    assert [p["project_id"] for p in s["projects"]] == [mine]
    assert s["decisions_by_day"][0]["approve"] == 1
    client.post(f"/api/v1/alerts/{a1['work_item_id']}/undo", headers=OK)
    s = client.get("/api/v1/insights/summary", headers=OK).json()
    assert s["alerts"]["pending"] == 2 and s["undone"] == 1 and s["acceptance_rate"] is None


def test_pending_lists_visible_alerts_by_score_with_redacted_reason(client, plane):
    mine = str(uuid.uuid4())
    plane.projects = [mine]
    lo, hi = _alert(mine, "IS-1", 0.4), _alert(mine, "IS-2", 0.8, diagnosis=_card("OTHER-9"))
    client.put("/api/v1/alerts", json=[lo, hi], headers=INGEST)
    out = client.get("/api/v1/insights/pending", headers=OK).json()
    assert [i["issue_key"] for i in out] == ["IS-2", "IS-1"]
    assert "secret title" not in str(out) and out[0]["cause_label"]
    assert [i["diagnosed"] for i in out] == [True, False]


def test_insights_need_a_plane_session(client, plane):
    assert client.get("/api/v1/insights/summary").status_code == 401
    assert client.get("/api/v1/insights/pending", headers=LIMITED).status_code == 403


def test_an_alert_without_a_diagnosis_is_not_counted_as_an_unknown_cause(client, plane):
    mine = str(uuid.uuid4())
    plane.projects = [mine]
    client.put("/api/v1/alerts", json=[_alert(mine, "IS-1", 0.4)], headers=INGEST)
    s = client.get("/api/v1/insights/summary", headers=OK).json()
    assert s["causes"] == [{"cause": "undiagnosed", "n": 1}] and s["ai"]["diagnosed"] == 0


def test_pending_can_be_limited_to_one_assignee(client, plane):
    mine, person = str(uuid.uuid4()), str(uuid.uuid4())
    plane.projects = [mine]
    a, b = _alert(mine, "IS-1", 0.4, assignee_ids=[person]), _alert(mine, "IS-2", 0.8)
    client.put("/api/v1/alerts", json=[a, b], headers=INGEST)
    out = client.get(f"/api/v1/insights/pending?assignee={person}", headers=OK).json()
    assert [i["issue_key"] for i in out] == ["IS-1"]
    assert len(client.get("/api/v1/insights/pending", headers=OK).json()) == 2


def test_summary_can_be_narrowed_to_chosen_projects_but_never_widened(client, plane):
    a, b, other = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    plane.projects = [a, b]
    client.put(
        "/api/v1/alerts",
        json=[_alert(a, "A-1", 0.5), _alert(b, "B-1", 0.5), _alert(other, "C-1", 0.5)],
        headers=INGEST,
    )

    def total(q):
        return client.get(f"/api/v1/insights/summary{q}", headers=OK).json()["alerts"]["total"]

    assert total("") == 2 and total(f"?project_ids={a}") == 1
    assert total(f"?project_ids={other}") == 0  # not visible: ignored, not added


def decide_on(client, decision):
    return client.post(
        f"/api/v1/alerts/{ALERT['work_item_id']}/decision",
        json={"decision": decision},
        headers=OK,
    ).json()


def test_a_second_run_counts_and_remembers_the_previous_score(seeded):
    first = seeded.get(f"/api/v1/alerts/{ALERT['work_item_id']}", headers=OK).json()
    assert first["seen_count"] == 1 and first["prev_score"] is None
    seeded.put("/api/v1/alerts", json=[{**ALERT, "score": 0.9}], headers=INGEST)
    again = seeded.get(f"/api/v1/alerts/{ALERT['work_item_id']}", headers=OK).json()
    assert again["seen_count"] == 2 and again["prev_score"] == ALERT["score"]
    assert again["score"] == 0.9


def test_a_dismissed_alert_comes_back_when_its_score_rises_a_lot(seeded):
    assert decide_on(seeded, "reject")["state"] == "dismissed"

    def state_after_run(score):
        seeded.put("/api/v1/alerts", json=[{**ALERT, "score": score}], headers=INGEST)
        return seeded.get(f"/api/v1/alerts/{ALERT['work_item_id']}", headers=OK).json()["state"]

    assert state_after_run(0.60) == "dismissed"  # better than before
    assert state_after_run(0.65) == "dismissed"  # +0.05: not enough to disturb anyone
    assert state_after_run(0.82) == "pending"  # +0.17 on the run before: back for a new decision


def test_an_approved_alert_stays_decided_however_much_worse_it_gets(seeded):
    assert decide_on(seeded, "approve")["state"] == "approved"
    seeded.put("/api/v1/alerts", json=[{**ALERT, "score": 0.99}], headers=INGEST)
    assert (
        seeded.get(f"/api/v1/alerts/{ALERT['work_item_id']}", headers=OK).json()["state"]
        == "approved"
    )
