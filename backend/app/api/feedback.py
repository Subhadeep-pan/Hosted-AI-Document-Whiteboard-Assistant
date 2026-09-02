"""Feedback endpoints (Section 6 of the upgrade plan) - the 👍/👎 the
frontend calls after showing an answer."""

from fastapi import APIRouter, Header
from pydantic import BaseModel

from backend.app.services.learning_service import submit_feedback
from backend.app.services.memory_service import get_feedback_history

router = APIRouter()


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    helpful: bool
    correction: str | None = None


@router.post("/feedback")
def post_feedback(payload: FeedbackRequest, x_session_id: str = Header(default="default")):
    submit_feedback(
        x_session_id,
        payload.question,
        payload.answer,
        payload.helpful,
        payload.correction,
    )
    return {"status": "recorded"}


@router.get("/feedback/history")
def feedback_history(x_session_id: str = Header(default="default")):
    return {"history": get_feedback_history(x_session_id)}
