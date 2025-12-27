from app.core.config import get_db
from app.models.user import UserCreate, UserUpdate
from datetime import datetime

class UserService:
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
            self._collection = self.db.collection('users')
        return self._collection

    def get_user(self, uid: str):
        doc = self.collection.document(uid).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def create_user(self, user: UserCreate):
        user_data = user.model_dump()
        user_data['created_at'] = datetime.utcnow()
        user_data['is_verified'] = False
        user_data['stats'] = {
            "carbon_saved": 0,
            "items_donated": 0,
            "items_received": 0
        }
        
        self.collection.document(user.uid).set(user_data)
        return user_data

    def update_user(self, uid: str, user_update: UserUpdate):
        doc_ref = self.collection.document(uid)
        update_data = user_update.model_dump(exclude_unset=True)
        
        if update_data:
            doc_ref.update(update_data)
        
        return self.get_user(uid)

    def toggle_favorite(self, uid: str, listing_id: str):
        fav_ref = self.collection.document(uid).collection('favorites').document(listing_id)
        doc = fav_ref.get()
        
        if doc.exists:
            fav_ref.delete()
            return False # Unliked
        else:
            fav_ref.set({
                "listing_id": listing_id,
                "created_at": datetime.utcnow()
            })
            return True # Liked

    def get_favorites(self, uid: str):
        fav_ref = self.collection.document(uid).collection('favorites').order_by('created_at', direction='DESCENDING')
        docs = fav_ref.stream()
        
        favorites = []
        from app.services.listing_service import listing_service
        
        for doc in docs:
            data = doc.to_dict()
            listing = listing_service.get_listing(data['listing_id'])
            if listing:
                favorites.append(listing)
                
        return favorites

user_service = UserService()
