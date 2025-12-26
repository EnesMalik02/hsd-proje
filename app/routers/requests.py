from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Literal
from app.models.request import RequestResponse, RequestCreate, RequestUpdate
from app.services.request_service import request_service
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=RequestResponse)
def create_request(request: RequestCreate, current_user: dict = Depends(get_current_user)):
    try:
        return request_service.create_request(request, current_user['uid'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[RequestResponse])
def get_requests(
    role: Literal["requester", "seller"],
    current_user: dict = Depends(get_current_user)
):
    """
    role='requester': Get requests I made (Outbound)
    role='seller': Get requests for my items (Inbound)
    """
    return request_service.get_requests(role, current_user['uid'])

@router.put("/{request_id}/status", response_model=RequestResponse)
def update_request_status(
    request_id: str, 
    status_update: RequestUpdate, 
    current_user: dict = Depends(get_current_user)
):
    try:
        updated = request_service.update_status(request_id, status_update.status, current_user['uid'])
        if not updated:
            raise HTTPException(status_code=404, detail="Request not found")
        return updated
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")
