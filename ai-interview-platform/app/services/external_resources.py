from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock
from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.schemas.external_resource import ExternalResource, ExternalResourceResponse


@dataclass
class CacheEntry:
    expires_at: float
    value: ExternalResourceResponse


class ExternalResourceService:
    """Adapter around a third-party API used in Lab 4.

    The platform uses GitHub Search API as an external source of interview
    preparation materials. The service isolates timeout/retry/cache/rate-limit
    logic from the FastAPI endpoint, so the API layer stays thin.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._cache: dict[str, CacheEntry] = {}
        self._request_timestamps: list[float] = []
        self._lock = Lock()

    def search_interview_resources(self, skill: str, limit: int = 6) -> ExternalResourceResponse:
        normalized_skill = self._normalize_skill(skill)
        safe_limit = max(1, min(int(limit), 12))
        cache_key = f"{normalized_skill.lower()}:{safe_limit}"

        cached = self._get_cache(cache_key)
        if cached:
            return cached

        if not self._allow_request():
            return self._fallback_response(
                normalized_skill,
                safe_limit,
                warning="Локальный rate limit внешнего API временно исчерпан. Показаны резервные материалы.",
            )

        try:
            items = self._load_from_github(normalized_skill, safe_limit)
            response = ExternalResourceResponse(
                query=normalized_skill,
                source="GitHub Search API",
                external_status="live",
                items=items,
            )
        except Exception as exc:  # pragma: no cover - depends on external network
            response = self._fallback_response(
                normalized_skill,
                safe_limit,
                warning=f"Внешний API временно недоступен: {exc}. Показаны резервные материалы.",
            )

        self._set_cache(cache_key, response)
        return response

    def _load_from_github(self, skill: str, limit: int) -> list[ExternalResource]:
        api_url = self.settings.GITHUB_API_URL.rstrip("/")
        url = f"{api_url}/search/repositories"
        query = f'{skill} interview questions preparation in:name,description,readme'
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "ai-interview-platform-lab4",
        }
        if self.settings.GITHUB_API_TOKEN:
            headers["Authorization"] = f"Bearer {self.settings.GITHUB_API_TOKEN}"

        last_error: Exception | None = None
        attempts = max(1, int(self.settings.EXTERNAL_API_RETRIES) + 1)
        timeout = float(self.settings.EXTERNAL_API_TIMEOUT_SECONDS)

        for attempt in range(attempts):
            try:
                with httpx.Client(timeout=timeout, headers=headers) as client:
                    response = client.get(
                        url,
                        params={
                            "q": query,
                            "sort": "stars",
                            "order": "desc",
                            "per_page": limit,
                        },
                    )
                response.raise_for_status()
                payload = response.json()
                return self._normalize_github_items(payload.get("items") or [], limit)
            except Exception as exc:  # pragma: no cover - depends on external network
                last_error = exc
                if attempt < attempts - 1:
                    time.sleep(0.2 * (attempt + 1))

        raise RuntimeError(str(last_error) if last_error else "unknown external API error")

    def _normalize_github_items(self, raw_items: list[dict[str, Any]], limit: int) -> list[ExternalResource]:
        normalized: list[ExternalResource] = []
        for item in raw_items[:limit]:
            html_url = item.get("html_url")
            name = item.get("full_name") or item.get("name")
            if not html_url or not name:
                continue
            normalized.append(
                ExternalResource(
                    title=str(name),
                    description=item.get("description") or "Материал для подготовки к техническому интервью.",
                    url=html_url,
                    source="GitHub",
                    stars=int(item.get("stargazers_count") or 0),
                    language=item.get("language"),
                    updated_at=item.get("updated_at"),
                )
            )
        return normalized

    def _fallback_response(self, skill: str, limit: int, warning: str) -> ExternalResourceResponse:
        items = [
            ExternalResource(
                title=f"{skill}: чек-лист подготовки к интервью",
                description="Повторить базовые определения, типовые вопросы, практические задачи и примеры из собственного опыта.",
                url="https://github.com/search?q=interview+preparation",
                source="Fallback",
                stars=0,
                language=None,
                updated_at=None,
            ),
            ExternalResource(
                title=f"{skill}: вопросы для самопроверки",
                description="Составить 10–15 вопросов по выбранному навыку и ответить на них вслух в формате mock interview.",
                url="https://github.com/search?q=technical+interview+questions",
                source="Fallback",
                stars=0,
                language=None,
                updated_at=None,
            ),
            ExternalResource(
                title=f"{skill}: практические задачи",
                description="Найти небольшую задачу, решить её, объяснить сложность решения и возможные улучшения.",
                url="https://github.com/search?q=coding+interview+practice",
                source="Fallback",
                stars=0,
                language=None,
                updated_at=None,
            ),
        ][:limit]
        return ExternalResourceResponse(
            query=skill,
            source="local fallback",
            external_status="fallback",
            items=items,
            warning=warning,
        )

    def _allow_request(self) -> bool:
        now = time.monotonic()
        window_start = now - 60
        with self._lock:
            self._request_timestamps = [ts for ts in self._request_timestamps if ts >= window_start]
            if len(self._request_timestamps) >= int(self.settings.EXTERNAL_API_RATE_LIMIT_PER_MINUTE):
                return False
            self._request_timestamps.append(now)
            return True

    def _get_cache(self, key: str) -> ExternalResourceResponse | None:
        entry = self._cache.get(key)
        if not entry:
            return None
        if entry.expires_at < time.monotonic():
            self._cache.pop(key, None)
            return None
        return entry.value

    def _set_cache(self, key: str, value: ExternalResourceResponse) -> None:
        ttl = max(0, int(self.settings.EXTERNAL_API_CACHE_TTL_SECONDS))
        if ttl:
            self._cache[key] = CacheEntry(expires_at=time.monotonic() + ttl, value=value)

    def _normalize_skill(self, skill: str) -> str:
        cleaned = " ".join((skill or "").strip().split())
        return cleaned[:80] or "FastAPI"
