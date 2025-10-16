"""
OAuth authentication schemas
"""

from pydantic import BaseModel
from typing import Optional


class GoogleAuthURL(BaseModel):
    """Google OAuth authorization URL response"""

    auth_url: str


class GoogleCallback(BaseModel):
    """Google OAuth callback data"""

    code: str
    state: Optional[str] = None


class OAuthUserInfo(BaseModel):
    """OAuth user information from provider"""

    provider: str
    provider_id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_email_verified: bool = True  # OAuth providers verify emails
