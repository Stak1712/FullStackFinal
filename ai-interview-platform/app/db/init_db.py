from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select, text

from app.auth.rbac import ROLE_ADMIN, normalize_role
from app.db.database import SessionLocal, engine
from app.models import Interview, InterviewSession, InterviewTurn, RefreshSession, ResumeAsset, User  # noqa: F401



def init_db() -> None:
    from app.db.database import Base

    Path("data").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    _ensure_schema()
    _migrate_users_json_once()
    _bootstrap_admin_if_missing()



def _ensure_schema() -> None:
    with engine.begin() as conn:
        cols = [r[1] for r in conn.execute(text("PRAGMA table_info(interview_turns)")).fetchall()]
        if "question_id" not in cols:
            conn.execute(text("ALTER TABLE interview_turns ADD COLUMN question_id VARCHAR"))
        if "feedback" not in cols:
            conn.execute(text("ALTER TABLE interview_turns ADD COLUMN feedback TEXT"))
        cols_s = [r[1] for r in conn.execute(text("PRAGMA table_info(interview_sessions)")).fetchall()]
        if "max_questions" not in cols_s:
            conn.execute(text("ALTER TABLE interview_sessions ADD COLUMN max_questions INTEGER DEFAULT 5"))
        refresh_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(refresh_sessions)")).fetchall()]
        if refresh_cols and "last_rotated_at" not in refresh_cols:
            conn.execute(text("ALTER TABLE refresh_sessions ADD COLUMN last_rotated_at DATETIME"))
        if refresh_cols and "updated_at" not in refresh_cols:
            conn.execute(text("ALTER TABLE refresh_sessions ADD COLUMN updated_at DATETIME"))



def _migrate_users_json_once() -> None:
    json_path = Path("data/users.json")
    if not json_path.exists():
        return

    with SessionLocal() as db:
        existing = db.execute(select(User.id).limit(1)).first()
        if existing:
            return

        try:
            raw = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            return

        users = raw.get("users") if isinstance(raw, dict) else None
        if not isinstance(users, list):
            return

        for item in users:
            if not isinstance(item, dict):
                continue
            if not item.get("id") or not item.get("email"):
                continue

            role = normalize_role(item.get("role") or "user")
            u = User(
                id=str(item.get("id")),
                first_name=str(item.get("first_name") or ""),
                last_name=str(item.get("last_name") or ""),
                email=str(item.get("email")),
                password_hash=str(item.get("password_hash")),
                role=role,
            )
            db.add(u)

        db.commit()



def _bootstrap_admin_if_missing() -> None:
    with SessionLocal() as db:
        admin = db.execute(select(User).where(User.role == ROLE_ADMIN).limit(1)).scalar_one_or_none()
        if admin:
            return

        oldest_user = db.execute(select(User).order_by(User.created_at.asc()).limit(1)).scalar_one_or_none()
        if not oldest_user:
            return

        oldest_user.role = ROLE_ADMIN
        db.commit()
