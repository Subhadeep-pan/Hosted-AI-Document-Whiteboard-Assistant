"""
Gmail connect/disconnect endpoints. Kept separate from the `protected`
API-key dependency group in main.py, same reasoning as the whiteboard
websocket - /auth/gmail/callback is hit directly by Google's redirect,
which won't carry an X-API-Key header.
"""

from fastapi import APIRouter, Header, Request
from fastapi.responses import RedirectResponse

from backend.app.services.gmail_auth_service import (
    build_auth_url,
    handle_oauth_callback,
    is_connected,
    disconnect,
)

router = APIRouter()


@router.get("/auth/gmail/connect")
def gmail_connect(x_session_id: str = Header(default="default")):
    """Frontend calls this, then redirects the browser to the returned URL."""
    return {"auth_url": build_auth_url(x_session_id)}


@router.get("/auth/gmail/callback")
def gmail_callback(request: Request):
    """Google redirects here after the user approves access. `state`
    is the session_id we passed in build_auth_url."""

    session_id = request.query_params.get("state", "default")
    handle_oauth_callback(session_id, str(request.url))

    # Send the user back to the app once connected.
    return RedirectResponse(url="/")


@router.get("/auth/gmail/status")
def gmail_status(x_session_id: str = Header(default="default")):
    return {"connected": is_connected(x_session_id)}


@router.post("/auth/gmail/disconnect")
def gmail_disconnect(x_session_id: str = Header(default="default")):
    disconnect(x_session_id)
    return {"status": "disconnected"}
