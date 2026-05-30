from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.ticket import Priority, TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    status: TicketStatus = TicketStatus.BACKLOG
    assignee_id: UUID | None = None
    project_id: UUID
    story_points: int | None = Field(default=None, ge=0, le=100)
    due_date: date | None = None


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: Priority | None = None
    status: TicketStatus | None = None
    assignee_id: UUID | None = None
    story_points: int | None = Field(default=None, ge=0, le=100)
    due_date: date | None = None


class UserBrief(BaseModel):
    id: UUID
    name: str
    email: str
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class TicketResponse(BaseModel):
    id: UUID
    ticket_key: str
    ticket_number: int
    title: str
    description: str | None
    priority: Priority
    status: TicketStatus
    story_points: int | None
    due_date: date | None
    project_id: UUID
    project_key: str
    project_name: str
    reporter: UserBrief
    assignee: UserBrief | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketFilter(BaseModel):
    assignee_id: UUID | None = None
    status: TicketStatus | None = None
    priority: Priority | None = None
    project_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    search: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    page: int
    page_size: int
