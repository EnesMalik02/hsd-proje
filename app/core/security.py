from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from app.core.config import init_firebase, settings
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Optional

# Setup password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Setup JWT
SECRET_KEY = settings.PROJECT_NAME + "_secret_key_change_me" # In prod, use env var!
ALGORITHM = "HS256"

# Initialize scheme
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default "infinite" (10 years)
        expire = datetime.utcnow() + timedelta(days=365*10)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(res: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates Token. 
    First tries to validate as Custom JWT (for Login/Register flow).
    If that fails, falls back to Firebase ID Token (for legacy/other flows if needed).
    """
    token = res.credentials
    
    # 1. Try Custom JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: str = payload.get("sub")
        if uid is None:
            raise ValueError("No sub")
        # Return a dict that mimics Firebase Token payload to keep compatibility
        return {"uid": uid, "token_type": "custom"}
    except jwt.PyJWTError:
        pass
        
    # 2. Try Firebase ID Token
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
