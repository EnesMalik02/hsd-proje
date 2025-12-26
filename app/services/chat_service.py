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

    def create_chat(self, request_data: dict = None, listing_id: str = None, requester_id: str = None, seller_id: str = None):
        # Support flexible arguments for both Request flow and Direct Start flow
        if request_data:
            listing_id = request_data['listing_id']
            requester_id = request_data['requester_id']
            seller_id = request_data['seller_id']
            
        if not (listing_id and requester_id and seller_id):
            raise ValueError("Missing chat parameters")

        # ID format: listingID_buyerID
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

    def start_chat(self, listing_id: str, requester_uid: str):
        # 1. Get listing to find owner
        from app.services.listing_service import listing_service
        listing = listing_service.get_listing(listing_id)
        if not listing:
            raise ValueError("Listing not found")
            
        owner_id = listing['owner_id']
        if owner_id == requester_uid:
             # If owner tries to start chat, maybe check if they have chats ON this listing?
             # For now, let's assume "Start Chat" is mainly for buyers.
             # If owner clicks on their own listing, they should probably see list of chats.
             # But if they really want to create a chat with themselves? Probably block.
             raise ValueError("Cannot chat with yourself")

        return self.create_chat(listing_id=listing_id, requester_id=requester_uid, seller_id=owner_id)

    def get_chats(self, uid: str):
        # Query where participants array contains uid
        query = self.collection.where(filter=firestore.FieldFilter("participants", "array_contains", uid))
        docs = query.stream()
        
        chat_list = []
        from app.services.listing_service import listing_service
        
        for doc in docs:
            data = doc.to_dict()
            listing_id = data.get('listing_id')
            if listing_id:
                listing = listing_service.get_listing(listing_id)
                if listing:
                    data['listing_title'] = listing.get('title')
                    # Get first image if available
                    images = listing.get('images', [])
                    data['listing_image'] = images[0] if images else None
            
            chat_list.append(data)
            
        return chat_list

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
        # Get messages subcollection
        # We want the LAST 100 messages.
        # So we order by created_at DESCENDING, limit 100, then reverse.
        msgs = chat_ref.collection('messages').order_by('created_at', direction=firestore.Query.DESCENDING).limit(100).stream()
        
        # Convert to list
        results = [{**m.to_dict(), "id": m.id} for m in msgs]
        
        # Reverse to return in chronological order (oldest first)
        results.reverse()
        return results

    def send_message(self, chat_id: str, message: MessageCreate, sender_id: str):
        chat_ref = self.collection.document(chat_id)
        chat = chat_ref.get()
        if not chat.exists:
            raise ValueError("Chat not found")
        
        participants = chat.get('participants')
        if sender_id not in participants:
            raise PermissionError("Not a participant")
            
        # Create message in subcollection
        msg_data = message.model_dump()
        msg_data['sender_id'] = sender_id
        msg_data['created_at'] = datetime.utcnow()
        
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
