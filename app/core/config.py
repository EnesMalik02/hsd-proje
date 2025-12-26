import os
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

class Settings:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "HSD Proje API")
    API_V1_STR = "/api/v1"
    
    # Firebase
    # If GOOGLE_APPLICATION_CREDENTIALS is set, firebase_admin.initialize_app() will use it automatically.
    # Otherwise, we can manually look for a specific path.
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

settings = Settings()

def init_firebase():
    """Initializes Firebase App."""
    try:
        if not firebase_admin._apps:
            if settings.FIREBASE_CREDENTIALS_PATH:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            else:
                # expecting GOOGLE_APPLICATION_CREDENTIALS to be set or default behavior
                firebase_admin.initialize_app()
            
            print("Firebase initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")

# Initialize db client (will be used in services)
# Note: We must call init_firebase() before accessing this, usually in main.py startup event
# or lazily. Here we might just expose a function to get it.

def get_db():
    return firestore.client()
