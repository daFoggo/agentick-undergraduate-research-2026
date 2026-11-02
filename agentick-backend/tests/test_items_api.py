from fastapi.testclient import TestClient


def test_create_then_get_item(client: TestClient) -> None:
    created = client.post("/api/v1/items", json={"name": "Widget", "description": "A widget"})
    assert created.status_code == 201
    item_id = created.json()["id"]

    fetched = client.get(f"/api/v1/items/{item_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Widget"


def test_create_duplicate_name_returns_409(client: TestClient) -> None:
    client.post("/api/v1/items", json={"name": "Widget"})

    duplicate = client.post("/api/v1/items", json={"name": "Widget"})

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Resource already exists."


def test_create_item_with_nul_byte_in_name_returns_422_not_500(client: TestClient) -> None:
    response = client.post("/api/v1/items", json={"name": "bad\x00name"})

    assert response.status_code == 422


def test_get_item_with_out_of_range_id_returns_422_not_500(client: TestClient) -> None:
    response = client.get("/api/v1/items/99999999999999")

    assert response.status_code == 422


def test_list_items_with_out_of_range_page_returns_422_not_500(client: TestClient) -> None:
    response = client.get("/api/v1/items", params={"page": 99999999999999})

    assert response.status_code == 422


def test_get_missing_item_returns_404_with_detail(client: TestClient) -> None:
    missing = client.get("/api/v1/items/999999")

    assert missing.status_code == 404
    assert missing.json()["detail"] == "Item not found."


def test_update_and_delete_item(client: TestClient) -> None:
    created = client.post("/api/v1/items", json={"name": "Gadget"})
    item_id = created.json()["id"]

    updated = client.patch(f"/api/v1/items/{item_id}", json={"description": "Updated"})
    assert updated.status_code == 200
    assert updated.json()["description"] == "Updated"

    deleted = client.delete(f"/api/v1/items/{item_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/v1/items/{item_id}")
    assert missing.status_code == 404


def test_update_bumps_updated_at_past_created_at(client: TestClient) -> None:
    created = client.post("/api/v1/items", json={"name": "Thingamajig"})
    item_id = created.json()["id"]
    created_at = created.json()["created_at"]
    assert created.json()["updated_at"] == created_at

    updated = client.patch(f"/api/v1/items/{item_id}", json={"description": "Changed"})

    assert updated.json()["updated_at"] > created_at
