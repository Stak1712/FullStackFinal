from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_session import RefreshSession


class RefreshSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, user_id: str, token_hash: str, expires_at: datetime) -> RefreshSession:
        session = RefreshSession(
            id=str(uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_token_hash(self, token_hash: str) -> RefreshSession | None:
        return self.db.execute(
            select(RefreshSession).where(RefreshSession.token_hash == token_hash)
        ).scalar_one_or_none()

    def rotate(self, session: RefreshSession, *, new_token_hash: str, new_expires_at: datetime) -> RefreshSession:
        session.token_hash = new_token_hash
        session.expires_at = new_expires_at
        session.last_rotated_at = datetime.utcnow()
        session.revoked_at = None
        self.db.commit()
        self.db.refresh(session)
        return session

    def revoke(self, session: RefreshSession) -> RefreshSession:
        session.revoked_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session
