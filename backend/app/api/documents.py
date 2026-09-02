"""
Lets the frontend see which documents are uploaded (so the list survives
a page refresh) and delete just one of them, without wiping everything
like "Reset Documents" does.

UPGRADED: both endpoints are now scoped to X-Session-Id, so a session
only ever sees or deletes its own documents.
"""

from fastapi import APIRouter, Header

from backend.app.services.chroma_service import get_document_ids, delete_document

router = APIRouter()


@router.get("/documents")
def get_documents(x_session_id: str = Header(default="default")):
    return {"documents": get_document_ids(x_session_id)}


@router.delete("/documents/{doc_id}")
def remove_document(doc_id: str, x_session_id: str = Header(default="default")):
    delete_document(doc_id, x_session_id)
    return {"message": "Document deleted"}
