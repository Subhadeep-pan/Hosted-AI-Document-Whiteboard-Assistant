import logging

from google import genai
from google.genai import types

from backend.app.core.config import GEMINI_API_KEY


logger = logging.getLogger("gemini")

# Shown to the user on any Gemini failure - the real exception is always
# logged server-side (see logger.exception calls below) for debugging,
# but a raw exception string (API keys, quota details, internal error
# codes) should never be shown directly to an end user, and definitely
# shouldn't get saved as a chat title or into long-term memory as if it
# were a real answer.
FRIENDLY_ERROR_MESSAGE = (
    "I'm having trouble reaching the AI service right now. "
    "Please try again in a moment."
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_answer(prompt):
    """
    Generate a normal text answer using Gemini.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        return response.text

    except Exception:
        logger.exception("Gemini call failed")
        return FRIENDLY_ERROR_MESSAGE


def generate_answer_from_image(
    prompt,
    image_bytes,
    mime_type="image/png"
):
    """
    Send a whiteboard image to Gemini and return its response.
    """

    try:
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                prompt,
                image_part,
            ],
        )

        return response.text

    except Exception:
        logger.exception("Gemini vision call failed")
        return FRIENDLY_ERROR_MESSAGE