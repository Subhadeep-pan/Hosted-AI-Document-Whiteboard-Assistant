from fastapi import APIRouter, Header
import os
import shutil

from backend.app.services.chroma_service import delete_all_for_session
from backend.app.core.config import UPLOAD_DIR

router = APIRouter()


@router.delete("/reset")
def reset_project(x_session_id: str = Header(default="default")):
    """Clears all uploaded documents FOR THIS SESSION ONLY. This is
    separate from chats now - it does NOT delete any conversation
    history.

    UPGRADED: previously this wiped every user's documents at once
    (both in ChromaDB and on disk). Now it's scoped to X-Session-Id."""

    delete_all_for_session(x_session_id)

    session_upload_dir = os.path.join(UPLOAD_DIR, x_session_id)
    if os.path.isdir(session_upload_dir):
        shutil.rmtree(session_upload_dir)

    return {"message": "Documents cleared"}
