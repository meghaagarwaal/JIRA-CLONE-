# TaskFlow – Modern Jira Clone

A production-quality full-stack issue tracking and project management application inspired by Jira, Linear, and GitHub Projects.

## Features

- **Authentication** – JWT with refresh tokens, registration, login, user profiles
- **Project Management** – Create/edit/delete projects, dashboards, member management
- **Ticket Management** – Full CRUD with priority, status, assignee, story points, due dates
- **Kanban Board** – Drag-and-drop with `@dnd-kit`, instant UI updates, persisted to database
- **Comments** – Add, edit, delete comments on tickets
- **Search & Filtering** – Filter by assignee, status, priority, project; search titles/descriptions
- **Activity Timeline** – Chronological feed of all actions
- **Notifications** – In-app notifications for assignments, comments, status changes
- **Dashboard** – Stats cards, pie chart (tickets by status), bar chart (weekly progress) via Recharts
- **Dark/Light Mode** – Theme toggle in navigation

## Tech Stack

| Layer    | Technologies |
|----------|-------------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, ShadCN UI, React Query, React Router, React Hook Form, Zod, Recharts, @dnd-kit |
| Backend  | Python, FastAPI, SQLAlchemy, Pydantic, JWT |
| Database | PostgreSQL |
| Deploy   | Docker, Docker Compose |

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

### Run with Docker (recommended)

```bash
docker-compose up --build
```

Then open:

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Demo Account

After the seed script runs on startup:

```
Email:    john@taskflow.dev
Password: Password1
```

Other demo users: `sarah@taskflow.dev`, `alex@taskflow.dev` (same password)

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Start PostgreSQL and update DATABASE_URL in .env
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server proxies `/api` to `http://localhost:8000`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/refresh` | Refresh token |
| GET | `/api/auth/me` | Current user profile |
| GET/POST | `/api/projects` | List/create projects |
| PUT/DELETE | `/api/projects/{id}` | Update/delete project |
| GET | `/api/projects/{id}/dashboard` | Project dashboard |
| GET/POST | `/api/tickets` | List/create tickets |
| PUT/DELETE | `/api/tickets/{id}` | Update/delete ticket |
| GET/POST | `/api/comments` | Comments |
| GET | `/api/notifications` | Notifications |
| PATCH | `/api/notifications/{id}/read` | Mark notification read |
| GET | `/api/dashboard` | Main dashboard stats |
| GET | `/api/activities` | Activity feed |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/routes/      # REST endpoints
│   │   ├── core/            # Config, DB, security, logging
│   │   ├── models/          # SQLAlchemy models
│   │   ├── repositories/    # Data access layer
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── scripts/seed.py      # Demo data
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/      # UI components
│       ├── lib/             # API client, auth, theme
│       └── pages/           # Route pages
└── docker-compose.yml
```

## Running Tests

```bash
cd backend
pytest
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://taskflow:taskflow@db:5432/taskflow` | PostgreSQL connection |
| `SECRET_KEY` | (required in prod) | JWT signing key |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins |
| `VITE_API_URL` | `/api` | Frontend API base URL |

## License

MIT
