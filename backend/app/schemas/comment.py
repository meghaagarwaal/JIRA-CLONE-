from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    ticket_id: UUID
    content: str = Field(min_length=1, max_length=5000)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime | None = None
    user_id: UUID
    user_name: str
    user_avatar: str | None = None

    model_config = {"from_attributes": True}
