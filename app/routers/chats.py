from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.chat import ChatListResponse, MessageResponse, MessageCreate
from app.services.chat_service import chat_service
from app.core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ChatListResponse])
def get_my_chats(current_user: dict = Depends(get_current_user)):
    return chat_service.get_chats(current_user['uid'])

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
def get_chat_messages(chat_id: str, current_user: dict = Depends(get_current_user)):
    try:
        msgs = chat_service.get_messages(chat_id, current_user['uid'])
        if msgs is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        return msgs
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.post("/{chat_id}/messages", response_model=MessageResponse)
def send_message(chat_id: str, message: MessageCreate, current_user: dict = Depends(get_current_user)):
    try:
        return chat_service.send_message(chat_id, message, current_user['uid'])
    except ValueError:
        raise HTTPException(status_code=404, detail="Chat not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")
