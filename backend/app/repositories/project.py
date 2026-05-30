from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.project import Project, ProjectMember
from app.models.ticket import Ticket, TicketStatus
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def get_by_key(self, key: str) -> Project | None:
        return self.db.query(Project).filter(Project.project_key == key.upper()).first()

    def list_for_user(self, user_id: UUID) -> list[Project]:
        owned = self.db.query(Project).filter(Project.owner_id == user_id).all()
        member_ids = (
            self.db.query(ProjectMember.project_id).filter(ProjectMember.user_id == user_id).all()
        )
        member_project_ids = [m[0] for m in member_ids]
        member_projects = (
            self.db.query(Project).filter(Project.id.in_(member_project_ids)).all()
            if member_project_ids
            else []
        )
        seen = {p.id for p in owned}
        return owned + [p for p in member_projects if p.id not in seen]

    def get_with_members(self, project_id: UUID) -> Project | None:
        return (
            self.db.query(Project)
            .options(joinedload(Project.members).joinedload(ProjectMember.user))
            .filter(Project.id == project_id)
            .first()
        )

    def get_stats(self, project_id: UUID) -> dict[str, int]:
        total = self.db.query(func.count(Ticket.id)).filter(Ticket.project_id == project_id).scalar() or 0
        completed = (
            self.db.query(func.count(Ticket.id))
            .filter(Ticket.project_id == project_id, Ticket.status == TicketStatus.DONE)
            .scalar()
            or 0
        )
        return {"total": total, "open": total - completed, "completed": completed}


class ProjectMemberRepository(BaseRepository[ProjectMember]):
    def __init__(self, db: Session):
        super().__init__(db, ProjectMember)

    def get_member(self, project_id: UUID, user_id: UUID) -> ProjectMember | None:
        return (
            self.db.query(ProjectMember)
            .options(joinedload(ProjectMember.user))
            .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
            .first()
        )

    def list_members(self, project_id: UUID) -> list[ProjectMember]:
        return (
            self.db.query(ProjectMember)
            .options(joinedload(ProjectMember.user))
            .filter(ProjectMember.project_id == project_id)
            .all()
        )
