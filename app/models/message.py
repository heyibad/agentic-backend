from typing import Optional, Any, TYPE_CHECKING
from uuid import UUID
from sqlmodel import Field, Relationship
from sqlalchemy import Index, Column, JSON
from app.models.base import UUIDModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.conversation import Conversation


class Message(UUIDModel, table=True):
    """Message model for conversation messages."""

    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
        Index("ix_messages_author", "author_id"),
    )

    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False)
    author_id: Optional[UUID] = Field(
        default=None, foreign_key="users.id", nullable=True
    )
    role: str = Field(nullable=False)  # 'user'|'assistant'|'system'
    content: Optional[str] = Field(default=None, nullable=True)
    tokens: int = Field(default=0)
    status: str = Field(default="completed")  # pending/completed/failed
    provider_meta: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )  # JSONB in PostgreSQL

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
    author: Optional["User"] = Relationship(back_populates="messages")
