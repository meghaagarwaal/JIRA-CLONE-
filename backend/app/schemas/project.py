from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.project import MemberRole


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    project_key: str = Field(min_length=2, max_length=10, pattern=r"^[A-Z][A-Z0-9]*$")


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectMemberCreate(BaseModel):
    user_id: UUID
    role: MemberRole = MemberRole.MEMBER


class ProjectMemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    role: MemberRole
    name: str
    email: str
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    project_key: str
    owner_id: UUID
    created_at: datetime
    total_tickets: int = 0
    open_tickets: int = 0
    completed_tickets: int = 0
    member_count: int = 0

    model_config = {"from_attributes": True}


class ProjectDashboard(BaseModel):
    project: ProjectResponse
    recent_activity: list["ActivityResponse"] = []


from app.schemas.activity import ActivityResponse  # noqa: E402

ProjectDashboard.model_rebuild()
