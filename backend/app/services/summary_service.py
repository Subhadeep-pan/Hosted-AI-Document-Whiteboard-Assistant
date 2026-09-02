from backend.app.services.chroma_service import (
    collection
)

from backend.app.services.llm_service import (
    generate_answer
)


def summarize_document(doc_id, session_id):
    """UPGRADED: scoped so a session can only summarize its own
    document - matching on doc_id alone let any session's guessed
    filename pull back another user's content."""

    results = collection.get(
        where={
            "$and": [
                {"doc_id": doc_id},
                {"session_id": session_id},
            ]
        }
    )

    documents = results.get(
        "documents",
        []
    )

    if not documents:

        return (
            f"Document '{doc_id}' not found."
        )

    text = "\n".join(
        documents
    )

    prompt = f"""
Summarize the following document.

Document:
{text}

Provide:

1. Overview
2. Key Points
3. Important Technologies
4. Final Summary
"""

    return generate_answer(
        prompt
    )
