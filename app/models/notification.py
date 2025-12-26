from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    recipient_id: str
    type: str # "request_received", "request_approved", "new_message"
    title: str
    body: str
    related_item_id: Optional[str] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: str
    is_read: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
