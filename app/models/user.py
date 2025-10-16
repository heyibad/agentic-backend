from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.models.base import UUIDModel

if TYPE_CHECKING:
    from app.models.refresh_token import RefreshToken
    from app.models.conversation import Conversation
    from app.models.message import Message


class User(UUIDModel, table=True):
    """User model for authentication and profile - OAuth friendly."""

    __tablename__ = "users"

    email: str = Field(unique=True, index=True, nullable=False)
    is_email_verified: bool = Field(default=False)
    password_hash: Optional[str] = Field(
        default=None, nullable=True
    )  # null for OAuth-only users
    name: Optional[str] = Field(default=None, nullable=True)
    avatar_url: Optional[str] = Field(default=None, nullable=True)

    # OAuth fields
    oauth_provider: Optional[str] = Field(
        default=None, nullable=True
    )  # 'google', 'github', etc.
    oauth_id: Optional[str] = Field(
        default=None, nullable=True, index=True
    )  # Provider's user ID
    is_oauth_user: bool = Field(default=False)  # True if user registered via OAuth

    # Relationships
    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    conversations: list["Conversation"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    messages: list["Message"] = Relationship(back_populates="author")
