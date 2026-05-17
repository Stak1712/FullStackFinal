from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth.dependencies import enforce_path_user_or_permission, get_current_user, require_permissions
from app.auth.rbac import PERMISSION_PROFILE_READ_ANY, PERMISSION_USER_LIST_READ, get_permissions_for_role
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserOut


router = APIRouter()


@router.get("/", response_model=list[UserOut])
async def list_users_endpoint(
    db: Session = Depends(get_db),
    _user=Depends(require_permissions(PERMISSION_USER_LIST_READ)),
):
    rows = db.query(User).order_by(User.created_at.desc()).all()
    return [UserOut.model_validate({
        "id": u.id,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "email": u.email,
        "role": u.role,
        "permissions": get_permissions_for_role(u.role),
        "created_at": u.created_at,
    }) for u in rows]


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_path_user_or_permission(request, current_user, PERMISSION_PROFILE_READ_ANY)
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserOut.model_validate({
        "id": u.id,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "email": u.email,
        "role": u.role,
        "permissions": get_permissions_for_role(u.role),
        "created_at": u.created_at,
    })
