from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.models.listing import ListingResponse, ListingCreate, ListingUpdate
from app.services.listing_service import listing_service
from app.services.user_service import user_service
from app.core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ListingResponse])
def get_listings(
    category: Optional[str] = None, 
    type: Optional[str] = None,
    city: Optional[str] = None,
    district: Optional[str] = None,
):
    return listing_service.get_listings(category, type, city, district)

@router.get("/suggested", response_model=List[ListingResponse])
def get_suggested_listings(current_user: dict = Depends(get_current_user)):
    """
    Get suggested listings for the current user.
    If user has location info, return listings from their city.
    Otherwise, return random listings.
    """
    uid = current_user['uid']
    user = user_service.get_user(uid)
    
    if user and user.get('location') and user['location'].get('city'):
        # User has location, suggest based on city
        city = user['location']['city']
        listings = listing_service.get_listings_by_location(city)
        if listings:
            return listings
        # If no listings in city, fall back to random?
        # For now let's just return empty or maybe fall back. 
        # Requirement says "if location entered -> according to location; if not -> random".
        # It implies if location is there, we try location. 
        # But if location yields 0 results, random might be better than empty.
        # I'll stick to strict interpretation first: if location -> location results.
        return listings
        
    return listing_service.get_random_listings()

@router.get("/me", response_model=List[ListingResponse])
def get_my_listings(current_user: dict = Depends(get_current_user)):
    """
    Get listings created by the current user.
    """
    return listing_service.get_listings(owner_id=current_user['uid'])

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

@router.patch("/{listing_id}", response_model=ListingResponse)
def patch_listing(listing_id: str, listing_in: ListingUpdate, current_user: dict = Depends(get_current_user)):
    """
    Partially update a listing.
    """
    try:
        updated = listing_service.update_listing(listing_id, listing_in, current_user['uid'])
        if not updated:
            raise HTTPException(status_code=404, detail="Listing not found")
        return updated
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized to update this listing")
