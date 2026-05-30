from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.activity import Activity
from app.models.comment import Comment
from app.models.notification import Notification
from app.models.user import User
from app.repositories.activity import ActivityRepository
from app.repositories.comment import CommentRepository
from app.repositories.notification import NotificationRepository
from app.repositories.ticket import TicketRepository
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.ticket_service import TicketService


class CommentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CommentRepository(db)
        self.ticket_repo = TicketRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.notification_repo = NotificationRepository(db)
        self.ticket_service = TicketService(db)

    def _to_response(self, comment: Comment) -> CommentResponse:
        return CommentResponse(
            id=comment.id,
            ticket_id=comment.ticket_id,
            content=comment.content,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            user_id=comment.user_id,
            user_name=comment.user.name,
            user_avatar=comment.user.avatar_url,
        )

    def list_comments(self, ticket_id: UUID, user: User) -> list[CommentResponse]:
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        self.ticket_service._ensure_project_access(ticket.project_id, user)
        return [self._to_response(c) for c in self.repo.list_by_ticket(ticket_id)]

    def create_comment(self, data: CommentCreate, user: User) -> CommentResponse:
        ticket = self.ticket_repo.get_with_relations(data.ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        self.ticket_service._ensure_project_access(ticket.project_id, user)
        comment = Comment(ticket_id=data.ticket_id, user_id=user.id, content=data.content)
        comment = self.repo.create(comment)
        comment = (
            self.db.query(Comment)
            .options(joinedload(Comment.user))
            .filter(Comment.id == comment.id)
            .first()
        )
        key = f"{ticket.project.project_key}-{ticket.ticket_number}"
        self.activity_repo.create(
            Activity(
                user_id=user.id,
                ticket_id=ticket.id,
                project_id=ticket.project_id,
                action=f"{user.name} added a comment on {key}",
            )
        )
        if ticket.assignee_id and ticket.assignee_id != user.id:
            self.notification_repo.create(
                Notification(user_id=ticket.assignee_id, message=f"New comment on {key}")
            )
        if ticket.reporter_id != user.id and ticket.reporter_id != ticket.assignee_id:
            self.notification_repo.create(
                Notification(user_id=ticket.reporter_id, message=f"New comment on {key}")
            )
        return self._to_response(comment)

    def update_comment(self, comment_id: UUID, data: CommentUpdate, user: User) -> CommentResponse:
        comment = self.repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        if comment.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
        comment.content = data.content
        comment = self.repo.update(comment)
        refreshed = (
            self.db.query(Comment)
            .options(joinedload(Comment.user))
            .filter(Comment.id == comment_id)
            .first()
        )
        return self._to_response(refreshed)

    def delete_comment(self, comment_id: UUID, user: User) -> None:
        comment = self.repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        if comment.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
        self.repo.delete(comment)
