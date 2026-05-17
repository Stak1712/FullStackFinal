import pytest

from tests.conftest import login_user, register_user


pytestmark = pytest.mark.integration


def test_register_login_and_me_flow(client, unique_email):
    created = register_user(client, email=unique_email, first_name="Turpal", last_name="Shabazov")
    assert created["email"] == unique_email
    assert created["role"] == "admin"  # first user in clean test DB is bootstrap admin

    session = login_user(client, email=unique_email)
    me = client.get("/api/v1/auth/me", headers=session["headers"])

    assert me.status_code == 200
    assert me.json()["email"] == unique_email
    assert "permissions" in me.json()


def test_duplicate_registration_returns_400(client, unique_email):
    register_user(client, email=unique_email)

    response = client.post(
        "/api/v1/auth/register",
        json={"first_name": "Test", "last_name": "User", "email": unique_email, "password": "password123"},
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_invalid_login_returns_401(client, unique_email):
    register_user(client, email=unique_email, password="password123")

    response = client.post("/api/v1/auth/login", json={"email": unique_email, "password": "wrong-password"})

    assert response.status_code == 401


def test_refresh_token_is_rotated_and_old_refresh_token_stops_working(client, unique_email):
    register_user(client, email=unique_email)
    session = login_user(client, email=unique_email)
    old_refresh = session["tokens"]["refresh_token"]

    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})

    assert refresh_response.status_code == 200
    new_refresh = refresh_response.json()["refresh_token"]
    assert new_refresh != old_refresh

    old_refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert old_refresh_response.status_code == 401


def test_logout_revokes_refresh_token(client, unique_email):
    register_user(client, email=unique_email)
    session = login_user(client, email=unique_email)
    refresh_token = session["tokens"]["refresh_token"]

    logout_response = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_response.status_code == 200

    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 401
