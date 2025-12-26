from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from app.models.listing import Location

class UserStats(BaseModel):
    carbon_saved: float = 0.0
    items_donated: int = 0
    items_received: int = 0

class UserBase(BaseModel):
    email: EmailStr
    display_name: str
    photo_url: Optional[str] = None
    role: str = "standard" # "standard", "student", "ngo", "admin"
    bio: Optional[str] = None
    fcm_token: Optional[str] = None
    verification_doc: Optional[str] = None
    location: Optional[Location] = None

class UserCreate(UserBase):
    uid: str

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    fcm_token: Optional[str] = None
    verification_doc: Optional[str] = None
    location: Optional[Location] = None

class UserResponse(UserBase):
    uid: str
    is_verified: bool = False
    stats: UserStats = Field(default_factory=UserStats)
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
