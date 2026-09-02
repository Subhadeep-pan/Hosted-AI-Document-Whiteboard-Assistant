"""
The "brain" of the assistant - upgraded per the project upgrade plan
into an agentic pipeline with live data, long-term memory, feedback
learning, and answer verification.

Pipeline (Section 11's "agent state" made concrete):
  understand -> retrieve memory -> retrieve documents ->
  decide/fetch live data -> fuse evidence -> generate -> verify ->
  (re-generate once if unsupported) -> store memory -> return

The old fast paths (pure math, "summarize <doc>") are kept as-is at the
top - they're cheap, deterministic, and don't need an LLM planning call,
so there's no reason to route them through the full agentic pipeline.
Redis answer caching (unchanged) still short-circuits repeat questions.
"""

import re

from backend.app.tools.calculator_tool import calculate
from backend.app.tools.email_tool import search_emails
from backend.app.services.rag_service import retrieve_context
from backend.app.services.llm_service import generate_answer
from backend.app.services.chat_memory import add_message, get_history
from backend.app.services.redis_service import redis_client
from backend.app.services.document_finder import find_document
from backend.app.services.summary_service import summarize_document

from backend.app.services import planner_service
from backend.app.services import live_data_service
from backend.app.services import evidence_service
from backend.app.services import verification_service
from backend.app.services import memory_service
from backend.app.services import learning_service

MATH_EXPRESSION = re.compile(r"^[\d\s.()+\-*/]+$")
SUMMARY_KEYWORDS = ["summarize", "summary"]


def _normalize(question):
    text = question.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _build_agent_state(question, session_id, chat_id):
    """The shared structured state every stage below reads from / writes
    into (Section 11 of the plan)."""

    return {
        "question": question,
        "session_id": session_id,
        "chat_id": chat_id,
        "chat_history": None,
        "memory": None,
        "documents": None,
        "live_data": None,
        "tools_used": [],
        "answer": None,
        "sources": [],
        "confidence": None,
    }


def _run_agentic_pipeline(state):
    question = state["question"]

    # 1. Learn a standing preference from this message, if it looks like one.
    learning_service.maybe_learn_preference(state["session_id"], question)

    # 2. Plan: which evidence sources does this question actually need?
    the_plan = planner_service.plan(question)
    state["tools_used"].append("planner")

    # 3. Memory (preferences + similar past interactions).
    if the_plan["needs_memory"]:
        state["memory"] = learning_service.get_learned_context(state["session_id"], question)
        if state["memory"]:
            state["tools_used"].append("memory")

    # 4. Documents.
    document_context = None
    if the_plan["needs_documents"]:
        result = retrieve_context(question, state["session_id"])
        if result["sources"]:
            document_context = result["context"]
            state["sources"] = result["sources"]
            state["documents"] = document_context
            state["tools_used"].append("document_rag")

    # 5. Live data - either the planner asked for it, or documents came
    # up empty for a question that clearly needed *some* evidence.
    live_data_text = None
    if the_plan["needs_live_data"] or (not document_context and not the_plan["needs_memory"]):
        live_result = live_data_service.fetch_live_data(question)
        live_data_text = live_result["text"]
        state["live_data"] = live_data_text
        state["tools_used"].append(live_result["tool_used"])

    # 6. Email - separate from live_data since it's private, per-session
    # data (see email_tool.py), not public web data.
    email_text = None
    if the_plan["needs_email"]:
        email_text = search_emails(state["session_id"], question)
        state["tools_used"].append("email_tool")

    # 7. Fuse evidence.
    evidence = evidence_service.fuse_evidence(
        document_context=document_context,
        live_data_text=live_data_text,
        learned_context=state["memory"],
        email_text=email_text,
    )

    history = get_history(state["session_id"], state["chat_id"])

    prompt = f"""
Previous Conversation:
{history}

Evidence:
{evidence}

Question:
{question}
"""

    answer = generate_answer(prompt)

    # 8. Verify, and regenerate once (with a stricter instruction) if the
    # first answer wasn't well supported by the evidence.
    verification = verification_service.verify_answer(answer, evidence)
    state["confidence"] = verification["confidence"]

    if not verification["supported"]:
        stricter_prompt = prompt + (
            "\n\nImportant: only state facts directly supported by the "
            "evidence above. If the evidence doesn't cover something, "
            "say you're not sure instead of guessing."
        )
        answer = generate_answer(stricter_prompt)
        state["tools_used"].append("verifier_retry")

    if state["sources"]:
        answer += "\n\n Sources:\n"
        for source in state["sources"]:
            answer += f"• {source}\n"

    state["answer"] = answer

    # 9. Store this interaction in semantic memory for future retrieval.
    memory_service.store_interaction(
        state["session_id"], question, answer, sources=state["sources"]
    )

    return state


def _answer_question(question, session_id, chat_id):
    # Fast path 1: pure math expression -> calculator tool, no LLM needed.
    if MATH_EXPRESSION.match(question.strip()):
        return {"answer": calculate(question), "tools_used": ["calculator"], "sources": [], "confidence": "high"}

    # Fast path 2: "summarize my resume.pdf" -> direct document summary.
    if any(word in question.lower() for word in SUMMARY_KEYWORDS):
        doc_id = find_document(question, session_id)
        if doc_id:
            return {
                "answer": summarize_document(doc_id, session_id),
                "tools_used": ["summary_tool"],
                "sources": [doc_id],
                "confidence": "high",
            }

    # Everything else goes through the full agentic pipeline.
    state = _build_agent_state(question, session_id, chat_id)
    state = _run_agentic_pipeline(state)

    return {
        "answer": state["answer"],
        "tools_used": state["tools_used"],
        "sources": state["sources"],
        "confidence": state["confidence"],
    }


def run_agent(question, session_id, chat_id):
    """Returns a dict: {answer, tools_used, sources, confidence}.
    (Upgraded from returning a plain string - see api/chat.py for how
    the extra fields are surfaced to the frontend.)"""

    cache_key = f"answer:{session_id}:{chat_id}:{_normalize(question)}"

    cached_answer = redis_client.get(cache_key)
    if cached_answer:
        return {"answer": cached_answer, "tools_used": ["cache"], "sources": [], "confidence": "high"}

    result = _answer_question(question, session_id, chat_id)

    add_message(session_id, chat_id, "User", question)
    add_message(session_id, chat_id, "Assistant", result["answer"])
    redis_client.set(cache_key, result["answer"])

    return result
