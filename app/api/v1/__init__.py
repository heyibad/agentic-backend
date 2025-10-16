from fastapi import APIRouter
from app.api.v1 import auth, oauth

api_router = APIRouter(prefix="/api/v1")

# Include routers
api_router.include_router(auth.router)
api_router.include_router(oauth.router)

__all__ = ["api_router"]
