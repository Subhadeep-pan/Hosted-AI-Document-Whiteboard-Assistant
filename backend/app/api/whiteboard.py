"""
Real-time collaborative whiteboard.

Any number of users can join the same room_id.

Each connected client receives drawing events from other
clients through the WebSocket room.

Redis stores the persistent whiteboard state.
"""

import json
import base64

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from backend.app.services.whiteboard_service import (
    upsert_element,
    delete_element,
    clear_board,
    get_board_state,
    get_vars,
    set_var,
)

from backend.app.services.llm_service import (
    generate_answer_from_image,
)


router = APIRouter()


SOLVE_PROMPT = """
You are looking at an image of a handwritten mathematical
whiteboard.

Read the mathematical expression or problem.

Solve it.

Return ONLY valid JSON.

The JSON must have exactly this structure:

{
    "results": [
        {
            "expr": "the expression you read",
            "result": "the answer",
            "latex": "LaTeX representation of the equation and answer",
            "assign": false
        }
    ]
}

Rules:

1. If there is one equation, return one item.
2. If there are multiple equations, return multiple items.
3. "expr" must contain what you read from the whiteboard.
4. "result" must contain the calculated answer.
5. "latex" must contain a clean LaTeX representation.
6. "assign" should normally be false.
7. If the expression is a variable assignment such as x = 5,
   use:
   "assign": true
   "expr": "x"
   "result": "5"
8. Do not use Markdown.
9. Do not put the JSON inside ```json blocks.
10. Return only the JSON object.

If there is no mathematical problem, return:

{
    "results": []
}
"""


class RoomManager:
    """
    Tracks WebSocket connections for each whiteboard room.
    """

    def __init__(self):
        # room_id -> {websocket: user_name}
        self.rooms: dict[str, dict[WebSocket, str]] = {}

    async def join(
        self,
        room_id,
        websocket: WebSocket,
        user_name: str
    ):
        await websocket.accept()

        self.rooms.setdefault(
            room_id,
            {}
        )[websocket] = user_name

        await self.broadcast_presence(room_id)

    def leave(
        self,
        room_id,
        websocket: WebSocket
    ):
        room = self.rooms.get(room_id)

        if not room:
            return

        room.pop(websocket, None)

        if not room:
            self.rooms.pop(room_id, None)

    def users_in_room(self, room_id):
        return list(
            self.rooms.get(room_id, {}).values()
        )

    async def broadcast(
        self,
        room_id,
        message: dict,
        exclude: WebSocket = None
    ):
        """
        Send a message to every connected client
        except the sender.
        """

        room = self.rooms.get(
            room_id,
            {}
        )

        dead = []

        for websocket in room:

            if websocket is exclude:
                continue

            try:
                await websocket.send_json(
                    message
                )

            except Exception:
                dead.append(websocket)

        for websocket in dead:
            self.leave(
                room_id,
                websocket
            )

    async def broadcast_presence(
        self,
        room_id
    ):
        await self.broadcast(
            room_id,
            {
                "type": "presence",
                "users": self.users_in_room(room_id),
            },
        )


manager = RoomManager()


class SolveRequest(BaseModel):
    image_base64: str


@router.post("/whiteboard/solve")
def solve_from_whiteboard(
    payload: SolveRequest
):
    """
    Takes a snapshot of the whiteboard,
    sends it to Gemini Vision,
    and returns structured results.
    """

    try:
        raw = payload.image_base64

        # Remove data URL prefix if present.
        if "," in raw and raw.strip().startswith("data:"):
            raw = raw.split(",", 1)[1]

        # Decode base64 image.
        image_bytes = base64.b64decode(raw)

        # Ask Gemini to solve the whiteboard.
        gemini_result = generate_answer_from_image(
            SOLVE_PROMPT,
            image_bytes,
            "image/png",
        )

        # Gemini should return JSON.
        try:
            parsed = json.loads(gemini_result)

        except json.JSONDecodeError:

            # Sometimes models still return Markdown
            # despite being told not to.
            cleaned = gemini_result.strip()

            if cleaned.startswith("```"):
                cleaned = cleaned.replace(
                    "```json",
                    ""
                )

                cleaned = cleaned.replace(
                    "```",
                    ""
                )

                cleaned = cleaned.strip()

            parsed = json.loads(cleaned)

        # Make sure frontend always receives results.
        if not isinstance(parsed, dict):
            return {
                "results": []
            }

        results = parsed.get(
            "results",
            []
        )

        if not isinstance(results, list):
            results = []

        return {
            "results": results
        }

    except Exception as e:

        print(
            "Whiteboard solve failed:",
            repr(e)
        )

        return {
            "results": [],
            "error": str(e)
        }


@router.websocket(
    "/ws/whiteboard/{room_id}"
)
async def whiteboard_room(
    websocket: WebSocket,
    room_id: str,
    user_name: str = "Guest"
):
    await manager.join(
        room_id,
        websocket,
        user_name
    )

    # UPGRADED (fixes "can't leave the whiteboard" / ghost users still
    # showing as present after they left): everything from here on is
    # now wrapped in try/finally, so `manager.leave()` is GUARANTEED to
    # run no matter how this connection ends - a clean disconnect, an
    # error reading a message, or (the actual bug) an exception raised
    # while sending the initial board state, e.g. a momentary Redis
    # hiccup. Previously, manager.leave() was only called from inside
    # the except WebSocketDisconnect block below, which meant any
    # failure BEFORE that point (including the very next two lines)
    # left the connection stuck in the room's user list forever, with
    # no way for that user - or anyone else in the room - to ever see
    # them as "left".
    try:
        # Send the existing board to the new client.
        await websocket.send_json(
            {
                "type": "init",
                "elements": get_board_state(
                    room_id
                ),
                "users": manager.users_in_room(
                    room_id
                ),
                "vars": get_vars(room_id),
            }
        )

        while True:

            raw = await websocket.receive_text()

            message = json.loads(raw)

            msg_type = message.get(
                "type"
            )

            if (
                msg_type == "element_add"
                or msg_type == "element_update"
            ):

                element = message["element"]

                upsert_element(
                    room_id,
                    element
                )

                await manager.broadcast(
                    room_id,
                    message,
                    exclude=websocket
                )

            elif msg_type == "element_delete":

                delete_element(
                    room_id,
                    message["element_id"]
                )

                await manager.broadcast(
                    room_id,
                    message,
                    exclude=websocket
                )

            elif msg_type == "clear":

                clear_board(
                    room_id
                )

                await manager.broadcast(
                    room_id,
                    message,
                    exclude=websocket
                )

            elif msg_type == "cursor":

                message["user"] = (
                    manager.rooms[room_id]
                    .get(websocket)
                )

                await manager.broadcast(
                    room_id,
                    message,
                    exclude=websocket
                )

            elif msg_type == "var_update":
                # A Run on someone's client assigned a variable (e.g.
                # "x = 4") - store it so everyone's next Run can use it.
                set_var(room_id, message["name"], message["value"])
                await manager.broadcast(room_id, message, exclude=websocket)

    except WebSocketDisconnect:
        # The normal, expected way a connection ends - browser tab
        # closed, navigated away, network dropped.
        pass

    except Exception as e:
        # Anything else (e.g. a malformed message, a transient Redis
        # error) - log it, but still fall through to `finally` below so
        # the user is removed from the room instead of becoming a ghost.
        print(f"Whiteboard connection for room {room_id} ended with an error: {e!r}")

    finally:
        manager.leave(
            room_id,
            websocket
        )

        await manager.broadcast_presence(
            room_id
        )