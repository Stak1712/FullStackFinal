from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_permissions
from app.auth.rbac import PERMISSION_AI_SCORE, PERMISSION_INTERVIEWS_UPDATE
from app.db.database import get_db
from app.ml.text_scorer import score_answer
from app.models.interview import Interview
from app.schemas.ml import MLScoreRequest, MLScoreResponse, MLEvaluateInterviewResponse


router = APIRouter()


@router.post("/score", response_model=MLScoreResponse)
async def score(
    payload: MLScoreRequest,
    _user=Depends(require_permissions(PERMISSION_AI_SCORE)),
):
    result = score_answer(answer=payload.answer, question=payload.question, direction=payload.direction)
    return MLScoreResponse(score=result["score"], verdict=result["verdict"])


@router.post("/interviews/{interview_id}/evaluate", response_model=MLEvaluateInterviewResponse)
async def evaluate_interview(
    interview_id: int,
    payload: MLScoreRequest,
    db: Session = Depends(get_db),
    _user=Depends(require_permissions(PERMISSION_INTERVIEWS_UPDATE)),
):
    obj = db.get(Interview, interview_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    result = score_answer(answer=payload.answer, question=payload.question, direction=payload.direction)
    obj.last_answer_score = result["score"]
    obj.last_answer_verdict = result["verdict"]
    db.commit()
    db.refresh(obj)

    return MLEvaluateInterviewResponse(
        interview_id=obj.id,
        score=result["score"],
        verdict=result["verdict"],
    )
