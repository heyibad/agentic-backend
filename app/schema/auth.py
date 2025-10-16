from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class UserRegister(BaseModel):
    """Schema for user registration"""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh"""

    refresh_token: str


class TokenData(BaseModel):
    """Schema for token data payload"""

    user_id: Optional[UUID] = None
    email: Optional[str] = None


class PasswordReset(BaseModel):
    """Schema for password reset"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class ChangePassword(BaseModel):
    """Schema for password change"""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth"""

    code: str
    redirect_uri: str
