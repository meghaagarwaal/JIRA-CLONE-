import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine, SessionLocal
from app.main import app


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login(client):
    register = client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "Password1"},
    )
    assert register.status_code == 201
    assert register.json()["email"] == "test@example.com"

    login = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "Password1"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()

    token = login.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["name"] == "Test User"


def test_weak_password_rejected(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Bad", "email": "bad@example.com", "password": "weak"},
    )
    assert response.status_code == 422
