from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Enumerates the supported message roles for a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageStatus(str, Enum):
    """Enumerates lifecycle statuses for a message."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ConversationVisibility(str, Enum):
    """Visibility options for a conversation thread."""

    PRIVATE = "private"
    SHARED = "shared"


class MessageMetadata(BaseModel):
    """Client-supplied metadata captured alongside a message."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    tags: list[str] = Field(default_factory=list)
    client: Optional[str] = None
    extras: dict[str, Any] = Field(default_factory=dict)


class ProviderMetadata(BaseModel):
    """Model/provider level metadata returned by the LLM provider."""

    provider: Optional[str] = None
    model: Optional[str] = None
    latency_ms: Optional[float] = Field(default=None, ge=0)
    raw: Optional[dict[str, Any]] = None


class ConversationBase(BaseModel):
    """Shared conversation fields."""

    title: Optional[str] = Field(default=None, max_length=200)
    model: str = Field(default="gpt-4o-mini", max_length=100)
    system_prompt: Optional[str] = None
    visibility: ConversationVisibility = ConversationVisibility.PRIVATE


class ConversationCreate(ConversationBase):
    """Payload for creating a conversation."""

    user_id: UUID


class ConversationResponse(ConversationBase):
    """Conversation details returned to clients."""

    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    """Shared message attributes."""

    conversation_id: UUID
    role: MessageRole = MessageRole.USER
    content: str = Field(..., min_length=1, max_length=16000)
    metadata: Optional[MessageMetadata] = None


class ChatMessageCreate(ChatMessageBase):
    """Payload for persisting a new message."""

    author_id: Optional[UUID] = None


class ChatMessageUpdate(BaseModel):
    """Subset of message fields that can be updated."""

    status: Optional[MessageStatus] = None
    tokens: Optional[int] = Field(default=None, ge=0)
    provider_meta: Optional[dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    """Message representation returned via the API."""

    id: UUID
    conversation_id: UUID
    role: MessageRole = MessageRole.USER
    content: str = Field(default="", min_length=0)  # Allow empty for streaming
    author_id: Optional[UUID] = None
    tokens: int = 0
    status: MessageStatus = MessageStatus.COMPLETED
    provider_meta: Optional[dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatPrompt(BaseModel):
    """Input payload accepted by the synchronous chat endpoint."""

    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation to append to. When omitted, a new conversation should be created upstream.",
    )
    author_id: Optional[UUID] = None
    text: str = Field(..., min_length=1, max_length=16000)
    metadata: Optional[MessageMetadata] = None
    tags: list[str] = Field(default_factory=list)


class ChatCompletionResponse(BaseModel):
    """Structured response for a chat turn."""

    conversation: ConversationResponse
    request_message: ChatMessageResponse
    response_message: ChatMessageResponse


class ChatStreamDelta(BaseModel):
    """Delta chunk emitted when streaming assistant responses."""

    conversation_id: UUID
    message_id: UUID
    delta: str
    done: bool = False
    metadata: Optional[ProviderMetadata] = None
