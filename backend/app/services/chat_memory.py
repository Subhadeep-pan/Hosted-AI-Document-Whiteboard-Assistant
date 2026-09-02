"""
Chat storage in Redis.

Each browser gets a session_id (see frontend api.js). Within a session,
a person can have several separate conversations - just like the chat
list in ChatGPT or Claude - instead of one single never-ending thread.
Each conversation has its own chat_id.

Redis layout:
  chats:{session_id}                    -> hash of {chat_id: json({"title", "created_at"})}
  chat_history:{session_id}:{chat_id}   -> list of "role: message" strings
"""

import json
import time
import uuid
import threading

from backend.app.services.redis_service import redis_client
from backend.app.services.llm_service import generate_answer


def _chats_key(session_id):
    return f"chats:{session_id}"


def _history_key(session_id, chat_id):
    return f"chat_history:{session_id}:{chat_id}"


def create_chat(session_id):
    chat_id = str(uuid.uuid4())

    metadata = {
        "title": "New Chat",
        "created_at": time.time(),
    }

    redis_client.hset(_chats_key(session_id), chat_id, json.dumps(metadata))

    return chat_id


def list_chats(session_id):
    raw_chats = redis_client.hgetall(_chats_key(session_id))

    chats = []

    for chat_id, raw_metadata in raw_chats.items():
        metadata = json.loads(raw_metadata)
        chats.append({
            "chat_id": chat_id,
            "title": metadata["title"],
            "created_at": metadata["created_at"],
        })

    chats.sort(key=lambda chat: chat["created_at"], reverse=True)

    return chats


def delete_chat(session_id, chat_id):
    redis_client.hdel(_chats_key(session_id), chat_id)
    redis_client.delete(_history_key(session_id, chat_id))


def rename_chat(session_id, chat_id, new_title):
    """Lets the user manually rename a chat, e.g. with a pencil icon."""

    raw_metadata = redis_client.hget(_chats_key(session_id), chat_id)
    if not raw_metadata:
        return

    metadata = json.loads(raw_metadata)
    metadata["title"] = new_title[:40]
    redis_client.hset(_chats_key(session_id), chat_id, json.dumps(metadata))


def get_chat_title(session_id, chat_id):
    """Just reads the current title for one chat - used to send the
    freshly auto-generated title back to the frontend after a message."""

    raw_metadata = redis_client.hget(_chats_key(session_id), chat_id)
    if not raw_metadata:
        return "New Chat"

    return json.loads(raw_metadata)["title"]


def _make_short_title(question):
    """Asks Gemini for a short 3-4 word title, like ChatGPT does.
    Falls back to the raw question if Gemini fails for any reason."""

    prompt = (
        "Write a short 3 to 4 word title for a chat that starts with "
        "this message. Reply with ONLY the title, no quotes, no punctuation.\n\n"
        f"Message: {question}"
    )

    title = generate_answer(prompt).strip()

    # Safety net: if Gemini gives back something too long or empty,
    # just use the first few words of the question instead.
    if not title or len(title) > 60:
        title = question[:40]

    return title


def _set_title_from_first_message(session_id, chat_id, question):
    """The first question a user asks becomes the chat's title in the
    sidebar, same as ChatGPT/Claude do.

    UPGRADED: this used to call Gemini and write the result SYNCHRONOUSLY,
    inside the same request that's also answering the user's actual
    question - meaning every first message in a new chat paid for a
    second, full round-trip Gemini call before the user saw anything at
    all. That's a real, measurable slowdown, not just a minor delay.
    Title generation now runs in a background thread instead: the
    answer streams back immediately, and the sidebar picks up the title
    a moment later (the frontend re-checks shortly after each answer
    finishes - see useChats.js / App.jsx)."""

    raw_metadata = redis_client.hget(_chats_key(session_id), chat_id)
    if not raw_metadata:
        return

    metadata = json.loads(raw_metadata)

    if metadata["title"] != "New Chat":
        return

    def _generate_and_save():
        title = _make_short_title(question)

        # Re-read rather than reuse the outer `metadata` - some time has
        # passed on a background thread, so read the current value to
        # avoid clobbering a manual rename that happened in the meantime.
        current_raw = redis_client.hget(_chats_key(session_id), chat_id)
        if not current_raw:
            return

        current_metadata = json.loads(current_raw)
        if current_metadata["title"] != "New Chat":
            return  # user (or a race) already set a real title - don't overwrite it

        current_metadata["title"] = title
        redis_client.hset(_chats_key(session_id), chat_id, json.dumps(current_metadata))

    threading.Thread(target=_generate_and_save, daemon=True).start()


def add_message(session_id, chat_id, role, content):
    redis_client.rpush(_history_key(session_id, chat_id), f"{role}: {content}")

    if role == "User":
        _set_title_from_first_message(session_id, chat_id, content)


def get_history(session_id, chat_id):
    messages = redis_client.lrange(_history_key(session_id, chat_id), 0, -1)
    return "\n".join(messages)


def get_history_list(session_id, chat_id):
    """Returns history as a list of {role, text} dicts, for the frontend
    to rehydrate the chat window after a page refresh."""

    messages = redis_client.lrange(_history_key(session_id, chat_id), 0, -1)

    history = []

    for message in messages:
        role, _, text = message.partition(": ")
        history.append({"role": role, "text": text})

    return history