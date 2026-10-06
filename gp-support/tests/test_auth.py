# tests/test_auth.py

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.main import app
from app.dependencies.db import get_db
from app.db.models import UserRole
from app.services.auth_service import get_password_hash


def make_mock_db(user=None):
    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = user

    return db


def override_db(db):
    def _override():
        yield db

    return _override


def test_login_success(client):

    user = SimpleNamespace(
        id=1,
        username="testpatient",
        name="Test Patient",
        role=UserRole.PATIENT,
        email_verified_at=datetime.now(UTC),
        hashed_password=get_password_hash("Password123!"),
    )

    db = make_mock_db(user)

    app.dependency_overrides[get_db] = override_db(db)

    response = client.post(
        "/auth/login",
        data={
            "username": "testpatient",
            "password": "Password123!",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_id"] == 1
    assert data["name"] == "Test Patient"


def test_login_wrong_password(client):

    user = SimpleNamespace(
        id=1,
        username="testpatient",
        name="Test Patient",
        role=UserRole.PATIENT,
        email_verified_at=datetime.now(UTC),
        hashed_password=get_password_hash("Password123!"),
    )

    db = make_mock_db(user)

    app.dependency_overrides[get_db] = override_db(db)

    response = client.post(
        "/auth/login",
        data={
            "username": "testpatient",
            "password": "WRONGPASSWORD",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_unknown_username(client):

    db = make_mock_db(None)

    app.dependency_overrides[get_db] = override_db(db)

    response = client.post(
        "/auth/login",
        data={
            "username": "doesnotexist",
            "password": "Password123!",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 401


def test_login_unverified_email(client):

    user = SimpleNamespace(
        id=1,
        username="unverified",
        name="Unverified User",
        role=UserRole.PATIENT,
        email_verified_at=None,
        hashed_password=get_password_hash("Password123!"),
    )

    db = make_mock_db(user)

    app.dependency_overrides[get_db] = override_db(db)

    response = client.post(
        "/auth/login",
        data={
            "username": "unverified",
            "password": "Password123!",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert (
            response.json()["detail"]
            == "Please verify your email before logging in"
    )