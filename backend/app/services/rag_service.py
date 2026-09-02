from backend.app.services.embedding_service import model

from backend.app.services.chroma_service import (
    collection
)


def retrieve_context(question, session_id):
    """UPGRADED: query is now scoped to session_id via `where`, so
    retrieval only ever searches documents THIS session uploaded -
    never another user's."""

    query_embedding = model.encode(
        question
    )

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=5,
        where={"session_id": session_id},
    )

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    context = "\n".join(
        documents
    )

    sources = []

    for metadata in metadatas:

        if metadata is None:
            continue

        doc_id = metadata.get(
            "doc_id"
        )

        if (
            doc_id
            and doc_id not in sources
        ):

            sources.append(
                doc_id
            )

    return {
        "context": context,
        "sources": sources
    }
