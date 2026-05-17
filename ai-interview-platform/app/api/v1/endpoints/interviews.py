from __future__ import annotations

from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.auth.dependencies import require_permissions
from app.auth.rbac import (
    PERMISSION_INTERVIEWS_CREATE,
    PERMISSION_INTERVIEWS_DELETE,
    PERMISSION_INTERVIEWS_READ,
    PERMISSION_INTERVIEWS_UPDATE,
)
from app.db.database import get_db
from app.models.interview import Interview
from app.schemas.interview import InterviewCreate, InterviewInResponse, InterviewUpdate

router = APIRouter()


class InterviewListResponse(BaseModel):
    items: list[InterviewInResponse]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool


@router.get("/", response_model=list[InterviewInResponse])
async def list_interviews(
    db: Session = Depends(get_db),
    _user=Depends(require_permissions(PERMISSION_INTERVIEWS_READ)),
):
    return db.query(Interview).order_by(Interview.id.desc()).all()


@router.get("/catalog", response_model=InterviewListResponse)
async def list_interviews_catalog(
    db: Session = Depends(get_db),
    _user=Depends(require_permissions(PERMISSION_INTERVIEWS_READ)),
    search: str | None = Query(default=None, max_length=120),
    status_filter: str | None = Query(default=None, alias="status", max_length=32),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
):
    query = db.query(Interview)
    if search:
        needle = f"%{search.strip()}%"
        query = query.filter(or_(Interview.title.ilike(needle), Interview.description.ilike(needle)))
    if status_filter:
        query = query.filter(Interview.status == status_filter.strip())

    sort_map = {
        "created_at": Interview.created_at,
        "title": Interview.title,
        "status": Interview.status,
        "score": Interview.last_answer_score,
    }
    sort_column = sort_map.get(sort_by, Interview.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc(), Interview.id.asc())
    else:
        query = query.order_by(sort_column.desc(), Interview.id.desc())

    total = query.with_entities(func.count(Interview.id)).scalar() or 0
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    pages = max(1, ceil(total / page_size)) if total else 1
    return InterviewListResponse(
        items=rows,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )


@router.post("/", response_model=InterviewInResponse)
async def create_interview(
    payload: InterviewCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_permissions(PERMISSION_INTERVIEWS_CREATE)),
):
    obj = Interview(title=payload.title, description=payload.description, status=payload.status or "active")
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{interview_id}", response_model=InterviewInResponse)
async def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_permissions(PERMISSION_INTERVIEWS_READ)),
):
    obj = db.get(Interview, interview_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    return obj


@router.put("/{interview_id}", response_model=InterviewInResponse)
async def update_interview(
    interview_id: int,
    payload: InterviewUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_permissions(PERMISSION_INTERVIEWS_UPDATE)),
):
    obj = db.get(Interview, interview_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    obj.title = payload.title
    obj.description = payload.description
    obj.status = payload.status or obj.status
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_permissions(PERMISSION_INTERVIEWS_DELETE)),
):
    obj = db.get(Interview, interview_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    db.delete(obj)
    db.commit()
    return None
