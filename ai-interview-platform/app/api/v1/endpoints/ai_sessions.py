from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_permissions
from app.auth.rbac import (
    PERMISSION_AI_SESSION_ANSWER_OWN,
    PERMISSION_AI_SESSION_CREATE,
    PERMISSION_AI_SESSION_READ_ANY,
    PERMISSION_AI_SESSION_READ_OWN,
)
from app.db.database import get_db
from app.models.interview_session import InterviewSession
from app.models.interview_turn import InterviewTurn
from app.services.ai_interviewer import evaluate_answer, get_question_by_id, normalize_grade, pick_next_question


router = APIRouter()


class StartSessionIn(BaseModel):
    grade: str = Field(..., min_length=1)
    skills: list[str] = Field(default_factory=list)


class StartSessionOut(BaseModel):
    session_id: int
    question: str


@router.post("/sessions", response_model=StartSessionOut)
def start_session(
    data: StartSessionIn,
    db: Session = Depends(get_db),
    user=Depends(require_permissions(PERMISSION_AI_SESSION_CREATE)),
):
    grade = normalize_grade(data.grade)
    skills_csv = ", ".join(data.skills or [])

    s = InterviewSession(
        user_email=user["email"],
        direction="mixed",
        grade=grade,
        skills=skills_csv,
        current_step=0,
        status="active",
        max_questions=5,
    )
    db.add(s)
    db.commit()
    db.refresh(s)

    seed_score = 0 if grade == "junior" else (50 if grade == "middle" else 70)
    q = pick_next_question(grade=grade, skills=data.skills, asked_ids=[], prev_score=seed_score)

    db.add(InterviewTurn(session_id=s.id, role="ai", text=q["text"], question_id=q["id"]))
    db.commit()

    return {"session_id": s.id, "question": q["text"]}


class AnswerIn(BaseModel):
    text: str = Field(..., min_length=1)


class AnswerOut(BaseModel):
    score: int
    verdict: str
    next_question: str | None



def _ensure_session_access(session: InterviewSession, user: dict, for_answer: bool = False) -> None:
    own_session = session.user_email == user.get("email")
    current_permissions = set(user.get("permissions") or [])

    if own_session:
        needed = PERMISSION_AI_SESSION_ANSWER_OWN if for_answer else PERMISSION_AI_SESSION_READ_OWN
        if needed not in current_permissions:
            raise HTTPException(status_code=403, detail="Forbidden")
        return

    if PERMISSION_AI_SESSION_READ_ANY in current_permissions and not for_answer:
        return

    raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/sessions/{session_id}/answer", response_model=AnswerOut)
def answer(
    session_id: int,
    data: AnswerIn,
    db: Session = Depends(get_db),
    user=Depends(require_permissions(PERMISSION_AI_SESSION_ANSWER_OWN)),
):
    s = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    _ensure_session_access(s, user, for_answer=True)
    if s.status != "active":
        raise HTTPException(status_code=400, detail="Session finished")

    last_ai = (
        db.query(InterviewTurn)
        .filter(InterviewTurn.session_id == session_id, InterviewTurn.role == "ai")
        .order_by(InterviewTurn.id.desc())
        .first()
    )
    if not last_ai or not last_ai.question_id:
        raise HTTPException(status_code=400, detail="No active question")

    question = get_question_by_id(last_ai.question_id)
    if not question:
        raise HTTPException(status_code=400, detail="Unknown question")

    res = evaluate_answer(data.text, question, direction=s.direction)

    db.add(
        InterviewTurn(
            session_id=s.id,
            role="user",
            text=data.text,
            score=res["score"],
            verdict=res["verdict"],
        )
    )

    s.current_step += 1

    if s.current_step >= (s.max_questions or 5):
        s.status = "finished"
        db.add(
            InterviewTurn(
                session_id=s.id,
                role="ai",
                text="Интервью завершено. Спасибо!",
            )
        )
        db.commit()
        return {
            "score": res["score"],
            "verdict": res["verdict"],
            "next_question": None,
        }

    asked_ids = [
        t.question_id
        for t in db.query(InterviewTurn)
        .filter(InterviewTurn.session_id == session_id, InterviewTurn.role == "ai")
        .order_by(InterviewTurn.id.asc())
        .all()
        if t.question_id
    ]

    skills_list = [x.strip() for x in (s.skills or "").split(",") if x.strip()]
    q2 = pick_next_question(
        grade=s.grade,
        skills=skills_list,
        asked_ids=asked_ids,
        prev_score=res["score"],
        prev_skill=question.get("skill"),
    )
    next_q_text = q2["text"]
    db.add(InterviewTurn(session_id=s.id, role="ai", text=next_q_text, question_id=q2["id"]))
    db.commit()

    return {
        "score": res["score"],
        "verdict": res["verdict"],
        "next_question": next_q_text,
    }


@router.get("/sessions/{session_id}")
def get_history(
    session_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    s = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    _ensure_session_access(s, user, for_answer=False)

    turns = (
        db.query(InterviewTurn)
        .filter(InterviewTurn.session_id == session_id)
        .order_by(InterviewTurn.id.asc())
        .all()
    )

    return {
        "session": {
            "id": s.id,
            "grade": s.grade,
            "skills": s.skills,
            "status": s.status,
            "step": s.current_step,
            "max_questions": s.max_questions,
        },
        "turns": [
            {
                "role": t.role,
                "text": t.text,
                "score": t.score,
                "verdict": t.verdict,
                "created_at": t.created_at.isoformat(),
            }
            for t in turns
        ],
    }
