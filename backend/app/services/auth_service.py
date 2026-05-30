from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, data: UserRegister) -> UserResponse:
        if self.repo.get_by_email(data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user = User(
            name=data.name,
            email=data.email,
            password_hash=get_password_hash(data.password),
        )
        user = self.repo.create(user)
        return UserResponse.model_validate(user)

    def login(self, data: UserLogin) -> TokenResponse:
        user = self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        user_id = UUID(payload["sub"])
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    def get_profile(self, user: User) -> dict:
        from sqlalchemy import func

        from app.models.project import Project
        from app.models.ticket import Ticket

        db = self.repo.db
        projects_count = db.query(func.count(Project.id)).filter(Project.owner_id == user.id).scalar() or 0
        assigned_count = db.query(func.count(Ticket.id)).filter(Ticket.assignee_id == user.id).scalar() or 0
        return {
            **UserResponse.model_validate(user).model_dump(),
            "created_projects_count": projects_count,
            "assigned_tickets_count": assigned_count,
        }
