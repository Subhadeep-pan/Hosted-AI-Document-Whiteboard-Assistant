"""
Gmail OAuth2 flow + per-session credential storage.

There's no real user-login system in this project yet (just an
anonymous session_id - see chat_memory.py), so credentials are stored
in Redis keyed by session_id, the same way chat history and
preferences already are. That's fine for a single-user demo/dev setup;
if this ever becomes multi-tenant with real accounts, swap the storage
key from session_id to a real user_id - nothing else here would need
to change.

Read-only scope only (gmail.readonly): this can search/read email, it
can never send or delete anything.
"""

import json

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from backend.app.core.config import (
    GMAIL_CLIENT_ID,
    GMAIL_CLIENT_SECRET,
    GMAIL_REDIRECT_URI,
)
from backend.app.services.redis_service import redis_client

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _client_config():
    return {
        "web": {
            "client_id": GMAIL_CLIENT_ID,
            "client_secret": GMAIL_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [GMAIL_REDIRECT_URI],
        }
    }


def _credentials_key(session_id):
    return f"gmail_credentials:{session_id}"


def build_auth_url(session_id):
    """Returns the Google consent-screen URL to redirect the user to.
    `state` carries the session_id through the OAuth round trip so the
    callback knows whose credentials it just received."""

    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, redirect_uri=GMAIL_REDIRECT_URI)

    auth_url, _ = flow.authorization_url(
        access_type="offline",       # needed to get a refresh_token
        include_granted_scopes="true",
        prompt="consent",
        state=session_id,
    )

    return auth_url


def handle_oauth_callback(session_id, authorization_response_url):
    """Exchanges the code Google sent back for tokens, and stores them
    in Redis against this session_id."""

    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, redirect_uri=GMAIL_REDIRECT_URI)
    flow.fetch_token(authorization_response=authorization_response_url)

    credentials = flow.credentials

    redis_client.set(_credentials_key(session_id), credentials.to_json())


def get_credentials(session_id):
    """Loads stored credentials for this session, refreshing the access
    token if it's expired. Returns None if the user never connected
    Gmail (or the connection was reset)."""

    raw = redis_client.get(_credentials_key(session_id))
    if not raw:
        return None

    credentials = Credentials.from_authorized_user_info(json.loads(raw), SCOPES)

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        redis_client.set(_credentials_key(session_id), credentials.to_json())

    return credentials


def is_connected(session_id):
    return get_credentials(session_id) is not None


def disconnect(session_id):
    redis_client.delete(_credentials_key(session_id))
