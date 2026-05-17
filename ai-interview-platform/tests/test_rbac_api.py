import pytest

from tests.conftest import register_and_login


pytestmark = pytest.mark.integration


def test_anonymous_user_cannot_read_current_profile(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_regular_user_cannot_open_admin_panel(client):
    register_and_login(client, prefix="seed-admin")
    regular = register_and_login(client, prefix="regular")

    response = client.get("/api/v1/admin/users", headers=regular["headers"])

    assert response.status_code == 403


def test_admin_can_promote_user_and_manager_can_create_interview(client):
    admin = register_and_login(client, prefix="admin")
    target = register_and_login(client, prefix="manager-candidate")

    promote_response = client.patch(
        f"/api/v1/admin/users/{target['user']['id']}/role",
        json={"role": "manager"},
        headers=admin["headers"],
    )
    assert promote_response.status_code == 200
    assert promote_response.json()["role"] == "manager"

    manager_session = client.post(
        "/api/v1/auth/login",
        json={"email": target["user"]["email"], "password": "password123"},
    )
    manager_headers = {"Authorization": f"Bearer {manager_session.json()['access_token']}"}

    create_response = client.post(
        "/api/v1/interviews/",
        json={"title": "System Design", "description": "Manager-created interview", "status": "active"},
        headers=manager_headers,
    )

    assert create_response.status_code == 200
    assert create_response.json()["title"] == "System Design"


def test_user_without_permission_cannot_create_interview(client):
    register_and_login(client, prefix="seed-admin")
    regular = register_and_login(client, prefix="regular")

    response = client.post(
        "/api/v1/interviews/",
        json={"title": "Forbidden", "description": "No permission", "status": "active"},
        headers=regular["headers"],
    )

    assert response.status_code == 403
