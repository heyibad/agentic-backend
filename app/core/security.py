from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession
import secrets
import string
from uuid import UUID
from app.utils.jwt import decode_token
from app.utils.db import get_db
import bcrypt

# Password hashing using bcrypt directly (more reliable)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    """Hash password using bcrypt directly - max 72 bytes"""
    # Truncate to 72 bytes if needed (bcrypt limitation)
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        # Truncate to 72 bytes for bcrypt
        password_bytes = password_bytes[:72]

    # Use bcrypt directly to avoid passlib compatibility issues
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash using bcrypt directly"""
    # Truncate password to 72 bytes if needed
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Use bcrypt directly to avoid passlib compatibility issues
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user from JWT token"""
    from app.models.user import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Get user from database
        user = await db.get(User, UUID(user_id))
        if user is None:
            raise credentials_exception

        return user

    except ValueError:
        raise credentials_exception


async def get_current_active_user(current_user=Depends(get_current_user)):
    """Get current active user (email verified)"""
    if not current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified"
        )
    return current_user


def generate_random_password(length: int = 12) -> str:
    """Generate secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def hash_token(token: str) -> str:
    """Hash a token for storage (for refresh token revocation)"""
    import hashlib

    return hashlib.sha256(token.encode()).hexdigest()


def check_password_strength(password: str) -> bool:
    """Check if password meets security requirements"""
    if len(password) < 8:
        return False
    # Add more complexity checks
    return True


async def reset_password(user_id: int, new_password: str):
    """Reset user password"""
    hashed = hash_password(new_password)
    # Update in database
    pass
