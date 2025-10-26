from fastapi import APIRouter
from app.api.v1 import auth, oauth
from app.api.v1 import chat

api_router = APIRouter(prefix="/api/v1")

# Include routers
api_router.include_router(auth.router)
api_router.include_router(oauth.router)
api_router.include_router(chat.router)

__all__ = ["api_router"]
