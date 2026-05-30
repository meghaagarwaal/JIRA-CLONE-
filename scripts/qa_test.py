#!/usr/bin/env python3
"""End-to-end API QA for TaskFlow."""

import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
FRONTEND = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5173"

results: list[tuple[str, bool, str]] = []


def req(method: str, path: str, data: dict | None = None, token: str | None = None) -> tuple[int, dict | list | str]:
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw
    except Exception as e:
        return 0, str(e)


def check(name: str, ok: bool, detail: str = ""):
    results.append((name, ok, detail))
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def main():
    print(f"QA against API={BASE} Frontend={FRONTEND}\n")

    code, body = req("GET", "/health")
    check("1. Backend health", code == 200 and body.get("status") == "ok", str(body))

    try:
        with urllib.request.urlopen(FRONTEND, timeout=10) as r:
            check("2. Frontend reachable", r.status == 200, f"status {r.status}")
    except Exception as e:
        check("2. Frontend reachable", False, str(e))

    code, body = req("POST", "/api/auth/login", {"email": "john@taskflow.dev", "password": "Password1"})
    token = body.get("access_token") if isinstance(body, dict) else None
    check("3. Login (john@taskflow.dev)", code == 200 and bool(token), str(body)[:200])

    if not token:
        print("\nCannot continue without token.")
        report()
        sys.exit(1)

    code, body = req("GET", "/api/auth/me", token=token)
    check("4. Auth /me", code == 200 and body.get("email") == "john@taskflow.dev", str(body)[:120])

    code, body = req("GET", "/api/dashboard", token=token)
    check("5. Dashboard", code == 200 and "stats" in body, str(body)[:120])

    code, projects = req("GET", "/api/projects", token=token)
    check("6. Project list", code == 200 and isinstance(projects, list) and len(projects) > 0, f"count={len(projects) if isinstance(projects, list) else 0}")

    project_id = projects[0]["id"] if isinstance(projects, list) and projects else None

    if project_id:
        code, body = req("GET", f"/api/projects/{project_id}/dashboard", token=token)
        check("7. Project dashboard", code == 200, str(body)[:80])

        code, tickets = req("GET", f"/api/tickets/project/{project_id}", token=token)
        check("8. Project tickets (Kanban data)", code == 200 and isinstance(tickets, list), f"count={len(tickets) if isinstance(tickets, list) else 0}")

        ticket_id = tickets[0]["id"] if isinstance(tickets, list) and tickets else None

        code, created = req(
            "POST",
            "/api/tickets",
            {
                "title": "QA Test Ticket",
                "description": "Created by qa_test.py",
                "priority": "Medium",
                "status": "Todo",
                "project_id": project_id,
            },
            token=token,
        )
        check("9. Ticket creation", code == 201, str(created)[:120])
        new_id = created.get("id") if isinstance(created, dict) else None

        drag_id = new_id or ticket_id
        if drag_id:
            code, updated = req("PUT", f"/api/tickets/{drag_id}", {"status": "In Progress"}, token=token)
            persisted = isinstance(updated, dict) and updated.get("status") == "In Progress"
            check("10. Kanban status persist (API)", code == 200 and persisted, str(updated)[:120])

            code, body = req(
                "POST",
                "/api/comments",
                {"ticket_id": drag_id, "content": "QA comment from script"},
                token=token,
            )
            check("11. Comment create", code == 201, str(body)[:120])

            code, comments = req("GET", f"/api/comments/ticket/{drag_id}", token=token)
            has_comment = isinstance(comments, list) and any("QA comment" in c.get("content", "") for c in comments)
            check("12. Comments list", code == 200 and has_comment, f"count={len(comments) if isinstance(comments, list) else 0}")

    code, notifs = req("GET", "/api/notifications", token=token)
    check("13. Notifications", code == 200 and isinstance(notifs, list), f"count={len(notifs) if isinstance(notifs, list) else 0}")

    report()
    sys.exit(0 if all(r[1] for r in results) else 1)


def report():
    print("\n" + "=" * 50)
    failed = [r for r in results if not r[1]]
    print(f"Total: {len(results)} | Passed: {len(results) - len(failed)} | Failed: {len(failed)}")
    if failed:
        print("\nFAILURES:")
        for name, _, detail in failed:
            print(f"  - {name}: {detail}")


if __name__ == "__main__":
    main()
