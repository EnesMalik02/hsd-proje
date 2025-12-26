from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings, init_firebase
from app.routers import users, listings, requests, chats, notifications, auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
origins = ["*"] # Allow all for development

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
def startup_event():
    init_firebase()
    from app.core.config import init_walrus
    init_walrus()

# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(listings.router, prefix="/listings", tags=["Listings"])
app.include_router(requests.router, prefix="/requests", tags=["Requests"])
app.include_router(chats.router, prefix="/chats", tags=["Chats"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

@app.get("/")
def read_root():
    return {"message": "Welcome to HSD Proje API"}
