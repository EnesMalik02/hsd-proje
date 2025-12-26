from fastapi import APIRouter, HTTPException, status, Depends
from app.models.auth import UserRegister, UserLogin, Token
from app.services.user_service import user_service
from app.core.security import get_password_hash, verify_password, create_access_token
import uuid
from datetime import datetime
from firebase_admin import firestore

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_in: UserRegister):
    # 1. Check if user exists (by email OR username)
    users_ref = user_service.collection.where(filter=firestore.FieldFilter("email", "==", user_in.email)).get()
    if len(users_ref) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    username_ref = user_service.collection.where(filter=firestore.FieldFilter("username", "==", user_in.username)).get()
    if len(username_ref) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # 2. Create User
    uid = f"user_{uuid.uuid4().hex[:12]}"
    hashed_pw = get_password_hash(user_in.password)
    
    user_data = {
        "uid": uid,
        "uid": uid,
        "email": user_in.email,
        "username": user_in.username,
        "display_name": user_in.display_name,
        "hashed_password": hashed_pw, # Store hashed password
        "role": "standard",
        "created_at": datetime.utcnow(),
        "is_verified": False,
        "stats": {"carbon_saved": 0, "items_donated": 0, "items_received": 0}
    }
    
    user_service.collection.document(uid).set(user_data)
    
    # 3. Generate Token
    access_token = create_access_token(data={"sub": uid})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user_in: UserLogin):
    # 1. Find user by identifier (email or username)
    from firebase_admin import firestore
    
    identifier = user_in.identifier
    query = None
    
    if "@" in identifier:
        query = user_service.collection.where(filter=firestore.FieldFilter("email", "==", identifier))
    else:
        query = user_service.collection.where(filter=firestore.FieldFilter("username", "==", identifier))
        
    docs = list(query.stream())
    
    if not docs:
        raise HTTPException(status_code=400, detail="Incorrect email/username or password")
    
    user_doc = docs[0].to_dict()
    user_uid = user_doc['uid']
    hashed_pw = user_doc.get('hashed_password')
    
    if not hashed_pw:
        # Fallback for firebase users who might not have password set here?
        raise HTTPException(status_code=400, detail="Invalid credential configuration")
        
    # 2. Verify Password
    if not verify_password(user_in.password, hashed_pw):
        raise HTTPException(status_code=400, detail="Incorrect email/username or password")
        
    # 3. Generate Token
    # "Sonsuz süreli" -> Default behavior in create_access_token is 10 years
    access_token = create_access_token(data={"sub": user_uid})
    return {"access_token": access_token, "token_type": "bearer"}


