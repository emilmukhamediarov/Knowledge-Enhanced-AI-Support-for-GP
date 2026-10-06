# tests/test_consultations.py

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.main import app
from app.db.models import (
    UserRole,
    ConsultationStatus,
)

from app.dependencies.auth import get_current_user
from app.db.database import get_db


def override_current_user(user):
    def _override():
        return user

    return _override


def override_db(db):
    def _override():
        yield db

    return _override


def make_patient():
    return SimpleNamespace(
        id=1,
        role=UserRole.PATIENT,
    )


def make_doctor():
    return SimpleNamespace(
        id=2,
        role=UserRole.DOCTOR,
    )


def make_consultation(
        user_id=1,
        doctor_id=2,
        status=ConsultationStatus.IN_PROGRESS,
):
    patient_user = SimpleNamespace(
        id=user_id,
        doctor_id=doctor_id,
    )

    return SimpleNamespace(
        id=10,
        user_id=user_id,
        related_consultation_id=None,
        title="Headache",
        status=status,
        created_at=datetime.now(UTC),
        closed_at=None,
        subjective=None,
        objective=None,
        assessment=None,
        plan=None,
        user=patient_user,
    )

def test_create_consultation(client, monkeypatch):

    patient = make_patient()
    consultation = make_consultation()

    def fake_create_consultation(db, user_id):
        return consultation

    monkeypatch.setattr(
        "app.routers.consultations.repository.create_consultation",
        fake_create_consultation,
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    response = client.post(
        "/consultations",
        json={
            "user_id": patient.id,
            "previous_consultation_id": None
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["consultation_id"] == consultation.id
    assert data["user_id"] == patient.id

def test_delete_consultation(client, monkeypatch):

    patient = make_patient()
    consultation = make_consultation()

    db = MagicMock()

    monkeypatch.setattr(
        "app.routers.consultations.repository.get_consultation_by_id",
        lambda db, consultation_id: consultation,
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.delete(
        f"/consultations/{consultation.id}"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["message"] == "Consultation deleted"

    db.delete.assert_called_once()
    db.commit.assert_called_once()


def test_cannot_delete_another_users_consultation(
        client,
        monkeypatch,
):

    patient = make_patient()

    consultation = make_consultation(
        user_id=999
    )

    db = MagicMock()

    monkeypatch.setattr(
        "app.routers.consultations.repository.get_consultation_by_id",
        lambda db, consultation_id: consultation,
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.delete(
        f"/consultations/{consultation.id}"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert (
            response.json()["detail"]
            == "Not allowed to access this consultation"
    )


def test_cannot_delete_ready_consultation(
        client,
        monkeypatch,
):

    patient = make_patient()

    consultation = make_consultation(
        status=ConsultationStatus.READY
    )

    db = MagicMock()

    monkeypatch.setattr(
        "app.routers.consultations.repository.get_consultation_by_id",
        lambda db, consultation_id: consultation,
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.delete(
        f"/consultations/{consultation.id}"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409



def test_clear_conversation(client, monkeypatch):

    patient = make_patient()
    consultation = make_consultation()

    db = MagicMock()

    cleared = {"called": False}

    monkeypatch.setattr(
        "app.routers.consultations.repository.get_consultation_by_id",
        lambda db, consultation_id: consultation,
    )

    def fake_clear_conversation(db, consultation):
        cleared["called"] = True

    monkeypatch.setattr(
        "app.routers.consultations.repository.clear_conversation",
        fake_clear_conversation,
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.delete(
        f"/consultations/{consultation.id}/messages"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["message"] == "Conversation cleared"
    assert cleared["called"] is True
    assert consultation.title is None


def test_doctor_can_close_ready_consultation(
        client,
        monkeypatch,
):

    doctor = make_doctor()

    consultation = make_consultation(
        status=ConsultationStatus.READY
    )

    db = MagicMock()

    monkeypatch.setattr(
        "app.routers.consultations.repository.get_consultation_by_id",
        lambda db, consultation_id: consultation,
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(doctor)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.patch(
        f"/consultations/{consultation.id}/close"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert consultation.status == ConsultationStatus.CLOSED
    assert consultation.closed_at is not None


def test_doctor_cannot_access_unassigned_patient_consultation(
        client,
        monkeypatch,
):

    doctor = make_doctor()

    consultation = make_consultation(
        doctor_id=999
    )

    db = MagicMock()

    monkeypatch.setattr(
        "app.routers.consultations.repository.get_consultation_by_id",
        lambda db, consultation_id: consultation,
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(doctor)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.get(
        f"/consultations/{consultation.id}/subjective"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert (
            response.json()["detail"]
            == "Patient is not assigned to this doctor"
    )


def test_get_subjective(client, monkeypatch):

    doctor = make_doctor()
    consultation = make_consultation()
    consultation.subjective = "Patient reports headaches"

    db = MagicMock()

    monkeypatch.setattr(
        "app.routers.consultations.repository.get_consultation_by_id",
        lambda db, consultation_id: consultation,
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(doctor)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.get(
        f"/consultations/{consultation.id}/subjective"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert (
            response.json()["subjective"]
            == "Patient reports headaches"
    )


def test_update_subjective(client, monkeypatch):

    doctor = make_doctor()
    consultation = make_consultation()

    db = MagicMock()

    monkeypatch.setattr(
        "app.routers.consultations.repository.get_consultation_by_id",
        lambda db, consultation_id: consultation,
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(doctor)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.patch(
        f"/consultations/{consultation.id}/subjective",
        json={
            "subjective": "Updated subjective notes"
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert (
            response.json()["subjective"]
            == "Updated subjective notes"
    )

    db.commit.assert_called_once()
    db.refresh.assert_called_once()


def test_update_plan(client, monkeypatch):

    doctor = make_doctor()
    consultation = make_consultation()

    db = MagicMock()

    monkeypatch.setattr(
        "app.routers.consultations.repository.get_consultation_by_id",
        lambda db, consultation_id: consultation,
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(doctor)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.patch(
        f"/consultations/{consultation.id}/plan",
        json={
            "plan": "Follow up with GP"
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["plan"] == "Follow up with GP"


def test_get_consultation_status(client):

    patient = make_patient()

    consultation = make_consultation()

    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = (
        consultation
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.get(
        f"/consultations/{consultation.id}/status"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["consultation_id"] == consultation.id


def test_consultation_cannot_be_related_to_itself(
        client,
        monkeypatch,
):

    patient = make_patient()
    consultation = make_consultation()

    db = MagicMock()

    monkeypatch.setattr(
        "app.routers.consultations.repository.get_consultation_by_id",
        lambda db, consultation_id: consultation,
    )

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.patch(
        f"/consultations/{consultation.id}/related-consultation",
        json={
            "related_consultation_id": consultation.id
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert (
            response.json()["detail"]
            == "A consultation cannot be related to itself"
    )