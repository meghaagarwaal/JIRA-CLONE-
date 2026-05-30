from datetime import date
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.project import Project
from app.models.ticket import Priority, Ticket, TicketStatus
from app.repositories.base import BaseRepository
from app.schemas.ticket import TicketFilter


class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, db: Session):
        super().__init__(db, Ticket)

    def next_ticket_number(self, project_id: UUID) -> int:
        last = (
            self.db.query(Ticket.ticket_number)
            .filter(Ticket.project_id == project_id)
            .order_by(Ticket.ticket_number.desc())
            .first()
        )
        return (last[0] + 1) if last else 1

    def get_with_relations(self, ticket_id: UUID) -> Ticket | None:
        return (
            self.db.query(Ticket)
            .options(
                joinedload(Ticket.reporter),
                joinedload(Ticket.assignee),
                joinedload(Ticket.project),
            )
            .filter(Ticket.id == ticket_id)
            .first()
        )

    def list_filtered(self, user_id: UUID, filters: TicketFilter) -> tuple[list[Ticket], int]:
        query = (
            self.db.query(Ticket)
            .join(Project)
            .options(
                joinedload(Ticket.reporter),
                joinedload(Ticket.assignee),
                joinedload(Ticket.project),
            )
        )

        from sqlalchemy import select

        from app.models.project import ProjectMember

        member_project_ids = select(ProjectMember.project_id).where(ProjectMember.user_id == user_id)
        query = query.filter(
            or_(Project.owner_id == user_id, Project.id.in_(member_project_ids))
        )

        if filters.assignee_id:
            query = query.filter(Ticket.assignee_id == filters.assignee_id)
        if filters.status:
            query = query.filter(Ticket.status == filters.status)
        if filters.priority:
            query = query.filter(Ticket.priority == filters.priority)
        if filters.project_id:
            query = query.filter(Ticket.project_id == filters.project_id)
        if filters.date_from:
            query = query.filter(Ticket.created_at >= filters.date_from)
        if filters.date_to:
            query = query.filter(Ticket.created_at <= filters.date_to)
        if filters.search:
            term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Ticket.title.ilike(term),
                    Ticket.description.ilike(term),
                    Project.name.ilike(term),
                )
            )

        total = query.count()
        offset = (filters.page - 1) * filters.page_size
        items = (
            query.order_by(Ticket.updated_at.desc()).offset(offset).limit(filters.page_size).all()
        )
        return items, total

    def list_by_project(self, project_id: UUID) -> list[Ticket]:
        return (
            self.db.query(Ticket)
            .options(
                joinedload(Ticket.reporter),
                joinedload(Ticket.assignee),
                joinedload(Ticket.project),
            )
            .filter(Ticket.project_id == project_id)
            .order_by(Ticket.ticket_number)
            .all()
        )
