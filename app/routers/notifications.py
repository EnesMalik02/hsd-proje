from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.notification import NotificationResponse
from app.services.notification_service import notification_service
from app.core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def get_my_notifications(current_user: dict = Depends(get_current_user)):
    return notification_service.get_notifications(current_user['uid'])

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    try:
        updated = notification_service.mark_as_read(notification_id, current_user['uid'])
        if not updated:
            raise HTTPException(status_code=404, detail="Notification not found")
        return updated
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")
