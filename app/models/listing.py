from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime

class Location(BaseModel):
    lat: float
    lng: float
    city: str
    district: str

class ListingBase(BaseModel):
    title: str
    description: str
    images: List[str] = []
    category: str # "furniture", "electronics", "clothing", "books"
    type: str # "donation", "sale", "support"
    price: float = 0.0
    currency: str = "TRY"
    currency: str = "TRY"
    location: Location
    phone_number: Optional[str] = None
    status: str = "active" # "active", "reserved", "completed", "archived"

class ListingCreate(ListingBase):
    @field_validator('images')
    @classmethod
    def validate_images(cls, v):
        if not v:
            return v
        for img in v:
            if not img.startswith('data:image/'):
                raise ValueError('Images must be Base64 encoded data URIs starting with "data:image/"')
        return v

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None
    images: Optional[List[str]] = None
    price: Optional[float] = None
    phone_number: Optional[str] = None
    status: Optional[str] = None

    @field_validator('images')
    @classmethod
    def validate_images(cls, v):
        if not v:
            return v
        for img in v:
            if not img.startswith('data:image/'):
                raise ValueError('Images must be Base64 encoded data URIs starting with "data:image/"')
        return v

class ListingResponse(ListingBase):
    id: str
    owner_id: str
    owner_name: str
    owner_avatar: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
