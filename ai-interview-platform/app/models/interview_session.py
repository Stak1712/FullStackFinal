from __future__ import annotations

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_email: Mapped[str] = mapped_column(String, index=True)

    direction: Mapped[str] = mapped_column(String, index=True)
    grade: Mapped[str] = mapped_column(String, default="junior")
    skills: Mapped[str] = mapped_column(Text, default="")

    status: Mapped[str] = mapped_column(String, default="active")
    current_step: Mapped[int] = mapped_column(Integer, default=0)

    max_questions: Mapped[int] = mapped_column(Integer, default=5)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
