from fastapi import APIRouter, Header

from backend.app.services.summary_service import (
    summarize_document
)

router = APIRouter()


@router.get("/summary")
def get_summary(
        doc_id: str,
        x_session_id: str = Header(default="default"),
):

    summary = summarize_document(
        doc_id,
        x_session_id,
    )

    return {
        "document": doc_id,
        "summary": summary
    }
