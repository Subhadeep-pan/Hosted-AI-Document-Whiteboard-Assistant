"""
All configuration lives here, loaded from environment variables (.env file).
This is the ONLY place that should read os.getenv() - every other file
imports the values it needs from here. That way, nothing is hardcoded
and the whole app can be reconfigured just by editing the .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Every path below is resolved relative to the project root (two levels
# up from backend/app/core/), NOT relative to whatever directory the
# server happens to be launched from. This matters for deployment: a
# process manager (systemd, gunicorn, Docker, etc) often starts the app
# from a different working directory than a developer's terminal, and a
# relative path like "backend/.env" silently loads nothing (no error!)
# the moment that assumption breaks.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_BACKEND_DIR = _PROJECT_ROOT / "backend"

load_dotenv(_BACKEND_DIR / ".env")

# --- API keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

if not GEMINI_API_KEY:
    print(f"WARNING: GEMINI_API_KEY is not set. Looked for it in: {_BACKEND_DIR / '.env'}")

# --- Simple app auth ---
# If left empty, the API runs "open" (fine for local dev).
# Set API_KEY in .env to require an "X-API-Key" header on every request.
API_KEY = os.getenv("API_KEY", "")

# --- CORS ---
# Comma separated list, e.g. "http://localhost:5173,https://myapp.com"
# In production, set this to your real deployed frontend URL(s) - do
# NOT leave it defaulting to localhost.
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# --- Redis ---
# REDIS_URL takes priority if set - this is what hosted Redis providers
# (Render's managed Redis, Upstash, etc) give you: a single URL with
# auth + TLS baked in, e.g. "rediss://default:password@host:6379".
# REDIS_HOST/REDIS_PORT remain as the simple local-dev fallback (plain,
# unauthenticated, e.g. `docker run redis` or a local install).
REDIS_URL = os.getenv("REDIS_URL", "")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# --- Storage ---
# Absolute by default (see note above); still overridable via env var
# for deployments that mount a persistent disk at a specific path.
# Uses `or` (not getenv's default arg) so a blank value in .env - e.g.
# copied straight from .env.example - still falls through to the
# computed default instead of resolving to an empty/invalid path.
UPLOAD_DIR = os.getenv("UPLOAD_DIR") or str(_BACKEND_DIR / "uploads" / "pdfs")
VECTORSTORE_DIR = os.getenv("VECTORSTORE_DIR") or str(_BACKEND_DIR / "app" / "vectorstore" / "chroma_db")

# --- OCR ---
# Only needed on Windows if Tesseract isn't on PATH.
# Leave empty on Linux/Mac - pytesseract will just use the "tesseract" command.
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")

# --- Rate limiting ---
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "20"))

# --- Gmail OAuth (email tool) ---
# Create these in Google Cloud Console: APIs & Services > Credentials >
# OAuth client ID (type "Web application"). Add GMAIL_REDIRECT_URI as an
# authorized redirect URI there too, and enable the Gmail API for the
# project. Scope used is read-only (gmail.readonly) - this tool can
# search/read email, it never sends or deletes anything.
GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET", "")
GMAIL_REDIRECT_URI = os.getenv("GMAIL_REDIRECT_URI", "http://127.0.0.1:8000/auth/gmail/callback")
