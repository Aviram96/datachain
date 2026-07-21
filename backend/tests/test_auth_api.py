"""Registration and login API tests (in-memory SQLite)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.deps import get_db
from app.main import app

import app.models as _models  # noqa: F401

TEST_PASSWORD = "test-password-12"
TEST_EMAIL = "slice-a@example.com"


@pytest.fixture
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_register_success(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == TEST_EMAIL
    assert "id" in body
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_email(client: TestClient) -> None:
    first = client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert first.status_code == 201

    second = client.post(
        "/auth/register",
        json={"email": "SLICE-A@example.com", "password": TEST_PASSWORD},
    )
    assert second.status_code == 409
    assert "already exists" in second.json()["detail"].lower()


def test_register_password_too_short(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "short-pw@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_register_password_exceeds_bcrypt_bytes(client: TestClient) -> None:
    # 73 ASCII bytes exceeds bcrypt's 72-byte limit enforced in UserRegister.
    response = client.post(
        "/auth/register",
        json={"email": "long-pw@example.com", "password": "x" * 73},
    )
    assert response.status_code == 422


def test_login_success(client: TestClient) -> None:
    register = client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert login.status_code == 200
    body = login.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 0


def test_login_wrong_password(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    login = client.post(
        "/auth/login",
        json={"email": TEST_EMAIL, "password": "wrong-password"},
    )
    assert login.status_code == 401
    assert login.json()["detail"] == "Incorrect email or password."


def test_login_unknown_email(client: TestClient) -> None:
    login = client.post(
        "/auth/login",
        json={"email": "missing@example.com", "password": TEST_PASSWORD},
    )
    assert login.status_code == 401
    assert login.json()["detail"] == "Incorrect email or password."


def test_me_requires_auth(client: TestClient) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_token(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    login = client.post(
        "/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    token = login.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == TEST_EMAIL
