# TaskFlow QA Report

**Date:** 2026-05-30  
**Environment:** `docker compose up --build -d`  
**Tester:** Automated (`scripts/qa_test.py`) + container health checks

---

## Infrastructure

| Check | Status | Notes |
|-------|--------|-------|
| PostgreSQL container healthy | **PASS** | `jira-clone--db-1` healthy, `pg_isready` |
| Backend container healthy | **PASS** | Healthcheck `GET /health` 200 |
| Frontend container healthy | **PASS** | nginx + wget healthcheck |
| Seed script executes | **PASS** | Log: `Seed data created successfully!` |

---

## Functional flows (API verification)

| # | Flow | Status | Notes |
|---|------|--------|-------|
| 1 | Login `john@taskflow.dev` / `Password1` | **PASS** | JWT access + refresh returned |
| 2 | Dashboard loads | **PASS** | `GET /api/dashboard` returns stats + charts data |
| 3 | Project list loads | **PASS** | 1 project (E-Commerce Platform) |
| 4 | Ticket creation | **PASS** | Created `ECOM-6` |
| 5 | Kanban status persist | **PASS** | `PUT` status → `In Progress` persisted |
| 6 | Comments save | **PASS** | Create + list returns QA comment |
| 7 | Notifications load | **PASS** | `GET /api/notifications` 200 (0 for john — expected per seed) |
| 8 | Frontend reachable | **PASS** | `http://localhost:5173` returns 200 |
| 9 | Frontend API proxy | **PASS** | `/api/health` and `/api/auth/login` via nginx |

---

## Fixes applied during QA

1. **Docker Compose healthchecks** — DB, backend, frontend with `depends_on: service_healthy`
2. **Backend entrypoint** — Wait for PostgreSQL before seed + uvicorn
3. **JWT `exp`** — Unix timestamp for python-jose compatibility
4. **bcrypt** — Pinned to `4.0.1` for passlib compatibility
5. **FastAPI lifespan** — Replaced deprecated `on_event("startup")`
6. **Ticket filter query** — SQLAlchemy 2.0 `select()` for member project access
7. **Frontend Dockerfile** — `npm ci` fallback, `wget` for healthcheck
8. **Project member `get_member`** — `joinedload` for user relation
9. **Notifications route** — Removed unused imports

---

## Known limitations (non-blocking)

- **Notifications for demo user John:** Seed assigns notifications to Sarah/Alex only; John correctly sees an empty list.
- **UI flows:** Browser drag-and-drop not automated; API-level Kanban persist verified.
- **Docker Desktop:** May require ~2–3 min after install/restart before engine is ready (`hello-world` test).

---

## How to re-run QA

```bash
docker compose up --build -d
# wait until all services healthy
python scripts/qa_test.py http://localhost:8000 http://localhost:5173
```

**Expected:** 13/13 PASS

---

## Result

**All targeted flows PASS** on API and infrastructure level.
