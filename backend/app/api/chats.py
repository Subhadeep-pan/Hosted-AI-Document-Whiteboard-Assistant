from fastapi import APIRouter, Header
from pydantic import BaseModel

from backend.app.services.chat_memory import (
    create_chat,
    delete_chat,
    get_history_list,
    list_chats,
    rename_chat,
)

router = APIRouter()


class RenameRequest(BaseModel):
    title: str


@router.get("/chats")
def get_chats(x_session_id: str = Header(default="default")):
    return {"chats": list_chats(x_session_id)}


@router.post("/chats")
def create_new_chat(x_session_id: str = Header(default="default")):
    return {
        "chat_id": create_chat(x_session_id)
    }


@router.delete("/chats/{chat_id}")
def delete_chat_route(
    chat_id: str,
    x_session_id: str = Header(default="default"),
):
    delete_chat(x_session_id, chat_id)
    return {"message": "Chat deleted"}


@router.patch("/chats/{chat_id}")
def rename_chat_route(
    chat_id: str,
    request: RenameRequest,
    x_session_id: str = Header(default="default"),
):
    rename_chat(
        x_session_id,
        chat_id,
        request.title,
    )

    return {"message": "Chat renamed"}


@router.get("/history")
def get_chat_history(
    chat_id: str,
    x_session_id: str = Header(default="default"),
):
    return {
        "history": get_history_list(
            x_session_id,
            chat_id,
        )
    }