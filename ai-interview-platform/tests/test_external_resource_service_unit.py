import pytest

from app.core.config import Settings
from app.schemas.external_resource import ExternalResource
from app.services.external_resources import ExternalResourceService


pytestmark = pytest.mark.unit


def test_external_service_uses_cache_for_repeated_request(monkeypatch):
    settings = Settings(EXTERNAL_API_CACHE_TTL_SECONDS=60, EXTERNAL_API_RATE_LIMIT_PER_MINUTE=30)
    service = ExternalResourceService(settings=settings)
    calls = {"count": 0}

    def fake_load(skill: str, limit: int):
        calls["count"] += 1
        return [ExternalResource(title="Repo", description="Desc", url="https://github.com/example/repo", source="GitHub", stars=1)]

    monkeypatch.setattr(service, "_load_from_github", fake_load)

    first = service.search_interview_resources("FastAPI", 1)
    second = service.search_interview_resources("FastAPI", 1)

    assert first.items[0].title == "Repo"
    assert second.items[0].title == "Repo"
    assert calls["count"] == 1


def test_external_service_rate_limit_returns_fallback(monkeypatch):
    settings = Settings(EXTERNAL_API_CACHE_TTL_SECONDS=0, EXTERNAL_API_RATE_LIMIT_PER_MINUTE=1)
    service = ExternalResourceService(settings=settings)

    monkeypatch.setattr(
        service,
        "_load_from_github",
        lambda skill, limit: [ExternalResource(title="Repo", description="Desc", url="https://github.com/example/repo", source="GitHub", stars=1)],
    )

    live = service.search_interview_resources("React", 1)
    fallback = service.search_interview_resources("React", 1)

    assert live.external_status == "live"
    assert fallback.external_status == "fallback"
    assert "rate limit" in (fallback.warning or "")
