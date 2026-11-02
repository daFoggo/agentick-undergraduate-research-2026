from fastapi.testclient import TestClient


def test_list_items_returns_paginated_result(client: TestClient) -> None:
    for name in ["Alpha", "Beta", "Gamma"]:
        client.post("/api/v1/items", json={"name": name})

    response = client.get("/api/v1/items", params={"page": 1, "page_size": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["total_count"] == 3
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert len(body["founds"]) == 2


def test_list_items_second_page(client: TestClient) -> None:
    for name in ["Alpha", "Beta", "Gamma"]:
        client.post("/api/v1/items", json={"name": name})

    response = client.get("/api/v1/items", params={"page": 2, "page_size": 2})

    assert response.status_code == 200
    body = response.json()
    assert len(body["founds"]) == 1
