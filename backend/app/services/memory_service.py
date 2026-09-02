"""
Long-term memory layer (Section 7 of the upgrade plan).

Three kinds of memory live here, on top of the short-term memory that
already exists in chat_memory.py:

1. Semantic memory   - a separate ChromaDB collection ("agent_memory")
                        of past question/answer pairs, so a similar
                        question later can retrieve what worked before.
2. Preference memory  - simple per-session key/values in Redis
                        (e.g. response_style=concise).
3. Feedback memory    - a Redis list of 👍/👎 records per session, used
                        by learning_service.py.

This intentionally does NOT retrain or fine-tune the Gemini model. It
just gives the agent something persistent to retrieve from, which is
what section 17 of the plan calls a "self-learning / adaptive agent"
rather than continuous foundation-model retraining.
"""

import json
import time
import uuid

from backend.app.services.embedding_service import model
from backend.app.services.redis_service import redis_client
from backend.app.services.chroma_service import client as _chroma_client

memory_collection = _chroma_client.get_or_create_collection(name="agent_memory")


# ---- Semantic (episodic) memory -------------------------------------

def store_interaction(session_id, question, answer, sources=None, helpful=None):
    """Saves a question/answer pair into the semantic memory store so a
    similar future question can retrieve it as a worked example."""

    embedding = model.encode(question)

    memory_id = str(uuid.uuid4())

    memory_collection.add(
        ids=[memory_id],
        embeddings=[embedding.tolist()],
        documents=[question],
        metadatas=[{
            "session_id": session_id,
            "answer": answer[:2000],
            "sources": json.dumps(sources or []),
            "helpful": helpful if helpful is not None else "unknown",
            "created_at": time.time(),
        }],
    )

    return memory_id


def retrieve_similar_interactions(session_id, question, n_results=3):
    """Returns past Q&A pairs (for this session) similar to the current
    question, to use as few-shot context / learned examples."""

    embedding = model.encode(question)

    results = memory_collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=n_results,
        where={"session_id": session_id},
    )

    memories = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    for past_question, metadata in zip(documents, metadatas):
        # Skip past interactions that were explicitly marked unhelpful -
        # no point reinforcing an answer the user already rejected.
        if metadata.get("helpful") == False or metadata.get("helpful") == "false":
            continue

        memories.append({
            "question": past_question,
            "answer": metadata.get("answer", ""),
        })

    return memories


# ---- Preference memory ------------------------------------------------

def _preferences_key(session_id):
    return f"preferences:{session_id}"


def set_preference(session_id, key, value):
    redis_client.hset(_preferences_key(session_id), key, value)


def get_preferences(session_id):
    return redis_client.hgetall(_preferences_key(session_id))


def get_preferences_text(session_id):
    """Renders stored preferences as a short instruction block to inject
    into the prompt, e.g. 'response_style: concise'."""

    preferences = get_preferences(session_id)

    if not preferences:
        return ""

    lines = [f"- {key}: {value}" for key, value in preferences.items()]
    return "User preferences (apply these to your answer):\n" + "\n".join(lines)


# ---- Feedback memory ---------------------------------------------------

def _feedback_key(session_id):
    return f"feedback:{session_id}"


def record_feedback(session_id, question, answer, helpful, correction=None):
    entry = {
        "question": question,
        "answer": answer[:2000],
        "helpful": helpful,
        "correction": correction,
        "created_at": time.time(),
    }
    redis_client.rpush(_feedback_key(session_id), json.dumps(entry))

    # Also tag the matching semantic memory (if we can find it) so future
    # retrieval knows this interaction was good or bad.
    _tag_semantic_memory_feedback(session_id, question, helpful)


def _tag_semantic_memory_feedback(session_id, question, helpful):
    embedding = model.encode(question)

    results = memory_collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=1,
        where={"session_id": session_id},
    )

    ids = results.get("ids", [[]])[0]
    if not ids:
        return

    memory_collection.update(
        ids=[ids[0]],
        metadatas=[{"helpful": helpful}],
    )


def get_feedback_history(session_id):
    raw = redis_client.lrange(_feedback_key(session_id), 0, -1)
    return [json.loads(item) for item in raw]
