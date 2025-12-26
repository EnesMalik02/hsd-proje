from fastapi import APIRouter, Depends, HTTPException
from app.models.user import UserResponse, UserCreate, UserUpdate
from app.services.user_service import user_service
from app.core.security import get_current_user

router = APIRouter()

@router.post("/me", response_model=UserResponse)
def create_or_update_me(user_in: UserCreate, current_user: dict = Depends(get_current_user)):
    """
    Create or update the current user's profile.
    Client checks if user exists in Firestore, if not call this.
    Or we can upsert.
    """
    if current_user['uid'] != user_in.uid:
        raise HTTPException(status_code=403, detail="UID mismatch")
    
    existing = user_service.get_user(user_in.uid)
    if existing:
        # If exists, we might treat this as an update or simple return
        # But let's assume this endpoint is primarily for initial creation if it doesn't exist
        # Or full profile sync
        return existing
    
    return user_service.create_user(user_in)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    uid = current_user['uid']
    user = user_service.get_user(uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{uid}", response_model=UserResponse)
def get_user(uid: str, current_user: dict = Depends(get_current_user)):
    user = user_service.get_user(uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=UserResponse)
def update_me(user_in: UserUpdate, current_user: dict = Depends(get_current_user)):
    uid = current_user['uid']
    updated_user = user_service.update_user(uid, user_in)
    return updated_user
