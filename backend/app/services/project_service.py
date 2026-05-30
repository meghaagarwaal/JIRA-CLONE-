from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.project import MemberRole, Project, ProjectMember
from app.models.user import User
from app.repositories.activity import ActivityRepository
from app.repositories.project import ProjectMemberRepository, ProjectRepository
from app.schemas.activity import ActivityResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectDashboard,
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectUpdate,
)


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProjectRepository(db)
        self.member_repo = ProjectMemberRepository(db)
        self.activity_repo = ActivityRepository(db)

    def _to_response(self, project: Project) -> ProjectResponse:
        stats = self.repo.get_stats(project.id)
        members = self.member_repo.list_members(project.id)
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            project_key=project.project_key,
            owner_id=project.owner_id,
            created_at=project.created_at,
            total_tickets=stats["total"],
            open_tickets=stats["open"],
            completed_tickets=stats["completed"],
            member_count=len(members) + 1,
        )

    def _ensure_access(self, project: Project | None, user: User, admin_only: bool = False) -> Project:
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if project.owner_id == user.id:
            return project
        member = self.member_repo.get_member(project.id, user.id)
        if not member:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        if admin_only and member.role != MemberRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        return project

    def list_projects(self, user: User) -> list[ProjectResponse]:
        projects = self.repo.list_for_user(user.id)
        return [self._to_response(p) for p in projects]

    def create_project(self, data: ProjectCreate, user: User) -> ProjectResponse:
        if self.repo.get_by_key(data.project_key):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project key already exists")
        project = Project(
            name=data.name,
            description=data.description,
            project_key=data.project_key.upper(),
            owner_id=user.id,
        )
        project = self.repo.create(project)
        self.activity_repo.create(
            Activity(
                user_id=user.id,
                project_id=project.id,
                action=f"{user.name} created project {project.name}",
            )
        )
        return self._to_response(project)

    def get_project(self, project_id: UUID, user: User) -> ProjectResponse:
        project = self.repo.get_by_id(project_id)
        return self._to_response(self._ensure_access(project, user))

    def get_dashboard(self, project_id: UUID, user: User) -> ProjectDashboard:
        project = self.repo.get_by_id(project_id)
        self._ensure_access(project, user)
        activities = self.activity_repo.list_recent(project_id=project_id, limit=10)
        return ProjectDashboard(
            project=self._to_response(project),
            recent_activity=[
                ActivityResponse(
                    id=a.id,
                    user_id=a.user_id,
                    user_name=a.user.name,
                    ticket_id=a.ticket_id,
                    project_id=a.project_id,
                    action=a.action,
                    created_at=a.created_at,
                )
                for a in activities
            ],
        )

    def update_project(self, project_id: UUID, data: ProjectUpdate, user: User) -> ProjectResponse:
        project = self.repo.get_by_id(project_id)
        self._ensure_access(project, user, admin_only=True)
        if data.name is not None:
            project.name = data.name
        if data.description is not None:
            project.description = data.description
        project = self.repo.update(project)
        return self._to_response(project)

    def delete_project(self, project_id: UUID, user: User) -> None:
        project = self.repo.get_by_id(project_id)
        project = self._ensure_access(project, user, admin_only=True)
        if project.owner_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can delete project")
        self.repo.delete(project)

    def add_member(self, project_id: UUID, data: ProjectMemberCreate, user: User) -> ProjectMemberResponse:
        project = self.repo.get_by_id(project_id)
        self._ensure_access(project, user, admin_only=True)
        if self.member_repo.get_member(project_id, data.user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already a member")
        member = ProjectMember(project_id=project_id, user_id=data.user_id, role=data.role)
        member = self.member_repo.create(member)
        member = self.member_repo.get_member(project_id, data.user_id)
        u = member.user
        return ProjectMemberResponse(
            id=member.id,
            user_id=member.user_id,
            role=member.role,
            name=u.name,
            email=u.email,
            avatar_url=u.avatar_url,
        )

    def list_members(self, project_id: UUID, user: User) -> list[ProjectMemberResponse]:
        project = self.repo.get_by_id(project_id)
        self._ensure_access(project, user)
        members = self.member_repo.list_members(project_id)
        return [
            ProjectMemberResponse(
                id=m.id,
                user_id=m.user_id,
                role=m.role,
                name=m.user.name,
                email=m.user.email,
                avatar_url=m.user.avatar_url,
            )
            for m in members
        ]
