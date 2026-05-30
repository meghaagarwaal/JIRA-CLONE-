from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.activity import ActivityResponse
from app.schemas.dashboard import DashboardResponse
from app.repositories.activity import ActivityRepository
from app.services.dashboard_service import DashboardService

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).get_dashboard(current_user)


@router.get("/activities", response_model=list[ActivityResponse])
def activities(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = ActivityRepository(db).list_for_user_projects(current_user.id, limit=50)
    return [
        ActivityResponse(
            id=a.id,
            user_id=a.user_id,
            user_name=a.user.name,
            ticket_id=a.ticket_id,
            project_id=a.project_id,
            action=a.action,
            created_at=a.created_at,
        )
        for a in items
    ]
