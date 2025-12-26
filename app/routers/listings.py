from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.models.listing import ListingResponse, ListingCreate, ListingUpdate
from app.services.listing_service import listing_service
from app.core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ListingResponse])
def get_listings(
    category: Optional[str] = None, 
    type: Optional[str] = None,
    current_user: dict = Depends(get_current_user) # Optional: if we want public access, remove Depends
):
    return listing_service.get_listings(category, type)

@router.post("/", response_model=ListingResponse)
def create_listing(listing: ListingCreate, current_user: dict = Depends(get_current_user)):
    try:
        return listing_service.create_listing(listing, current_user['uid'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: str, current_user: dict = Depends(get_current_user)):
    listing = listing_service.get_listing(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

@router.put("/{listing_id}", response_model=ListingResponse)
def update_listing(listing_id: str, listing_in: ListingUpdate, current_user: dict = Depends(get_current_user)):
    try:
        updated = listing_service.update_listing(listing_id, listing_in, current_user['uid'])
        if not updated:
            raise HTTPException(status_code=404, detail="Listing not found")
        return updated
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized to update this listing")
