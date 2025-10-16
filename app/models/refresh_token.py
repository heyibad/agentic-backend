from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(SQLModel, table=True):
    """Refresh token model for JWT token management."""

    __tablename__ = "refresh_tokens"

    id: UUID = Field(
        default_factory=lambda: __import__("uuid").uuid4(),
        primary_key=True,
        nullable=False,
    )
    user_id: UUID = Field(foreign_key="users.id", nullable=False, ondelete="CASCADE")
    token_hash: str = Field(nullable=False)
    expires_at: datetime = Field(nullable=False)
    revoked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="refresh_tokens")
