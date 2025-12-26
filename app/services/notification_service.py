from firebase_admin import firestore
from app.core.config import get_db
from app.models.notification import NotificationCreate
from datetime import datetime
import uuid

class NotificationService:
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
            self._collection = self.db.collection('notifications')
        return self._collection

    def create_notification(self, notification: NotificationCreate):
        notif_data = notification.model_dump()
        notif_data['id'] = f"notif_{uuid.uuid4().hex[:8]}"
        notif_data['is_read'] = False
        notif_data['created_at'] = datetime.utcnow()
        
        self.collection.document(notif_data['id']).set(notif_data)
        return notif_data

    def get_notifications(self, uid: str):
        query = self.collection.where(filter=firestore.FieldFilter("recipient_id", "==", uid)).order_by("created_at", direction=firestore.Query.DESCENDING)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    def mark_as_read(self, notification_id: str, uid: str):
        doc_ref = self.collection.document(notification_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        
        if doc.get('recipient_id') != uid:
            raise PermissionError("Not authorized")
            
        doc_ref.update({"is_read": True})
        return doc_ref.get().to_dict()

notification_service = NotificationService()
