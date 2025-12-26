from firebase_admin import firestore
from app.core.config import get_db
from app.models.user import UserCreate, UserUpdate
from datetime import datetime

class UserService:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection('users')

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

user_service = UserService()
