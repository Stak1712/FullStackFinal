from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.refresh_sessions import RefreshSessionRepository
from app.repositories.users import UserRepository
from app.services.auth_service import AuthService


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(
        users=UserRepository(db),
        refresh_sessions=RefreshSessionRepository(db),
    )
