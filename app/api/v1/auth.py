from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.utils.db import get_db
from app.schema.auth import UserRegister, UserLogin, TokenResponse, TokenRefresh
from app.schema.user import UserResponse
from app.services.auth_service import AuthService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **name**: Optional display name

    Returns the created user and authentication tokens.
    """
    user, tokens = await AuthService.register_user(user_data, db)

    # Convert user to dict to avoid lazy loading issues
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        is_email_verified=user.is_email_verified,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password.

    Returns access token (short-lived) and refresh token (long-lived).
    """
    user, tokens = await AuthService.login_user(login_data, db)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using refresh token.

    The old refresh token will be revoked and a new one issued.
    """
    new_tokens = await AuthService.refresh_access_token(token_data.refresh_token, db)
    return new_tokens


@router.post("/logout")
async def logout(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Logout user by revoking refresh token.

    Requires a valid access token in Authorization header.
    """
    result = await AuthService.logout_user(token_data.refresh_token, db)
    return result


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.

    Requires valid access token in Authorization header.
    """
    # Convert user to dict to avoid lazy loading issues
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_email_verified=current_user.is_email_verified,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at,
    )


@router.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_user)):
    """
    Verify if the provided token is valid.

    Returns user ID if valid, otherwise 401 error.
    """
    return {"valid": True, "user_id": str(current_user.id), "email": current_user.email}
