"""
Feedback-driven learning (Sections 5 and 6 of the upgrade plan).

This is the "self-learning" layer. It does NOT retrain Gemini. It:
  1. Detects explicit preference statements ("keep answers short") and
     stores them via memory_service so future prompts respect them.
  2. Records 👍/👎 feedback on answers.
  3. Surfaces past similar interactions as learned examples.

Interview-accurate framing (section 17): "The agent improves future
responses by learning from user feedback, interaction history,
preferences, and successful retrieval patterns through a persistent
semantic memory layer - not by continuously retraining the model."
"""

import re

from backend.app.services.llm_service import generate_answer
from backend.app.services import memory_service

PREFERENCE_TRIGGERS = [
    "don't give me", "dont give me", "keep it short", "keep answers",
    "be concise", "be brief", "explain simply", "use simple",
    "always", "from now on", "in the future", "prefer",
]


def maybe_learn_preference(session_id, question):
    """Cheap heuristic: if the message sounds like a standing
    instruction rather than a one-off question, ask Gemini to turn it
    into a short preference key/value and store it.

    This deliberately only fires on phrasing that looks like an
    instruction (see PREFERENCE_TRIGGERS) so ordinary questions don't
    get misread as preferences.
    """

    lowered = question.lower()

    if not any(trigger in lowered for trigger in PREFERENCE_TRIGGERS):
        return None

    prompt = f"""
A user said this to an AI assistant: "{question}"

If this is a standing preference/instruction about how the assistant
should behave in future answers (e.g. tone, length, style, language),
reply with ONLY a compact "key: value" pair, like:
response_style: concise

If it is NOT a preference/instruction (just a normal question), reply
with exactly: NONE
"""

    result = generate_answer(prompt).strip()

    if result.upper() == "NONE" or ":" not in result:
        return None

    key, _, value = result.partition(":")
    key = re.sub(r"[^a-z_]", "", key.strip().lower().replace(" ", "_"))
    value = value.strip()

    if not key or not value:
        return None

    memory_service.set_preference(session_id, key, value)
    return {key: value}


def get_learned_context(session_id, question):
    """Combines preference memory + similar past interactions into one
    block of text to inject into the generation prompt."""

    preferences_text = memory_service.get_preferences_text(session_id)
    similar = memory_service.retrieve_similar_interactions(session_id, question)

    parts = []

    if preferences_text:
        parts.append(preferences_text)

    if similar:
        examples = "\n\n".join(
            f"Q: {item['question']}\nA: {item['answer']}" for item in similar
        )
        parts.append(f"Similar past interactions that worked well:\n{examples}")

    return "\n\n".join(parts)


def submit_feedback(session_id, question, answer, helpful, correction=None):
    memory_service.record_feedback(session_id, question, answer, helpful, correction)
