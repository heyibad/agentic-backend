from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlmodel import Field, Relationship
from app.models.base import UUIDModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.message import Message


class Conversation(UUIDModel, table=True):
    """Conversation model for AI chat sessions."""

    __tablename__ = "conversations"

    user_id: UUID = Field(foreign_key="users.id", nullable=False, ondelete="CASCADE")
    title: Optional[str] = Field(default=None, nullable=True)
    model: str = Field(default="gpt-4o-mini")
    system_prompt: Optional[str] = Field(default=None, nullable=True)
    visibility: str = Field(default="private")  # private/shared

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
