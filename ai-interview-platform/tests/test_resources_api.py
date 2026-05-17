import pytest

from app.schemas.external_resource import ExternalResource


pytestmark = pytest.mark.integration


def test_external_resources_endpoint_returns_normalized_live_response(client, monkeypatch):
    def fake_load(self, skill: str, limit: int):
        return [
            ExternalResource(
                title=f"{skill} interview repo",
                description="Questions and examples",
                url="https://github.com/example/interview",
                source="GitHub",
                stars=100,
                language="Python",
                updated_at="2026-05-12T00:00:00Z",
            )
        ]

    monkeypatch.setattr("app.services.external_resources.ExternalResourceService._load_from_github", fake_load)

    response = client.get("/api/v1/resources/interview-prep?skill=FastAPI&limit=1")

    assert response.status_code == 200
    body = response.json()
    assert body["external_status"] == "live"
    assert body["items"][0]["title"] == "FastAPI interview repo"
    assert body["items"][0]["stars"] == 100


def test_external_resources_endpoint_falls_back_when_external_api_fails(client, monkeypatch):
    def broken_load(self, skill: str, limit: int):
        raise RuntimeError("upstream timeout")

    monkeypatch.setattr("app.services.external_resources.ExternalResourceService._load_from_github", broken_load)

    response = client.get("/api/v1/resources/interview-prep?skill=React&limit=2")

    assert response.status_code == 200
    body = response.json()
    assert body["external_status"] == "fallback"
    assert body["warning"]
    assert len(body["items"]) == 2
