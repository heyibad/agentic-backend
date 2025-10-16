"""
OAuth authentication service using Authlib
Handles Google OAuth2 login flow
"""

from typing import Optional, Dict, Any
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.user import User
from app.schema.oauth import OAuthUserInfo
from app.services.auth_service import AuthService

# Load OAuth configuration
config = Config(".env")
oauth = OAuth(config)

# Register Google OAuth provider
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


class OAuthService:
    """Service for OAuth authentication operations"""

    @staticmethod
    def get_oauth_client(provider: str = "google"):
        """Get OAuth client for specified provider"""
        if provider == "google":
            return oauth.google
        raise ValueError(f"Unsupported OAuth provider: {provider}")

    @staticmethod
    async def get_or_create_oauth_user(
        oauth_info: OAuthUserInfo, db: AsyncSession
    ) -> User:
        """
        Get existing user by OAuth ID or create new user from OAuth data.
        If user exists by email but not OAuth, link the OAuth account.
        """
        # First, check if user exists with this OAuth provider ID
        statement = select(User).where(
            User.oauth_provider == oauth_info.provider,
            User.oauth_id == oauth_info.provider_id,
        )
        result = await db.exec(statement)
        user = result.first()

        if user:
            # User exists with this OAuth account
            # Update avatar if changed
            if oauth_info.avatar_url and user.avatar_url != oauth_info.avatar_url:
                user.avatar_url = oauth_info.avatar_url
                db.add(user)
                await db.commit()
                await db.refresh(user)
            return user

        # Check if user exists by email (might have registered with password before)
        statement = select(User).where(User.email == oauth_info.email)
        result = await db.exec(statement)
        existing_user = result.first()

        if existing_user:
            # User exists with email but no OAuth linked
            # Link this OAuth account to existing user
            existing_user.oauth_provider = oauth_info.provider
            existing_user.oauth_id = oauth_info.provider_id
            existing_user.is_oauth_user = True
            existing_user.is_email_verified = True  # OAuth emails are verified

            if oauth_info.avatar_url:
                existing_user.avatar_url = oauth_info.avatar_url
            if oauth_info.name and not existing_user.name:
                existing_user.name = oauth_info.name

            db.add(existing_user)
            await db.commit()
            await db.refresh(existing_user)
            return existing_user

        # Create new user from OAuth data
        new_user = User(
            email=oauth_info.email,
            name=oauth_info.name,
            avatar_url=oauth_info.avatar_url,
            is_email_verified=True,  # OAuth emails are pre-verified
            oauth_provider=oauth_info.provider,
            oauth_id=oauth_info.provider_id,
            is_oauth_user=True,
            password_hash=None,  # OAuth-only user, no password
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    @staticmethod
    async def handle_google_callback(
        code: str, db: AsyncSession, redirect_uri: Optional[str] = None
    ) -> tuple[User, Any]:
        """
        Handle Google OAuth callback and return user with tokens.

        Args:
            code: Authorization code from Google
            db: Database session
            redirect_uri: Optional redirect URI (must match the one used in authorization)

        Returns:
            Tuple of (User, TokenResponse)
        """
        try:
            # Exchange authorization code for access token
            google = oauth.google

            # Use configured redirect URI if not provided
            if not redirect_uri:
                redirect_uri = settings.google_redirect_uri

            token = await google.authorize_access_token(
                code=code, redirect_uri=redirect_uri
            )

            # Get user info from Google
            user_info = token.get("userinfo")
            if not user_info:
                # If userinfo not in token, fetch it
                resp = await google.get("https://www.googleapis.com/oauth2/v3/userinfo")
                user_info = resp.json()

            # Create OAuth user info
            oauth_info = OAuthUserInfo(
                provider="google",
                provider_id=user_info["sub"],  # Google's unique user ID
                email=user_info["email"],
                name=user_info.get("name"),
                avatar_url=user_info.get("picture"),
                is_email_verified=user_info.get("email_verified", True),
            )

            # Get or create user
            user = await OAuthService.get_or_create_oauth_user(oauth_info, db)

            # Generate JWT tokens
            tokens = await AuthService._generate_tokens(user, db)

            return user, tokens

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth authentication failed: {str(e)}",
            )

    @staticmethod
    def create_authorization_url(
        request, provider: str = "google", redirect_uri: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create OAuth authorization URL for the specified provider.

        Args:
            request: Starlette/FastAPI request object
            provider: OAuth provider name ('google')
            redirect_uri: Optional custom redirect URI

        Returns:
            Dictionary with 'auth_url' and 'state'
        """
        client = OAuthService.get_oauth_client(provider)

        if not redirect_uri:
            redirect_uri = settings.google_redirect_uri

        # Generate authorization URL
        redirect_uri_obj = client.authorize_redirect(request, redirect_uri)

        return {
            "auth_url": str(redirect_uri_obj.headers["location"]),
            "state": request.session.get("_oauth_state_"),
        }
