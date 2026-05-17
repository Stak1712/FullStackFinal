import pytest
from fastapi import HTTPException

from app.repositories.refresh_sessions import RefreshSessionRepository
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


pytestmark = pytest.mark.unit


def make_service(db_session) -> AuthService:
    return AuthService(users=UserRepository(db_session), refresh_sessions=RefreshSessionRepository(db_session))


def test_auth_service_register_assigns_admin_only_to_first_user(db_session):
    service = make_service(db_session)

    first = service.register(RegisterRequest(first_name="First", last_name="Admin", email="first@example.com", password="password123"))
    second = service.register(RegisterRequest(first_name="Second", last_name="User", email="second@example.com", password="password123"))

    assert first["role"] == "admin"
    assert second["role"] == "user"


def test_auth_service_rejects_duplicate_email(db_session):
    service = make_service(db_session)
    payload = RegisterRequest(first_name="Test", last_name="User", email="duplicate@example.com", password="password123")
    service.register(payload)

    with pytest.raises(ValueError):
        service.register(payload)


def test_auth_service_invalid_password_raises_401(db_session):
    service = make_service(db_session)
    service.register(RegisterRequest(first_name="Test", last_name="User", email="login@example.com", password="password123"))

    with pytest.raises(HTTPException) as exc:
        service.login(LoginRequest(email="login@example.com", password="bad-password"))

    assert exc.value.status_code == 401
