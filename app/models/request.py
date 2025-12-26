from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ListingSnapshot(BaseModel):
    title: str
    image: Optional[str] = None
    price: float = 0

class RequestBase(BaseModel):
    listing_id: str
    message: str

class RequestCreate(RequestBase):
    pass

class RequestUpdate(BaseModel):
    status: str # "approved", "rejected"

class RequestResponse(RequestBase):
    id: str
    requester_id: str
    requester_name: str
    requester_avatar: Optional[str] = None
    requester_role: str
    
    # Optimization: seller_id to query inbound requests easily
    seller_id: str
    
    listing_snapshot: ListingSnapshot
    status: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
