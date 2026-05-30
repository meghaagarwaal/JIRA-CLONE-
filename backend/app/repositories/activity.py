from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.activity import Activity
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, db: Session):
        super().__init__(db, Activity)

    def list_recent(self, project_id: UUID | None = None, limit: int = 20) -> list[Activity]:
        query = self.db.query(Activity).options(joinedload(Activity.user))
        if project_id:
            query = query.filter(Activity.project_id == project_id)
        return query.order_by(Activity.created_at.desc()).limit(limit).all()

    def list_for_user_projects(self, user_id: UUID, limit: int = 30) -> list[Activity]:
        return (
            self.db.query(Activity)
            .options(joinedload(Activity.user))
            .order_by(Activity.created_at.desc())
            .limit(limit)
            .all()
        )
