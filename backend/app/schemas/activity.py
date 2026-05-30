from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ActivityResponse(BaseModel):
    id: UUID
    user_id: UUID
    user_name: str
    ticket_id: UUID | None
    project_id: UUID | None
    action: str
    created_at: datetime

    model_config = {"from_attributes": True}
