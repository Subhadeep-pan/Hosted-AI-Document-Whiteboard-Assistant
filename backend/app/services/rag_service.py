from backend.app.services.embedding_service import (
    create_query_embedding
)

from backend.app.services.chroma_service import (
    collection
)


def retrieve_context(question, session_id):
    """
    Retrieve relevant document chunks for the current session.
    Uses the shared lazy-loaded embedding model to avoid
    keeping a separate model reference in this service.
    """

    query_embedding = create_query_embedding(
        question
    )

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=5,
        where={
            "session_id": session_id
        },
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