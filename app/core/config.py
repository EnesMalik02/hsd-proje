import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

class Settings:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "HSD Proje API")
    API_V1_STR = "/api/v1"
    
    # Firebase Credentials from .env
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY_ID = os.getenv("FIREBASE_PRIVATE_KEY_ID")
    FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY")
    FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
    FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID")
    FIREBASE_AUTH_URI = os.getenv("FIREBASE_AUTH_URI")
    FIREBASE_TOKEN_URI = os.getenv("FIREBASE_TOKEN_URI")
    FIREBASE_AUTH_PROVIDER_CERT_URL = os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL")
    FIREBASE_CLIENT_CERT_URL = os.getenv("FIREBASE_CLIENT_CERT_URL")

settings = Settings()

def init_firebase():
    """Initializes Firebase App using Environment Variables."""
    try:
        # Eğer uygulama zaten başlatılmadıysa
        if not firebase_admin._apps:
            
            # En kritik değişkenlerin varlığını kontrol edelim
            if settings.FIREBASE_PRIVATE_KEY and settings.FIREBASE_CLIENT_EMAIL:
                
                # .env'den gelen string içindeki kaçış karakterlerini (\n) gerçek satır sonuna çeviriyoruz
                # Bu adım çok önemlidir, yoksa "Invalid Private Key" hatası alırsınız.
                private_key = settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n')
                # JSON dosyası yerine bu sözlük yapısını kullanıyoruz
                cred_dict = {
                    "type": "service_account",
                    "project_id": settings.FIREBASE_PROJECT_ID,
                    "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                    "private_key": private_key,
                    "client_email": settings.FIREBASE_CLIENT_EMAIL,
                    "client_id": settings.FIREBASE_CLIENT_ID,
                    "auth_uri": settings.FIREBASE_AUTH_URI,
                    "token_uri": settings.FIREBASE_TOKEN_URI,
                    "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_CERT_URL,
                    "client_x509_cert_url": settings.FIREBASE_CLIENT_CERT_URL
                }

                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                print("Firebase initialized from Environment Variables successfully.")
            
            else:
                # Env değişkenleri yoksa fallback olarak default (Google Cloud ortamı) dene
                print("Firebase Env variables not found, trying default credentials...")
                firebase_admin.initialize_app()
                print("Firebase initialized from default credentials.")

    except Exception as e:
        print(f"Error initializing Firebase: {e}")

def get_db():
    return firestore.client()