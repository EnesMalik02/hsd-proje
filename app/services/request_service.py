from firebase_admin import firestore
from app.core.config import get_db
from app.models.request import RequestCreate, ListingSnapshot
from app.services.user_service import user_service
from app.services.listing_service import listing_service
# cyclic import risk if chat_service imports request_service.
# for now we will just use db directly or import inside method
from datetime import datetime
import uuid

class RequestService:
    def __init__(self):
        self._db = None
        self._collection = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_db()
        return self._db

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.db.collection('requests')
        return self._collection

    def create_request(self, request_in: RequestCreate, requester_uid: str):
        # 1. Get requester info
        requester = user_service.get_user(requester_uid)
        if not requester:
            raise ValueError("User not found")
        
        # 2. Get listing info
        listing = listing_service.get_listing(request_in.listing_id)
        if not listing:
            raise ValueError("Listing not found")
            
        if listing['owner_id'] == requester_uid:
            raise ValueError("Cannot request your own item")

        # 3. Prepare data
        req_id = f"req_{uuid.uuid4().hex[:8]}"
        
        snapshot = ListingSnapshot(
            title=listing['title'],
            image=listing['images'][0] if listing.get('images') else None,
            price=listing.get('price', 0)
        )

        req_data = {
            "id": req_id,
            "listing_id": request_in.listing_id,
            "requester_id": requester_uid,
            "requester_name": requester.get('display_name', 'Unknown'),
            "requester_avatar": requester.get('photo_url'),
            "requester_role": requester.get('role', 'standard'),
            "seller_id": listing['owner_id'], # Optimization
            "listing_snapshot": snapshot.model_dump(),
            "message": request_in.message,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        self.collection.document(req_id).set(req_data)
        return req_data

    def get_requests(self, role: str, uid: str):
        # role: "requester" (outbound) or "seller" (inbound)
        if role == "requester":
            query = self.collection.where(filter=firestore.FieldFilter("requester_id", "==", uid))
        elif role == "seller":
            query = self.collection.where(filter=firestore.FieldFilter("seller_id", "==", uid))
        else:
            return []
            
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    def update_status(self, request_id: str, status: str, user_uid: str):
        doc_ref = self.collection.document(request_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        
        # Only seller can approve/reject
        if data['seller_id'] != user_uid:
            raise PermissionError("Not authorized")
            
        doc_ref.update({"status": status})
        
        # If approved, trigger chat creation
        if status == "approved":
            from app.services.chat_service import chat_service
            chat_service.create_chat(data)
            
        return doc_ref.get().to_dict()

request_service = RequestService()
