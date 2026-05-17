from __future__ import annotations

from pydantic import BaseModel, Field


class MLScoreRequest(BaseModel):
    answer: str = Field(min_length=1)
    question: str | None = None
    direction: str | None = None


class MLScoreResponse(BaseModel):
    score: int
    verdict: str


class MLEvaluateInterviewResponse(MLScoreResponse):
    interview_id: int
