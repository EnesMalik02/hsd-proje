from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class MessageBase(BaseModel):
    text: Optional[str] = None
    type: str = "text" # "text", "image", "location"
    media_url: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: str
    sender_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatListResponse(BaseModel):
    id: str
    participants: List[str]
    listing_id: str
    listing_title: Optional[str] = None
    listing_image: Optional[str] = None
    status: str
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: Dict[str, int] = {}

class ChatStart(BaseModel):
    listing_id: str
