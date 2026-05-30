"""Seed demo data for TaskFlow."""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models import Activity, Comment, Notification, Project, ProjectMember, Ticket, User
from app.models.project import MemberRole
from app.models.ticket import Priority, TicketStatus


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).first():
            print("Database already seeded, skipping.")
            return

        users = [
            User(name="John Doe", email="john@taskflow.dev", password_hash=get_password_hash("Password1")),
            User(name="Sarah Chen", email="sarah@taskflow.dev", password_hash=get_password_hash("Password1")),
            User(name="Alex Rivera", email="alex@taskflow.dev", password_hash=get_password_hash("Password1")),
        ]
        for u in users:
            db.add(u)
        db.commit()
        for u in users:
            db.refresh(u)

        john, sarah, alex = users

        project = Project(
            name="E-Commerce Platform",
            description="Modern e-commerce platform rebuild",
            project_key="ECOM",
            owner_id=john.id,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        db.add(ProjectMember(project_id=project.id, user_id=sarah.id, role=MemberRole.ADMIN))
        db.add(ProjectMember(project_id=project.id, user_id=alex.id, role=MemberRole.MEMBER))
        db.commit()

        tickets_data = [
            ("User authentication flow", Priority.HIGH, TicketStatus.IN_PROGRESS, sarah, 5),
            ("Product catalog API", Priority.MEDIUM, TicketStatus.TODO, alex, 8),
            ("Shopping cart persistence", Priority.HIGH, TicketStatus.IN_REVIEW, sarah, 5),
            ("Payment gateway integration", Priority.CRITICAL, TicketStatus.BACKLOG, None, 13),
            ("Order confirmation emails", Priority.LOW, TicketStatus.DONE, alex, 3),
        ]
        tickets = []
        for i, (title, priority, status, assignee, sp) in enumerate(tickets_data, start=1):
            t = Ticket(
                ticket_number=i,
                title=title,
                description=f"Implement {title.lower()} for the e-commerce platform.",
                priority=priority,
                status=status,
                story_points=sp,
                due_date=date.today() + timedelta(days=7 * i),
                project_id=project.id,
                reporter_id=john.id,
                assignee_id=assignee.id if assignee else None,
            )
            db.add(t)
            tickets.append(t)
        db.commit()
        for t in tickets:
            db.refresh(t)

        db.add(
            Comment(
                ticket_id=tickets[0].id,
                user_id=sarah.id,
                content="OAuth2 integration is complete. Moving to JWT refresh tokens next.",
            )
        )
        db.add(
            Comment(
                ticket_id=tickets[2].id,
                user_id=alex.id,
                content="Redis session store looks good in staging. Ready for review.",
            )
        )

        activities = [
            Activity(user_id=john.id, project_id=project.id, action=f"{john.name} created project E-Commerce Platform"),
            Activity(user_id=john.id, ticket_id=tickets[0].id, project_id=project.id, action=f"{john.name} created ticket ECOM-1"),
            Activity(user_id=sarah.id, ticket_id=tickets[0].id, project_id=project.id, action=f"{sarah.name} moved ECOM-1 to In Progress"),
            Activity(user_id=alex.id, ticket_id=tickets[2].id, project_id=project.id, action=f"{alex.name} added a comment on ECOM-3"),
        ]
        for a in activities:
            db.add(a)

        db.add(Notification(user_id=sarah.id, message="You were assigned to ECOM-1"))
        db.add(Notification(user_id=alex.id, message="New comment on ECOM-3"))

        db.commit()
        print("Seed data created successfully!")
        print("Demo accounts: john@taskflow.dev / Password1")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
