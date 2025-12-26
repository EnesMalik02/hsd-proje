from pydantic import BaseModel, Field
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
    location: Location
    status: str = "active" # "active", "reserved", "completed", "archived"

class ListingCreate(ListingBase):
    pass

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None
    price: Optional[float] = None
    status: Optional[str] = None

class ListingResponse(ListingBase):
    id: str
    owner_id: str
    owner_name: str
    owner_avatar: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
