from backend.app.services.chroma_service import (
    collection,
    get_document_ids,
)


def find_document(query, session_id):
    """UPGRADED: only matches against THIS session's own documents."""

    query = query.lower()

    keywords = ["summarize", "summary", "document", "file", "my", "the", "of"]

    for keyword in keywords:
        query = query.replace(keyword, "")

    query = query.strip()

    doc_ids = get_document_ids(session_id)

    for doc_id in doc_ids:
        if query in doc_id.lower():
            return doc_id

    return None


def list_documents(session_id):
    """Looks at what THIS session has stored and returns the real
    list of uploaded documents - no guessing from the LLM needed."""

    doc_ids = get_document_ids(session_id)

    if not doc_ids:
        return "You haven't uploaded any documents yet."

    lines = "\n".join(f"• {doc_id}" for doc_id in doc_ids)
    return f"You have {len(doc_ids)} document(s) uploaded:\n{lines}"
