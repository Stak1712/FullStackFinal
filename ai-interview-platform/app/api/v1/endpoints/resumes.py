from __future__ import annotations

from math import ceil

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.rbac import (
    PERMISSION_RESUMES_DOWNLOAD_ANY,
    PERMISSION_RESUMES_DOWNLOAD_OWN,
    PERMISSION_RESUMES_READ_ANY,
    PERMISSION_RESUMES_READ_OWN,
    PERMISSION_RESUMES_UPLOAD,
)
from app.db.database import get_db
from app.models.resume_asset import ResumeAsset
from app.schemas.resume import ResumeCompleteRequest, ResumeListResponse, ResumeOut, ResumeUploadRequest, ResumeUploadTarget
from app.services.storage import StorageService

router = APIRouter()


def _parse_skills(csv_value: str | None) -> list[str]:
    if not csv_value:
        return []
    return [part.strip() for part in csv_value.split(",") if part.strip()]



def _resume_to_out(resume: ResumeAsset, request: Request, storage: StorageService) -> ResumeOut:
    return ResumeOut(
        id=resume.id,
        owner_id=resume.owner_id,
        title=resume.title,
        original_filename=resume.original_filename,
        content_type=resume.content_type,
        size_bytes=resume.size_bytes,
        storage_provider=resume.storage_provider,
        bucket_name=resume.bucket_name,
        status=resume.status,
        grade=resume.grade,
        skills=_parse_skills(resume.skills_csv),
        summary=resume.summary,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
        download_url=storage.create_download_url(
            base_url=str(request.base_url).rstrip("/"),
            object_key=resume.object_key,
            filename=resume.original_filename,
        ) if resume.status == "uploaded" else None,
    )



def _can_read_any(user: dict) -> bool:
    return PERMISSION_RESUMES_READ_ANY in set(user.get("permissions") or [])



def _can_download_any(user: dict) -> bool:
    return PERMISSION_RESUMES_DOWNLOAD_ANY in set(user.get("permissions") or [])



def _ensure_read_access(resume: ResumeAsset, user: dict) -> None:
    permissions = set(user.get("permissions") or [])
    if resume.owner_id == user.get("id") and PERMISSION_RESUMES_READ_OWN in permissions:
        return
    if PERMISSION_RESUMES_READ_ANY in permissions:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")



def _ensure_download_access(resume: ResumeAsset, user: dict) -> None:
    permissions = set(user.get("permissions") or [])
    if resume.owner_id == user.get("id") and PERMISSION_RESUMES_DOWNLOAD_OWN in permissions:
        return
    if PERMISSION_RESUMES_DOWNLOAD_ANY in permissions:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


@router.get("/", response_model=ResumeListResponse)
def list_resumes(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    search: str | None = Query(default=None, max_length=120),
    grade: str | None = Query(default=None, max_length=32),
    status_filter: str | None = Query(default=None, alias="status", max_length=32),
    skills_any: str | None = Query(default=None, description="Comma separated skill names"),
    owner_id: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
):
    permissions = set(user.get("permissions") or [])
    if PERMISSION_RESUMES_READ_OWN not in permissions and PERMISSION_RESUMES_READ_ANY not in permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    query = db.query(ResumeAsset)

    if _can_read_any(user):
        if owner_id:
            query = query.filter(ResumeAsset.owner_id == owner_id)
    else:
        query = query.filter(ResumeAsset.owner_id == user.get("id"))

    if search:
        needle = f"%{search.strip()}%"
        query = query.filter(or_(ResumeAsset.title.ilike(needle), ResumeAsset.original_filename.ilike(needle), ResumeAsset.summary.ilike(needle)))
    if grade:
        query = query.filter(ResumeAsset.grade == grade.strip())
    if status_filter:
        query = query.filter(ResumeAsset.status == status_filter.strip())
    if skills_any:
        for skill in [part.strip() for part in skills_any.split(",") if part.strip()]:
            query = query.filter(ResumeAsset.skills_csv.ilike(f"%{skill}%"))

    sort_map = {
        "created_at": ResumeAsset.created_at,
        "title": ResumeAsset.title,
        "size_bytes": ResumeAsset.size_bytes,
        "grade": ResumeAsset.grade,
        "status": ResumeAsset.status,
    }
    sort_column = sort_map.get(sort_by, ResumeAsset.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc(), ResumeAsset.id.asc())
    else:
        query = query.order_by(sort_column.desc(), ResumeAsset.id.desc())

    total = query.with_entities(func.count(ResumeAsset.id)).scalar() or 0
    rows = query.offset((page - 1) * page_size).limit(page_size).all()

    storage = StorageService()
    items = [_resume_to_out(row, request, storage) for row in rows]
    pages = max(1, ceil(total / page_size)) if total else 1
    return ResumeListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )


