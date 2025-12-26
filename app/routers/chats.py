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

@router.get("/{chat_id}/messages/{message_id}/walrus-info")
def get_message_walrus_info(chat_id: str, message_id: str, current_user: dict = Depends(get_current_user)):
    """Get Walrus blockchain information for a specific message."""
    try:
        from app.core.config import settings, get_db
        from app.services.walrus_service import get_walrus_service
        
        # Verify user has access to this chat
        db = get_db()
        chat_ref = db.collection('chats').document(chat_id)
        chat = chat_ref.get()
        
        if not chat.exists:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        if current_user['uid'] not in chat.get('participants'):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get message
        msg_ref = chat_ref.collection('messages').document(message_id)
        msg = msg_ref.get()
        
        if not msg.exists:
            raise HTTPException(status_code=404, detail="Message not found")
        
        msg_data = msg.to_dict()
        blob_id = msg_data.get('walrus_blob_id')
        
        if not blob_id:
            return {
                "message_id": message_id,
                "walrus_enabled": settings.WALRUS_ENABLED,
                "stored_on_walrus": False,
                "storage_type": msg_data.get('storage_type', 'firestore')
            }
        
        # Get Walrus info
        walrus = get_walrus_service()
        if walrus:
            blob_info = walrus.get_blob_info(blob_id)
            return {
                "message_id": message_id,
                "walrus_enabled": settings.WALRUS_ENABLED,
                "stored_on_walrus": True,
                "storage_type": msg_data.get('storage_type', 'hybrid'),
                "blob_id": blob_id,
                "blob_info": blob_info,
                "aggregator_url": f"{settings.WALRUS_AGGREGATOR_URL}/v1/{blob_id}"
            }
        
        return {
            "message_id": message_id,
            "walrus_enabled": False,
            "stored_on_walrus": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
