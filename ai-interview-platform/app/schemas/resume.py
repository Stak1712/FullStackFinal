from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ResumeUploadRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=1, max_length=120)
    size_bytes: int = Field(..., ge=1)
    grade: str | None = Field(default=None, max_length=32)
    skills: list[str] = Field(default_factory=list)
    summary: str | None = Field(default=None, max_length=4000)


class ResumeCompleteRequest(BaseModel):
    status: str = "uploaded"


class ResumeOut(BaseModel):
    id: int
    owner_id: str
    title: str
    original_filename: str
    content_type: str
    size_bytes: int
    storage_provider: str
    bucket_name: str | None = None
    status: str
    grade: str | None = None
    skills: list[str] = Field(default_factory=list)
    summary: str | None = None
    created_at: datetime
    updated_at: datetime
    download_url: str | None = None

    model_config = {"from_attributes": True}


class ResumeUploadTarget(BaseModel):
    resume: ResumeOut
    upload_url: str
    upload_method: str = "PUT"
    expires_in: int


class ResumeListResponse(BaseModel):
    items: list[ResumeOut]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool
