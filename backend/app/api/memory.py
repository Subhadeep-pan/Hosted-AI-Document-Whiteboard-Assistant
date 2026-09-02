"""Long-term memory endpoints (Section 7 of the upgrade plan) - lets the
frontend show/edit what the agent has learned about the user's
preferences."""

from fastapi import APIRouter, Header
from pydantic import BaseModel

from backend.app.services.memory_service import get_preferences, set_preference

router = APIRouter()


class PreferenceRequest(BaseModel):
    key: str
    value: str


@router.get("/memory/preferences")
def list_preferences(x_session_id: str = Header(default="default")):
    return {"preferences": get_preferences(x_session_id)}


@router.post("/memory/preferences")
def update_preference(payload: PreferenceRequest, x_session_id: str = Header(default="default")):
    set_preference(x_session_id, payload.key, payload.value)
    return {"status": "saved"}
