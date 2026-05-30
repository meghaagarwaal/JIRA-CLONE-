from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.ticket import Priority, TicketStatus
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketFilter, TicketListResponse, TicketResponse, TicketUpdate
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=TicketListResponse)
def list_tickets(
    assignee_id: UUID | None = None,
    status: TicketStatus | None = None,
    priority: Priority | None = None,
    project_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    filters = TicketFilter(
        assignee_id=assignee_id,
        status=status,
        priority=priority,
        project_id=project_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
        page=page,
        page_size=page_size,
    )
    return TicketService(db).list_tickets(filters, current_user)


@router.get("/project/{project_id}", response_model=list[TicketResponse])
def list_project_tickets(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TicketService(db).list_by_project(project_id, current_user)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TicketService(db).get_ticket(ticket_id, current_user)


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TicketService(db).create_ticket(data, current_user)


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: UUID,
    data: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TicketService(db).update_ticket(ticket_id, data, current_user)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    TicketService(db).delete_ticket(ticket_id, current_user)
