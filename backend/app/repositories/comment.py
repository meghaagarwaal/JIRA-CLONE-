from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: Session):
        super().__init__(db, Comment)

    def list_by_ticket(self, ticket_id: UUID) -> list[Comment]:
        return (
            self.db.query(Comment)
            .options(joinedload(Comment.user))
            .filter(Comment.ticket_id == ticket_id)
            .order_by(Comment.created_at.asc())
            .all()
        )
