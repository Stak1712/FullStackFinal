from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class ExternalResource(BaseModel):
    title: str
    description: str | None = None
    url: HttpUrl
    source: str = "GitHub"
    stars: int = Field(default=0, ge=0)
    language: str | None = None
    updated_at: str | None = None


class ExternalResourceResponse(BaseModel):
    query: str
    source: str
    external_status: str
    items: list[ExternalResource]
    warning: str | None = None
