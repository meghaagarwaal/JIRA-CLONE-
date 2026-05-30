from datetime import UTC, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardStats,
    StatusChartItem,
    WeeklyProgressItem,
)


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard(self, user: User) -> DashboardResponse:
        my_tickets = (
            self.db.query(func.count(Ticket.id)).filter(Ticket.assignee_id == user.id).scalar() or 0
        )
        completed = (
            self.db.query(func.count(Ticket.id))
            .filter(Ticket.assignee_id == user.id, Ticket.status == TicketStatus.DONE)
            .scalar()
            or 0
        )
        open_tickets = my_tickets - completed
        from app.repositories.project import ProjectRepository

        projects = len(ProjectRepository(self.db).list_for_user(user.id))

        status_rows = (
            self.db.query(Ticket.status, func.count(Ticket.id))
            .filter(Ticket.assignee_id == user.id)
            .group_by(Ticket.status)
            .all()
        )
        tickets_by_status = [
            StatusChartItem(status=s.value, count=c) for s, c in status_rows
        ]

        weekly: list[WeeklyProgressItem] = []
        today = datetime.now(UTC).date()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_start = datetime.combine(day, datetime.min.time()).replace(tzinfo=UTC)
            day_end = day_start + timedelta(days=1)
            completed_count = (
                self.db.query(func.count(Ticket.id))
                .filter(
                    Ticket.assignee_id == user.id,
                    Ticket.status == TicketStatus.DONE,
                    Ticket.updated_at >= day_start,
                    Ticket.updated_at < day_end,
                )
                .scalar()
                or 0
            )
            created_count = (
                self.db.query(func.count(Ticket.id))
                .filter(
                    Ticket.reporter_id == user.id,
                    Ticket.created_at >= day_start,
                    Ticket.created_at < day_end,
                )
                .scalar()
                or 0
            )
            weekly.append(
                WeeklyProgressItem(
                    day=day.strftime("%a"),
                    completed=completed_count,
                    created=created_count,
                )
            )

        return DashboardResponse(
            stats=DashboardStats(
                my_tickets=my_tickets,
                completed_tickets=completed,
                open_tickets=open_tickets,
                projects=projects,
            ),
            tickets_by_status=tickets_by_status,
            weekly_progress=weekly,
        )
