from firebase_admin import firestore
from app.core.config import get_db
from app.models.chat import MessageCreate
from datetime import datetime
import uuid

class ChatService:
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
            self._collection = self.db.collection('chats')
        return self._collection

    def create_chat(self, request_data: dict):
        # ID format: listingID_buyerID
        listing_id = request_data['listing_id']
        requester_id = request_data['requester_id']
        seller_id = request_data['seller_id']
        
        chat_id = f"{listing_id}_{requester_id}"
        
        doc_ref = self.collection.document(chat_id)
        if doc_ref.get().exists:
            return doc_ref.get().to_dict()
            
        chat_data = {
            "id": chat_id,
            "participants": [seller_id, requester_id],
            "listing_id": listing_id,
            "status": "open",
            "last_message": None,
            "last_message_time": None,
            "unread_count": {
                seller_id: 0,
                requester_id: 0
            }
        }
        doc_ref.set(chat_data)
        return chat_data

    def get_chats(self, uid: str):
        # Query where participants array contains uid
        query = self.collection.where(filter=firestore.FieldFilter("participants", "array_contains", uid))
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    def get_messages(self, chat_id: str, uid: str):
        # Verify participation
        chat_ref = self.collection.document(chat_id)
        chat = chat_ref.get()
        if not chat.exists:
            return None
        
        if uid not in chat.get('participants'):
            raise PermissionError("Not a participant")
            
        # Optimization: Reset unread count for this user
        # Note: In a real app, this might be a separate "mark read" call
        unread_map = chat.get('unread_count') or {}
        if unread_map.get(uid, 0) > 0:
            unread_map[uid] = 0
            chat_ref.update({"unread_count": unread_map})

        # Get messages subcollection
        msgs = chat_ref.collection('messages').order_by('created_at').stream()
        messages = [{**m.to_dict(), "id": m.id} for m in msgs]
        
        # Try to fetch content from Walrus if available
        from app.core.config import settings
        from app.services.walrus_service import get_walrus_service
        
        if settings.WALRUS_ENABLED:
            walrus = get_walrus_service()
            if walrus:
                for msg in messages:
                    blob_id = msg.get('walrus_blob_id')
                    if blob_id:
                        try:
                            # Read text from Walrus blockchain
                            walrus_text = walrus.read_text(blob_id)
                            if walrus_text:
                                msg['text'] = walrus_text
                                msg['_walrus_verified'] = True
                        except Exception as e:
                            print(f"Failed to read from Walrus {blob_id}: {e}")
                            # Fallback to Firestore text
        
        return messages

    def send_message(self, chat_id: str, message: MessageCreate, sender_id: str):
        chat_ref = self.collection.document(chat_id)
        chat = chat_ref.get()
        if not chat.exists:
            raise ValueError("Chat not found")
        
        participants = chat.get('participants')
        if sender_id not in participants:
            raise PermissionError("Not a participant")
            
        # Create message data
        msg_data = message.model_dump()
        msg_data['sender_id'] = sender_id
        msg_data['created_at'] = datetime.utcnow()
        msg_data['storage_type'] = 'firestore'  # Default
        msg_data['walrus_blob_id'] = None
        
        # Try to store on Walrus blockchain if enabled
        from app.core.config import settings
        from app.services.walrus_service import get_walrus_service
        
        if settings.WALRUS_ENABLED and message.text:
            walrus = get_walrus_service()
            if walrus:
                try:
                    # Store message text on Walrus blockchain
                    blob_result = walrus.store_text(message.text)
                    if blob_result and blob_result.get('blob_id'):
                        msg_data['walrus_blob_id'] = blob_result['blob_id']
                        msg_data['storage_type'] = 'hybrid'  # Stored in both Firestore and Walrus
                        print(f"Message stored on Walrus: {blob_result['blob_id']}")
                except Exception as e:
                    print(f"Failed to store on Walrus, using Firestore only: {e}")
        
        # Save to Firestore
        msg_ref = chat_ref.collection('messages').document()
        msg_ref.set(msg_data)
        
        # Update chat doc
        recipient_id = next((p for p in participants if p != sender_id), None)
        updates = {
            "last_message": message.text or ("Image" if message.type == "image" else "Location"),
            "last_message_time": msg_data['created_at']
        }
        
        # Increment unread for recipient
        if recipient_id:
            unread_map = chat.get('unread_count') or {}
            unread_map[recipient_id] = unread_map.get(recipient_id, 0) + 1
            updates["unread_count"] = unread_map
            
        chat_ref.update(updates)
        return {**msg_data, "id": msg_ref.id}

chat_service = ChatService()
