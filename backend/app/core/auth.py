"""
Very small auth check: if API_KEY is set in .env, every request must send
a matching "X-API-Key" header. If API_KEY is left empty, the check is
skipped (useful for local development).
"""

from fastapi import Header, HTTPException
from backend.app.core.config import API_KEY


def verify_api_key(x_api_key: str = Header(default="")):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Missing or invalid API key")
