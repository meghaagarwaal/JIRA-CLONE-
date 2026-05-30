from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationResponse


class NotificationService:
    def __init__(self, db: Session):
        self.repo = NotificationRepository(db)

    def list_notifications(self, user: User) -> list[NotificationResponse]:
        items = self.repo.list_for_user(user.id)
        return [NotificationResponse.model_validate(n) for n in items]

    def mark_read(self, notification_id: UUID, user: User) -> NotificationResponse:
        notification = self.repo.get_by_id(notification_id)
        if not notification or notification.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        notification.is_read = True
        notification = self.repo.update(notification)
        return NotificationResponse.model_validate(notification)
