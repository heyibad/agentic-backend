from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    name: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""

    id: UUID
    is_email_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update schema"""

    name: Optional[str] = None
    avatar_url: Optional[str] = None
