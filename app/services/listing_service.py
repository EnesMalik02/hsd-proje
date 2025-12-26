from firebase_admin import firestore
from app.core.config import get_db
from app.models.listing import ListingCreate, ListingUpdate
from app.services.user_service import user_service
from datetime import datetime
import uuid

class ListingService:
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
            self._collection = self.db.collection('listings')
        return self._collection

    def get_listings(self, category: str = None, type: str = None):
        query = self.collection
        if category:
            query = query.where(filter=firestore.FieldFilter("category", "==", category))
        if type:
            query = query.where(filter=firestore.FieldFilter("type", "==", type))
        
        # Limit for demo, in real world we need pagination
        docs = query.limit(50).stream()
        return [doc.to_dict() for doc in docs]

    def get_listing(self, listing_id: str):
        doc = self.collection.document(listing_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def create_listing(self, listing: ListingCreate, owner_uid: str):
        # Fetch user details for denormalization
        owner = user_service.get_user(owner_uid)
        if not owner:
            # Fallback or error? Let's assume user must exist
            raise ValueError("User not found")

        listing_data = listing.model_dump()
        listing_id = f"listing_{uuid.uuid4().hex[:8]}"
        
        listing_data['id'] = listing_id
        listing_data['owner_id'] = owner_uid
        listing_data['owner_name'] = owner.get('display_name', 'Unknown')
        listing_data['owner_avatar'] = owner.get('photo_url')
        listing_data['created_at'] = datetime.utcnow()
        listing_data['updated_at'] = datetime.utcnow()
        
        self.collection.document(listing_id).set(listing_data)
        return listing_data

    def update_listing(self, listing_id: str, listing_update: ListingUpdate, owner_uid: str):
        doc_ref = self.collection.document(listing_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
            
        current_data = doc.to_dict()
        if current_data['owner_id'] != owner_uid:
            raise PermissionError("Not authorized to update this listing")

        update_data = listing_update.model_dump(exclude_unset=True)
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            doc_ref.update(update_data)
            
        return doc_ref.get().to_dict()

listing_service = ListingService()
