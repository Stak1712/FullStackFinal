from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, Query

from app.schemas.external_resource import ExternalResourceResponse
from app.services.external_resources import ExternalResourceService

router = APIRouter()


@lru_cache
def get_external_resource_service() -> ExternalResourceService:
    return ExternalResourceService()


@router.get("/interview-prep", response_model=ExternalResourceResponse)
def get_interview_preparation_resources(
    skill: str = Query(default="FastAPI", min_length=1, max_length=80),
    limit: int = Query(default=6, ge=1, le=12),
    service: ExternalResourceService = Depends(get_external_resource_service),
) -> ExternalResourceResponse:
    """Return normalized external resources for interview preparation."""

    return service.search_interview_resources(skill=skill, limit=limit)
