from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.comment_service import CommentService

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/ticket/{ticket_id}", response_model=list[CommentResponse])
def list_comments(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CommentService(db).list_comments(ticket_id, current_user)


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CommentService(db).create_comment(data, current_user)


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: UUID,
    data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CommentService(db).update_comment(comment_id, data, current_user)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    CommentService(db).delete_comment(comment_id, current_user)
