from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.notification import Notification
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User
from app.repositories.activity import ActivityRepository
from app.repositories.notification import NotificationRepository
from app.repositories.project import ProjectMemberRepository, ProjectRepository
from app.repositories.ticket import TicketRepository
from app.schemas.ticket import TicketCreate, TicketFilter, TicketListResponse, TicketResponse, TicketUpdate, UserBrief


def ticket_to_response(ticket: Ticket) -> TicketResponse:
    return TicketResponse(
        id=ticket.id,
        ticket_key=f"{ticket.project.project_key}-{ticket.ticket_number}",
        ticket_number=ticket.ticket_number,
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        status=ticket.status,
        story_points=ticket.story_points,
        due_date=ticket.due_date,
        project_id=ticket.project_id,
        project_key=ticket.project.project_key,
        project_name=ticket.project.name,
        reporter=UserBrief.model_validate(ticket.reporter),
        assignee=UserBrief.model_validate(ticket.assignee) if ticket.assignee else None,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TicketRepository(db)
        self.project_repo = ProjectRepository(db)
        self.member_repo = ProjectMemberRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.notification_repo = NotificationRepository(db)

    def _ensure_project_access(self, project_id: UUID, user: User) -> None:
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if project.owner_id == user.id:
            return
        if not self.member_repo.get_member(project_id, user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    def _log_activity(self, user: User, ticket: Ticket, action: str) -> None:
        self.activity_repo.create(
            Activity(
                user_id=user.id,
                ticket_id=ticket.id,
                project_id=ticket.project_id,
                action=action,
            )
        )

    def _notify(self, user_id: UUID, message: str) -> None:
        self.notification_repo.create(Notification(user_id=user_id, message=message))

    def list_tickets(self, filters: TicketFilter, user: User) -> TicketListResponse:
        items, total = self.repo.list_filtered(user.id, filters)
        return TicketListResponse(
            items=[ticket_to_response(t) for t in items],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )

    def get_ticket(self, ticket_id: UUID, user: User) -> TicketResponse:
        ticket = self.repo.get_with_relations(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        self._ensure_project_access(ticket.project_id, user)
        return ticket_to_response(ticket)

    def create_ticket(self, data: TicketCreate, user: User) -> TicketResponse:
        self._ensure_project_access(data.project_id, user)
        number = self.repo.next_ticket_number(data.project_id)
        ticket = Ticket(
            ticket_number=number,
            title=data.title,
            description=data.description,
            priority=data.priority,
            status=data.status,
            story_points=data.story_points,
            due_date=data.due_date,
            project_id=data.project_id,
            reporter_id=user.id,
            assignee_id=data.assignee_id,
        )
        ticket = self.repo.create(ticket)
        ticket = self.repo.get_with_relations(ticket.id)
        key = f"{ticket.project.project_key}-{ticket.ticket_number}"
        self._log_activity(user, ticket, f"{user.name} created ticket {key}")
        if data.assignee_id and data.assignee_id != user.id:
            self._notify(data.assignee_id, f"You were assigned to {key}")
        return ticket_to_response(ticket)

    def update_ticket(self, ticket_id: UUID, data: TicketUpdate, user: User) -> TicketResponse:
        ticket = self.repo.get_with_relations(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        self._ensure_project_access(ticket.project_id, user)
        key = f"{ticket.project.project_key}-{ticket.ticket_number}"
        old_status = ticket.status
        old_assignee = ticket.assignee_id

        if data.title is not None:
            ticket.title = data.title
        if data.description is not None:
            ticket.description = data.description
        if data.priority is not None:
            ticket.priority = data.priority
        if data.status is not None:
            ticket.status = data.status
        if data.story_points is not None:
            ticket.story_points = data.story_points
        if data.due_date is not None:
            ticket.due_date = data.due_date
        if data.assignee_id is not None:
            ticket.assignee_id = data.assignee_id

        ticket = self.repo.update(ticket)
        ticket = self.repo.get_with_relations(ticket.id)

        if data.status and data.status != old_status:
            self._log_activity(user, ticket, f"{user.name} moved {key} to {data.status.value}")
            if ticket.assignee_id:
                self._notify(
                    ticket.assignee_id,
                    f"{key} status changed to {data.status.value}",
                )
        if data.assignee_id and data.assignee_id != old_assignee and data.assignee_id:
            self._notify(data.assignee_id, f"You were assigned to {key}")

        return ticket_to_response(ticket)

    def delete_ticket(self, ticket_id: UUID, user: User) -> None:
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        self._ensure_project_access(ticket.project_id, user)
        self.repo.delete(ticket)

    def list_by_project(self, project_id: UUID, user: User) -> list[TicketResponse]:
        self._ensure_project_access(project_id, user)
        tickets = self.repo.list_by_project(project_id)
        return [ticket_to_response(t) for t in tickets]
