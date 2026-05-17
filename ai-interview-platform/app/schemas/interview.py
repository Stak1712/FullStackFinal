from pydantic import BaseModel
from typing import Optional

class InterviewBase(BaseModel):
    title: str
    description: str
    status: Optional[str] = "active"  # Статус по умолчанию

class InterviewCreate(InterviewBase):
    pass

class InterviewUpdate(InterviewBase):
    pass

class InterviewInResponse(InterviewBase):
    id: int  # ID интервью
    last_answer_score: Optional[int] = None
    last_answer_verdict: Optional[str] = None

    model_config = {"from_attributes": True}