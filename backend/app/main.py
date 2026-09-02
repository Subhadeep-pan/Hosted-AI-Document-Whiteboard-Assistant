from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os

from backend.app.core.auth import verify_api_key
from backend.app.core.config import (
    CORS_ORIGINS,
    UPLOAD_DIR,
)

from backend.app.api.chat import router as chat_router
from backend.app.api.chats import router as chats_router
from backend.app.api.documents import router as documents_router
from backend.app.api.reset import router as reset_router
from backend.app.api.summary import router as summary_router
from backend.app.api.upload import router as upload_router
from backend.app.api.whiteboard import router as whiteboard_router
from backend.app.api.feedback import router as feedback_router
from backend.app.api.memory import router as memory_router
from backend.app.api.gmail_auth import router as gmail_auth_router


# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)


app = FastAPI(title="AI Document Inteligence")


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Protect all API routes
protected = [Depends(verify_api_key)]


for router in (
    upload_router,
    chat_router,
    chats_router,
    reset_router,
    summary_router,
    documents_router,
    feedback_router,
    memory_router,
):
    app.include_router(router, dependencies=protected)


# WebSocket routes can't send the X-API-Key header on the handshake
# the way normal HTTP requests do, so this is registered separately.
app.include_router(whiteboard_router)


# Google's OAuth redirect hits /auth/gmail/callback directly and won't
# carry an X-API-Key header either, so this group is also unprotected.
app.include_router(gmail_auth_router)


@app.get("/")
def home():
    return {
        "message": "AI Resume Assistant API"
    }