@router.post("/upload-url", response_model=ResumeUploadTarget, status_code=status.HTTP_201_CREATED)
def create_resume_upload_target(
    payload: ResumeUploadRequest,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    permissions = set(user.get("permissions") or [])
    if PERMISSION_RESUMES_UPLOAD not in permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    storage = StorageService()
    if payload.size_bytes > storage.max_file_size_bytes():
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File is too large")

    normalized_content_type = storage.normalize_content_type(payload.content_type, payload.filename)
    object_key = storage.generate_object_key(str(user.get("id")), payload.filename)
    skills_csv = ", ".join(sorted({skill.strip() for skill in payload.skills if skill.strip()})) or None

    resume = ResumeAsset(
        owner_id=str(user.get("id")),
        title=payload.title.strip(),
        original_filename=storage.sanitize_filename(payload.filename),
        object_key=object_key,
        content_type=normalized_content_type,
        size_bytes=payload.size_bytes,
        storage_provider=storage.provider_name(),
        bucket_name=storage.bucket_name(),
        status="pending_upload",
        grade=(payload.grade or "").strip().lower() or None,
        skills_csv=skills_csv,
        summary=payload.summary,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    upload_url = storage.create_upload_url(
        base_url=str(request.base_url).rstrip("/"),
        object_key=object_key,
        filename=resume.original_filename,
        content_type=normalized_content_type,
    )
    return ResumeUploadTarget(
        resume=_resume_to_out(resume, request, storage),
        upload_url=upload_url,
        upload_method="PUT",
        expires_in=int(storage.settings.STORAGE_SIGNED_URL_EXPIRES_SECONDS),
    )


@router.post("/{resume_id}/complete", response_model=ResumeOut)
def complete_resume_upload(
    resume_id: int,
    request: Request,
    payload: ResumeCompleteRequest | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    resume = db.get(ResumeAsset, resume_id)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    _ensure_read_access(resume, user)

    storage = StorageService()
    if not storage.object_exists(resume.object_key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is not found in object storage")

    resume.status = (payload.status if payload else "uploaded") or "uploaded"
    resume.size_bytes = storage.object_size(resume.object_key) or resume.size_bytes
    db.commit()
    db.refresh(resume)
    return _resume_to_out(resume, request, storage)


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(
    resume_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    resume = db.get(ResumeAsset, resume_id)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    _ensure_read_access(resume, user)
    return _resume_to_out(resume, request, StorageService())


@router.get("/{resume_id}/download-link")
def get_resume_download_link(
    resume_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    resume = db.get(ResumeAsset, resume_id)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    _ensure_download_access(resume, user)
    storage = StorageService()
    return {
        "resume_id": resume.id,
        "download_url": storage.create_download_url(
            base_url=str(request.base_url).rstrip("/"),
            object_key=resume.object_key,
            filename=resume.original_filename,
        ),
        "expires_in": int(storage.settings.STORAGE_SIGNED_URL_EXPIRES_SECONDS),
    }


@router.put("/storage/upload/{token}", status_code=status.HTTP_204_NO_CONTENT)
def signed_upload(token: str, request: Request, body: bytes = Body(default=b"")):
    storage = StorageService()
    storage.save_upload(token=token, payload=body, content_type=request.headers.get("content-type"))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/storage/download/{token}")
def signed_download(token: str):
    storage = StorageService()
    return storage.build_download_response(token)
