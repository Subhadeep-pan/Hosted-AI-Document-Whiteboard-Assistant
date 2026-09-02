"""
Answer verification (Section 12 of the upgrade plan).

After Gemini generates an answer, ask it (as a separate, narrower call)
whether the answer is actually supported by the evidence it was given.
This is a practical, cheap way to catch unsupported claims/hallucinations
before they reach the user - not a guarantee, but a real check.
"""

import json
import re

from backend.app.services.llm_service import generate_answer

VERIFY_PROMPT = """You are checking an AI assistant's answer for hallucinations.

Evidence given to the assistant:
{evidence}

Assistant's answer:
{answer}

Is the answer adequately supported by the evidence? Reply with ONLY
JSON in this shape:
{{"supported": true/false, "confidence": "high"/"medium"/"low", "notes": "short note"}}
"""


def verify_answer(answer, evidence):
    if not evidence:
        # Nothing to check the answer against (e.g. pure calculator
        # result) - treat as supported by definition.
        return {"supported": True, "confidence": "high", "notes": "no evidence needed"}

    raw = generate_answer(VERIFY_PROMPT.format(evidence=evidence[:6000], answer=answer))

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"supported": True, "confidence": "medium", "notes": "verifier output unparsable"}

    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"supported": True, "confidence": "medium", "notes": "verifier output invalid"}

    return {
        "supported": bool(parsed.get("supported", True)),
        "confidence": parsed.get("confidence", "medium"),
        "notes": parsed.get("notes", ""),
    }
