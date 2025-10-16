from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.security import hash_password, verify_password, hash_token
from app.utils.jwt import create_access_token, create_refresh_token, decode_token
from app.schema.auth import UserRegister, UserLogin, TokenResponse
from app.core.config import settings


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    async def register_user(
        user_data: UserRegister, db: AsyncSession
    ) -> tuple[User, TokenResponse]:
        """Register a new user"""
        # Check if user exists
        statement = select(User).where(User.email == user_data.email)
        result = await db.exec(statement)
        existing_user = result.first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            name=user_data.name,
            is_email_verified=False,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Detach user from session to prevent lazy loading issues
        db.expunge(new_user)

        # Generate tokens (need to get user back in session)
        statement = select(User).where(User.id == new_user.id)
        result = await db.exec(statement)
        user_for_tokens = result.first()
        tokens = await AuthService._generate_tokens(user_for_tokens, db)

        return new_user, tokens

    @staticmethod
    async def login_user(
        login_data: UserLogin, db: AsyncSession
    ) -> tuple[User, TokenResponse]:
        """Login user and return tokens"""
        # Get user by email
        statement = select(User).where(User.email == login_data.email)
        result = await db.exec(statement)
        user = result.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # Verify password
        if not user.password_hash or not verify_password(
            login_data.password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # Generate tokens
        tokens = await AuthService._generate_tokens(user, db)

        return user, tokens

    @staticmethod
    async def refresh_access_token(
        refresh_token: str, db: AsyncSession
    ) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            # Decode refresh token
            payload = decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            # Check if token is in database and not revoked
            token_hash = hash_token(refresh_token)
            statement = select(RefreshToken).where(
                RefreshToken.token_hash == token_hash, RefreshToken.revoked == False
            )
            result = await db.exec(statement)
            token_record = result.first()

            if not token_record:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token not found or revoked",
                )

            # Check if token expired
            from datetime import timezone

            current_time = datetime.now(timezone.utc).replace(tzinfo=None)
            token_expires = (
                token_record.expires_at.replace(tzinfo=None)
                if token_record.expires_at.tzinfo
                else token_record.expires_at
            )
            if token_expires < current_time:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
                )

            # Get user
            user = await db.get(User, UUID(user_id))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
                )

            # Generate new tokens
            new_tokens = await AuthService._generate_tokens(user, db)

            # Revoke old refresh token
            token_record.revoked = True
            db.add(token_record)
            await db.commit()

            return new_tokens

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    @staticmethod
    async def logout_user(refresh_token: str, db: AsyncSession) -> dict:
        """Logout user by revoking refresh token"""
        token_hash = hash_token(refresh_token)

        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await db.exec(statement)
        token_record = result.first()

        if token_record:
            token_record.revoked = True
            db.add(token_record)
            await db.commit()

        return {"message": "Successfully logged out"}

    @staticmethod
    async def get_user_by_id(user_id: UUID, db: AsyncSession) -> Optional[User]:
        """Get user by ID"""
        user = await db.get(User, user_id)
        return user

    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
        """Get user by email"""
        statement = select(User).where(User.email == email)
        result = await db.exec(statement)
        return result.first()

    @staticmethod
    async def _generate_tokens(user: User, db: AsyncSession) -> TokenResponse:
        """Generate access and refresh tokens for user"""
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        # Create refresh token
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Store refresh token in database
        token_hash = hash_token(refresh_token)
        expires_at = datetime.utcnow() + timedelta(
            days=settings.refresh_token_expire_days
        )

        refresh_token_record = RefreshToken(
            user_id=user.id, token_hash=token_hash, expires_at=expires_at, revoked=False
        )

        db.add(refresh_token_record)
        await db.commit()

        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
