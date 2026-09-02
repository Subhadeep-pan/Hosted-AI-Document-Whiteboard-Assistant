"""
ChromaDB document store.

UPGRADED for session isolation: every chunk is now tagged with the
session_id of whoever uploaded it, and every read/write is scoped to
that session_id. Before this change, all uploaded documents lived in
one shared pool visible to every user - this is what actually fixes
that: one Chroma collection, but every query/delete now filters by
session_id via `where`, so it behaves as if each session has its own
private store.

ids are also namespaced with session_id (not just doc_id) so two
different users uploading a file with the same name (e.g. "resume.pdf")
never collide.
"""

import chromadb

from backend.app.core.config import VECTORSTORE_DIR

client = chromadb.PersistentClient(
    path=VECTORSTORE_DIR
)

collection = client.get_or_create_collection(
    name="documents"
)


def store_chunks(chunks, embeddings, doc_id, session_id):
    ids = []
    metadatas = []

    for i in range(len(chunks)):
        ids.append(f"{session_id}_{doc_id}_{i}")
        metadatas.append({
            "doc_id": doc_id,
            "session_id": session_id,
        })

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )


def get_document_ids(session_id):
    """Returns the list of unique document names uploaded by THIS
    session only."""

    results = collection.get(where={"session_id": session_id})

    doc_ids = set()

    for metadata in results.get("metadatas", []):
        if metadata and metadata.get("doc_id"):
            doc_ids.add(metadata["doc_id"])

    return sorted(doc_ids)


def delete_document(doc_id, session_id):
    """Removes one document's chunks - scoped to this session, so a
    user can never delete (or even address) another session's document,
    even if they somehow guessed its doc_id."""

    collection.delete(where={
        "$and": [
            {"doc_id": doc_id},
            {"session_id": session_id},
        ]
    })


def delete_all_for_session(session_id):
    """Used by /reset - clears only this session's documents, not
    everyone's."""

    results = collection.get(where={"session_id": session_id})
    if results["ids"]:
        collection.delete(ids=results["ids"])
