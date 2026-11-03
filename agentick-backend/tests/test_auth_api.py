import jwt as pyjwt
from fastapi.testclient import TestClient

from app.core.config import settings


def register(
    client: TestClient,
    email: str = "jane@example.com",
    password: str = "correct-password",
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "name": "Jane"},
    )
    assert response.status_code == 201, response.text


def login(
    client: TestClient,
    email: str = "jane@example.com",
    password: str = "correct-password",
) -> dict:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_register_creates_a_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "jane@example.com", "password": "correct-password", "name": "Jane"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "jane@example.com"
    assert body["role"] == "member"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_rejects_a_duplicate_email(client: TestClient) -> None:
    register(client)
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "jane@example.com", "password": "another-password", "name": "Jane 2"},
    )
    assert response.status_code == 409


def test_login_returns_access_and_refresh_tokens(client: TestClient) -> None:
    register(client)
    tokens = login(client)
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]


def test_login_rejects_a_wrong_password(client: TestClient) -> None:
    register(client)
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "jane@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_access_token_carries_profile_claims_for_clients_to_read_locally(
    client: TestClient,
) -> None:
    register(client)
    tokens = login(client)
    payload = pyjwt.decode(
        tokens["access_token"], settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
    assert payload["email"] == "jane@example.com"
    assert payload["role"] == "member"
    assert payload["name"] == "Jane"


def test_login_rejects_an_unknown_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "nobody@example.com", "password": "whatever"},
    )
    assert response.status_code == 401


def test_me_returns_the_current_user_for_a_valid_access_token(client: TestClient) -> None:
    register(client)
    tokens = login(client)
    response = client.get(
        "/api/v1/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "jane@example.com"


def test_me_rejects_a_missing_token(client: TestClient) -> None:
    response = client.get("/api/v1/me")
    assert response.status_code == 401


def test_me_rejects_an_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/api/v1/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_me_rejects_a_refresh_token_used_as_an_access_token(client: TestClient) -> None:
    register(client)
    tokens = login(client)
    response = client.get(
        "/api/v1/me", headers={"Authorization": f"Bearer {tokens['refresh_token']}"}
    )
    assert response.status_code == 401


def test_refresh_returns_a_new_access_token(client: TestClient) -> None:
    register(client)
    tokens = login(client)
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200
    new_access_token = response.json()["access_token"]
    me_response = client.get(
        "/api/v1/me", headers={"Authorization": f"Bearer {new_access_token}"}
    )
    assert me_response.status_code == 200


def test_refresh_rejects_an_access_token_used_as_a_refresh_token(client: TestClient) -> None:
    register(client)
    tokens = login(client)
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert response.status_code == 401
