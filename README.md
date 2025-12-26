# HSD Proje API

This is the FastAPI backend for the HSD Proje.

## Stack
- Python 3.13+
- FastAPI
- Firebase Admin SDK (Firestore, Auth)

## Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```
   or manually:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file (copy from `.env.example` if available) and set:
   ```
   GOOGLE_APPLICATION_CREDENTIALS="path/to/serviceAccountKey.json"
   ```
   Or rely on default Google Cloud credentials if running in a cloud environment.

3. **Run Server**:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   or
   ```bash
   fastapi dev app/main.py
   ```

## Modules
- **/users**: User profile management
- **/listings**: Donation/Sale listings
- **/requests**: Handshake/Request mechanism
- **/chats**: Messaging
- **/notifications**: User notifications

## Authentication
All protected endpoints expect a Firebase ID Token in the Authorization header:
`Authorization: Bearer <firebase_id_token>`
