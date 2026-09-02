"""
Whiteboard room state, stored in Redis so a late-joiner (or a page
refresh) can rehydrate the board instead of starting blank.

Redis layout:
  whiteboard:{room_id}:elements  -> hash of {element_id: json(element)}

We use a hash (not a single JSON blob) so that adding/updating/deleting
one element is a single Redis call instead of read-modify-write on the
whole board — that matters once two people are drawing at once.
"""

import json

from backend.app.services.redis_service import redis_client

ROOM_TTL_SECONDS = 60 * 60 * 24 * 7  # rooms expire after 7 days of inactivity


def _elements_key(room_id):
    return f"whiteboard:{room_id}:elements"


def upsert_element(room_id, element):
    """element is a dict and MUST contain an 'id' field."""
    key = _elements_key(room_id)
    redis_client.hset(key, element["id"], json.dumps(element))
    redis_client.expire(key, ROOM_TTL_SECONDS)


def delete_element(room_id, element_id):
    redis_client.hdel(_elements_key(room_id), element_id)


def clear_board(room_id):
    redis_client.delete(_elements_key(room_id))


def get_board_state(room_id):
    """Returns the current list of elements, e.g. to send to a client
    that just joined the room."""
    raw = redis_client.hgetall(_elements_key(room_id))
    return [json.loads(value) for value in raw.values()]


# ---- Variable memory (Run button's dictOfVars) -------------------------
#
# When someone assigns a variable (e.g. drawing "x = 4" and clicking
# Run), it's stored here so later Runs - by ANYONE in the room, not just
# the person who assigned it - can reference it. The frontend already
# sends/expects "var_update" messages and a "vars" field on join; this
# was previously missing here, so those messages were silently ignored.

def _vars_key(room_id):
    return f"whiteboard:{room_id}:vars"


def get_vars(room_id):
    return redis_client.hgetall(_vars_key(room_id))


def set_var(room_id, name, value):
    key = _vars_key(room_id)
    redis_client.hset(key, name, value)
    redis_client.expire(key, ROOM_TTL_SECONDS)
