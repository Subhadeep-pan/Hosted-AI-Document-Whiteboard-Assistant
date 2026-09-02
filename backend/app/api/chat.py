from time import sleep
import json

from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse

from backend.app.services.agent_service import run_agent
from backend.app.services.chat_memory import get_chat_title
from backend.app.services.rate_limiter import is_rate_limited

router = APIRouter()

RATE_LIMIT_MESSAGE = (
    "You're sending messages too fast. "
    "Please wait a minute and try again."
)

# Marks where the visible answer text ends and a trailing JSON blob of
# metadata (tools_used/sources/confidence) begins, inside the plain-text
# stream. The frontend splits on this and never renders it.
META_DELIMITER = "\n<<<META>>>"


def stream_text(text, meta=None):
    """Stream text word by word, then (if given) append a metadata
    footer the frontend can parse out separately."""

    for word in text.split():
        yield word + " "
        sleep(0.03)

    if meta is not None:
        yield META_DELIMITER + json.dumps(meta)


@router.get("/ask")
def ask_question(
    question: str,
    chat_id: str,
    x_session_id: str = Header(default="default"),
):
    if is_rate_limited(x_session_id):
        return {"answer": RATE_LIMIT_MESSAGE}

    result = run_agent(question, x_session_id, chat_id)

    return {
        "answer": result["answer"],
        "title": get_chat_title(x_session_id, chat_id),
        # New: lets the frontend show "Tools Used / Memory Used / Live
        # Data / Sources / Confidence" per the upgrade plan (section 15).
        "tools_used": result["tools_used"],
        "sources": result["sources"],
        "confidence": result["confidence"],
    }


@router.get("/ask/stream")
def ask_question_stream(
    question: str,
    chat_id: str,
    x_session_id: str = Header(default="default"),
):
    if is_rate_limited(x_session_id):
        return StreamingResponse(
            stream_text(RATE_LIMIT_MESSAGE),
            media_type="text/plain",
        )

    result = run_agent(question, x_session_id, chat_id)

    meta = {
        "tools_used": result["tools_used"],
        "sources": result["sources"],
        "confidence": result["confidence"],
    }

    return StreamingResponse(
        stream_text(result["answer"], meta=meta),
        media_type="text/plain",
    )