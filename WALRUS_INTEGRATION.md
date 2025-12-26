# Walrus Blockchain Integration

This branch adds **Walrus blockchain decentralized storage** integration to the HSD Proje chat system.

## 🚀 What's New

### Walrus Blockchain Storage
- Chat messages are now stored on **Walrus Testnet** (decentralized storage on Sui blockchain)
- **Hybrid storage**: Messages stored in both Firestore and Walrus for redundancy
- Automatic fallback to Firestore if Walrus is unavailable
- New API endpoint to view blockchain storage information

## 📦 Changes Made

### New Files
- `app/services/walrus_service.py` - Walrus blockchain service with blob storage methods
- `.env.walrus.example` - Example environment configuration for Walrus

### Modified Files
- `app/core/config.py` - Added Walrus configuration settings and initialization
- `app/main.py` - Added Walrus service initialization on startup
- `app/models/chat.py` - Added `walrus_blob_id` and `storage_type` fields to messages
- `app/services/chat_service.py` - Integrated Walrus storage in send/receive message methods
- `app/routers/chats.py` - Added `/walrus-info` endpoint for blockchain information

## 🔧 Setup Instructions

### 1. Add Environment Variables

Add these lines to your `.env` file:

```env
# Walrus Blockchain Configuration
WALRUS_ENABLED=true
WALRUS_PUBLISHER_URL=https://publisher.walrus-testnet.walrus.space
WALRUS_AGGREGATOR_URL=https://aggregator.walrus-testnet.walrus.space
WALRUS_EPOCHS=5
```

### 2. Install Dependencies

No new dependencies required! The integration uses the existing `httpx` library.

### 3. Run the Application

```bash
uvicorn app.main:app --reload
```

You should see:
```
Walrus service initialized successfully (Testnet)
```

## 🧪 Testing

### Test Message Storage

1. Send a message via the API:
```bash
POST /chats/{chat_id}/messages
{
  "text": "Hello from Walrus blockchain!",
  "type": "text"
}
```

2. Check the response for `walrus_blob_id` and `storage_type: "hybrid"`

### View Blockchain Info

```bash
GET /chats/{chat_id}/messages/{message_id}/walrus-info
```

Response:
```json
{
  "message_id": "...",
  "walrus_enabled": true,
  "stored_on_walrus": true,
  "storage_type": "hybrid",
  "blob_id": "...",
  "aggregator_url": "https://aggregator.walrus-testnet.walrus.space/v1/..."
}
```

## 🔍 How It Works

### Message Flow

1. **Sending a Message**:
   - User sends message via API
   - If `WALRUS_ENABLED=true`, message text is stored on Walrus blockchain
   - Walrus returns a `blob_id`
   - Message metadata (including `blob_id`) is saved to Firestore
   - Storage type is set to `"hybrid"`

2. **Retrieving Messages**:
   - Messages are fetched from Firestore
   - If message has a `walrus_blob_id`, content is fetched from Walrus blockchain
   - Fallback to Firestore text if Walrus fetch fails

### Storage Types

- `"firestore"` - Only stored in Firestore (Walrus disabled or failed)
- `"walrus"` - Only stored on Walrus blockchain
- `"hybrid"` - Stored in both Firestore and Walrus (recommended)

## 🌐 Walrus Testnet

- **Publisher**: https://publisher.walrus-testnet.walrus.space
- **Aggregator**: https://aggregator.walrus-testnet.walrus.space
- **Explorer**: https://walruscan.com/testnet
- **Docs**: https://docs.walrus.site

## 🔐 Security & Privacy

- Messages are stored as blobs on Walrus blockchain
- Blob IDs are publicly accessible (anyone with blob ID can read the content)
- Consider encryption for sensitive messages in production
- Testnet data may be pruned after epoch expiration

## 🚦 Rollback

To disable Walrus and use Firestore only:

```env
WALRUS_ENABLED=false
```

The system will automatically fall back to Firestore-only mode. Existing messages with Walrus blob IDs will still be readable from Firestore.

## 📊 Future Enhancements

- [ ] End-to-end encryption for messages before storing on Walrus
- [ ] Media file (images, videos) storage on Walrus
- [ ] Mainnet deployment
- [ ] Blob deletion/expiration management
- [ ] Cost optimization for blob storage

## 🤝 Contributing

This is a feature branch. Please test thoroughly before merging to main.

---

**Branch**: `feature/walrus-blockchain-integration`  
**Status**: ✅ Ready for Review  
**Testnet**: Walrus Testnet on Sui Blockchain
