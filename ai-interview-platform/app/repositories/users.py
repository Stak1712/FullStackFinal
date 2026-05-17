from __future__ import annotations

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.auth.rbac import ROLE_ADMIN, normalize_role
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    def admin_exists(self) -> bool:
        stmt = select(exists().where(User.role == ROLE_ADMIN))
        return bool(self.db.execute(stmt).scalar())

    def create(self, *, user_id: str, first_name: str, last_name: str, email: str, password_hash: str, role: str) -> User:
        user = User(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role=normalize_role(role),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
