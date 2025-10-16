"""
User service with database operations using SQLModel.
Handles user CRUD operations and OAuth integration.
"""

from typing import Optional
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User
from app.core.security import hash_password, verify_password


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email address."""
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user by UUID."""
    return await db.get(User, user_id)


async def create_user(
    db: AsyncSession, email: str, password: str, name: Optional[str] = None
) -> User:
    """Create a new user with hashed password."""
    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name,
        is_email_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: UUID, **kwargs) -> Optional[User]:
    """Update user profile fields."""
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    # Update allowed fields
    allowed_fields = {"name", "avatar_url", "is_email_verified"}
    for field, value in kwargs.items():
        if field in allowed_fields and value is not None:
            setattr(user, field, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_password(
    db: AsyncSession, user_id: UUID, new_password: str
) -> Optional[User]:
    """Update user password with new hashed password."""
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    user.password_hash = hash_password(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def verify_user_password(user: User, password: str) -> bool:
    """Verify user password against stored hash."""
    if not user.password_hash:
        return False
    return verify_password(password, user.password_hash)


async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    """Delete user account."""
    user = await get_user_by_id(db, user_id)
    if not user:
        return False

    # Hard delete - cascade will handle related records
    await db.delete(user)
    await db.commit()
    return True
