"""
Agentic planner (Sections 8-11 of the upgrade plan).

Replaces pure keyword-matching with an LLM decision: given the
question (and a hint of what's in the docs / recent history), decide
which evidence sources are actually needed - documents, live data,
memory, or some combination. This is what turns simple routing into
"agent-driven tool selection" instead of if/elif on keywords.

Falls back to a conservative default (try documents first) if Gemini's
response can't be parsed, so a bad LLM response never crashes the
pipeline - it just behaves like the old router did.
"""

import json
import re

from backend.app.services.llm_service import generate_answer

PLANNER_PROMPT = """You are the planning step of a document-assistant agent.
Given the user's question, decide which evidence sources are needed to
answer it well.

Question: "{question}"

Reply with ONLY a JSON object, no other text, in exactly this shape:
{{"needs_documents": true/false, "needs_live_data": true/false, "needs_memory": true/false, "needs_email": true/false, "reason": "short reason"}}

Guidance:
- needs_documents: true if the question could be about the user's own uploaded files.
- needs_live_data: true if it needs current/real-world/external info (news, prices, weather, "current" facts, anything not likely to be in a personal document).
- needs_memory: true if it references past conversation, preferences, or "what I asked before".
- needs_email: true if it asks about the user's own inbox/emails (e.g. "did I get a reply from...", "find the email about...", "when did X email me").
- A question can need more than one source at once.
"""


def _fallback_plan():
    return {
        "needs_documents": True,
        "needs_live_data": False,
        "needs_memory": True,
        "needs_email": False,
        "reason": "fallback - could not parse planner output",
    }


def plan(question):
    raw = generate_answer(PLANNER_PROMPT.format(question=question))

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return _fallback_plan()

    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return _fallback_plan()

    return {
        "needs_documents": bool(parsed.get("needs_documents", True)),
        "needs_live_data": bool(parsed.get("needs_live_data", False)),
        "needs_memory": bool(parsed.get("needs_memory", True)),
        "needs_email": bool(parsed.get("needs_email", False)),
        "reason": parsed.get("reason", ""),
    }
