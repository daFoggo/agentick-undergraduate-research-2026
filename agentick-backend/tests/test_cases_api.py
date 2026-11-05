import uuid

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import settings
from app.dependencies import get_plane
from app.main import app
from tests.fake_plane import INGEST, LIMITED, OK, FakePlane

W1 = str(uuid.uuid4())
CASE = {
    "work_item_id": W1,
    "project_id": str(uuid.uuid4()),
    "sizes": {"small": 14, "medium": 4, "large": 2},
    "project_size": 900,
    "cases": [
        {
            "key": "IS-9",
            "title": "Fix login",
            "size": "small",
            "days": 3.0,
            "path": "/ript/browse/PCA-7/",
        },
        {
            "key": "IS-8",
            "title": "Retry upload",
            "size": "medium",
            "days": None,
            "path": "/ript/browse/PCA-8/",
        },
    ],
}


@pytest.fixture
def seeded(client: TestClient, monkeypatch) -> TestClient:
    monkeypatch.setattr(settings, "ingest_token", SecretStr("ingest-token"))
    app.dependency_overrides[get_plane] = lambda: FakePlane().client
    assert client.put("/api/v1/cases", json=[CASE], headers=INGEST).status_code == 200
    yield client
    app.dependency_overrides.pop(get_plane, None)


def test_ingest_requires_the_service_token(seeded):
    assert seeded.put("/api/v1/cases", json=[CASE]).status_code == 401


def test_reading_needs_a_session_that_plane_lets_see_the_item(seeded):
    assert seeded.get(f"/api/v1/cases/{W1}").status_code == 401
    assert seeded.get(f"/api/v1/cases/{W1}", headers=LIMITED).status_code == 403
    assert seeded.get(f"/api/v1/cases/{uuid.uuid4()}", headers=OK).status_code == 404


def test_size_days_and_links_are_returned(seeded):
    body = seeded.get(f"/api/v1/cases/{W1}", headers=OK).json()
    assert body["sizes"]["small"] == 14 and body["project_size"] == 900
    assert body["cases"][0]["days"] == 3.0 and body["cases"][1]["days"] is None


def test_case_link_must_stay_inside_plane(seeded):
    for bad in ("https://jira.example.org/browse/IS-9", "javascript:alert(1)", "//evil.example/x"):
        body = {**CASE, "cases": [{**CASE["cases"][0], "path": bad}]}
        assert seeded.put("/api/v1/cases", json=[body], headers=INGEST).status_code == 422


def test_a_record_with_no_cases_at_all_is_rejected(seeded):
    body = {**CASE, "sizes": {"small": 0, "medium": 0, "large": 0}}
    assert seeded.put("/api/v1/cases", json=[body], headers=INGEST).status_code == 422
