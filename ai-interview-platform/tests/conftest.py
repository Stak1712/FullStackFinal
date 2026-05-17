from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Environment must be configured before the application imports settings and DB engine.
os.environ.setdefault("ENV", "test")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("JWT_SECRET", "test_secret_for_lab5")
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/test.db")
os.environ.setdefault("STORAGE_PROVIDER", "local")
os.environ.setdefault("STORAGE_LOCAL_ROOT", "./data/test_object_storage")
os.environ.setdefault("EXTERNAL_API_CACHE_TTL_SECONDS", "0")
os.environ.setdefault("EXTERNAL_API_TIMEOUT_SECONDS", "0.1")

from app.core.config import get_settings  # noqa: E402

get_settings.cache_clear()

from app.api.v1.endpoints.resources import get_external_resource_service  # noqa: E402
from app.db.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Interview, InterviewSession, InterviewTurn, RefreshSession, ResumeAsset, User  # noqa: F401,E402


def reset_database() -> None:
    Path("data").mkdir(exist_ok=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    get_external_resource_service.cache_clear()
    storage_dir = Path("data/test_object_storage")
    if storage_dir.exists():
        shutil.rmtree(storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)


@pytest.fixture()
def db_session():
    reset_database()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    reset_database()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def unique_email() -> str:
    return f"test-{uuid4().hex[:10]}@example.com"


def register_user(client: TestClient, *, email: str | None = None, password: str = "password123", first_name: str = "Test", last_name: str = "User") -> dict[str, Any]:
    email = email or f"user-{uuid4().hex[:10]}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    payload["password"] = password
    return payload


def login_user(client: TestClient, *, email: str, password: str = "password123") -> dict[str, Any]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    tokens = response.json()
    return {
        "tokens": tokens,
        "headers": {"Authorization": f"Bearer {tokens['access_token']}"},
    }


def register_and_login(client: TestClient, *, prefix: str = "user", password: str = "password123") -> dict[str, Any]:
    user = register_user(client, email=f"{prefix}-{uuid4().hex[:8]}@example.com", password=password, first_name=prefix.title())
    session = login_user(client, email=user["email"], password=password)
    me = client.get("/api/v1/auth/me", headers=session["headers"])
    assert me.status_code == 200, me.text
    return {"user": me.json(), **session}
