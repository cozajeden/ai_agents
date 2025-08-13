from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

class TimestampMixin:
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ModelRequest(SQLModel, TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    model_name: str = Field(index=True)
    prompt: str
    response: Optional[str] = None
    status: str = Field(default="pending")
    processing_time: Optional[float] = None
    tokens_used: Optional[int] = None
    error_message: Optional[str] = None

class ChatInteraction(SQLModel, TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(default_factory=lambda: str(uuid4()), index=True)
    model_name: str = Field(index=True)
    user_message: str
    ai_response: str
    conversation_history: Optional[str] = Field(default=None)
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
