from __future__ import annotations

from typing import Any
from uuid import uuid4

from sqlalchemy import exists, func, select

from app.auth.rbac import ROLE_ADMIN, get_permissions_for_role, normalize_role
from app.core.security import hash_password, verify_password
from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.auth import RegisterRequest



def _public_user(u: User) -> dict[str, Any]:
    return {
        "id": u.id,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "email": u.email,
        "role": normalize_role(u.role),
        "permissions": get_permissions_for_role(u.role),
        "created_at": u.created_at,
    }



def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        u = db.get(User, user_id)
        return _public_user(u) if u else None



def get_user_by_email(email: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        u = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        return _public_user(u) if u else None



def list_users() -> list[dict[str, Any]]:
    with SessionLocal() as db:
        rows = db.execute(select(User).order_by(User.created_at.desc())).scalars().all()
        return [_public_user(u) for u in rows]



def _admin_exists(db) -> bool:
    stmt = select(exists().where(User.role == ROLE_ADMIN))
    return bool(db.execute(stmt).scalar())



def create_user(payload: RegisterRequest) -> dict[str, Any]:
    with SessionLocal() as db:
        exists_row = db.execute(select(User.id).where(User.email == str(payload.email))).first()
        if exists_row:
            raise ValueError("User with this email already exists")

        assigned_role = ROLE_ADMIN if not _admin_exists(db) else "user"

        u = User(
            id=str(uuid4()),
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=str(payload.email),
            password_hash=hash_password(payload.password),
            role=assigned_role,
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        return _public_user(u)



def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        u = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not u:
            return None
        if not verify_password(password, u.password_hash):
            return None
        return _public_user(u)



def update_user_role(user_id: str, new_role: str) -> dict[str, Any]:
    normalized_role = normalize_role(new_role)
    with SessionLocal() as db:
        u = db.get(User, user_id)
        if not u:
            raise ValueError("User not found")
        u.role = normalized_role
        db.commit()
        db.refresh(u)
        return _public_user(u)



def has_any_user() -> bool:
    with SessionLocal() as db:
        total = db.execute(select(func.count()).select_from(User)).scalar_one()
        return bool(total)
