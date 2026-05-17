from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException, status

from app.auth.rbac import ROLE_ADMIN, get_permissions_for_role
from app.core.config import get_settings
from app.core.security import create_access_token, generate_refresh_token, hash_password, hash_token, verify_password
from app.repositories.refresh_sessions import RefreshSessionRepository
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, *, users: UserRepository, refresh_sessions: RefreshSessionRepository):
        self.users = users
        self.refresh_sessions = refresh_sessions
        self.settings = get_settings()

    def register(self, payload: RegisterRequest) -> dict:
        existing = self.users.get_by_email(str(payload.email))
        if existing:
            raise ValueError("User with this email already exists")

        assigned_role = ROLE_ADMIN if not self.users.admin_exists() else "user"
        user = self.users.create(
            user_id=str(uuid4()),
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=str(payload.email),
            password_hash=hash_password(payload.password),
            role=assigned_role,
        )
        return self._public_user(user)

    def login(self, payload: LoginRequest) -> dict:
        user = self.users.get_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        return self._issue_session(user)

    def refresh(self, refresh_token: str) -> dict:
        session = self.refresh_sessions.get_by_token_hash(hash_token(refresh_token))
        if not session or session.revoked_at is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        if session.expires_at <= datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        user = self.users.get_by_id(session.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        new_refresh_token = generate_refresh_token()
        new_expires_at = datetime.utcnow() + timedelta(days=self.settings.REFRESH_TOKEN_EXPIRES_DAYS)
        session = self.refresh_sessions.rotate(
            session,
            new_token_hash=hash_token(new_refresh_token),
            new_expires_at=new_expires_at,
        )
        access_token = create_access_token(
            sub=user.id,
            email=user.email,
            role=user.role,
            session_id=session.id,
            expires_in_seconds=self.settings.ACCESS_TOKEN_EXPIRES_SECONDS,
        )
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "access_expires_in": self.settings.ACCESS_TOKEN_EXPIRES_SECONDS,
        }

    def logout(self, refresh_token: str) -> None:
        session = self.refresh_sessions.get_by_token_hash(hash_token(refresh_token))
        if session and session.revoked_at is None:
            self.refresh_sessions.revoke(session)

    def _issue_session(self, user) -> dict:
        refresh_token = generate_refresh_token()
        expires_at = datetime.utcnow() + timedelta(days=self.settings.REFRESH_TOKEN_EXPIRES_DAYS)
        session = self.refresh_sessions.create(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
        )
        access_token = create_access_token(
            sub=user.id,
            email=user.email,
            role=user.role,
            session_id=session.id,
            expires_in_seconds=self.settings.ACCESS_TOKEN_EXPIRES_SECONDS,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "access_expires_in": self.settings.ACCESS_TOKEN_EXPIRES_SECONDS,
        }

    @staticmethod
    def _public_user(user) -> dict:
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "permissions": get_permissions_for_role(user.role),
            "created_at": user.created_at,
        }
