from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class TimestampedModel(SQLModel):
    """Base model with timestamp fields - created_at only to match database schema."""

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class UUIDModel(TimestampedModel):
    """Base model with UUID primary key and timestamps."""

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
