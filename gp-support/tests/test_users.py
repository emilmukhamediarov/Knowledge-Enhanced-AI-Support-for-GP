# tests/test_users.py

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.main import app
from app.db.models import UserRole

from app.dependencies.auth import get_current_user
from app.db.database import get_db


def make_patient():
    return SimpleNamespace(
        id=1,
        username="testpatient",
        name="Test Patient",
        email="patient@example.com",
        role=UserRole.PATIENT,
        date_of_birth=date(2000, 1, 1),
        preferred_language="en-US",
        ethnicity="Test ethnicity",
        medical_history=None,
        allergies=None,
        medications=None,
        doctor_id=None,
    )


def make_doctor():
    return SimpleNamespace(
        id=2,
        username="testdoctor",
        name="Dr Test",
        email="doctor@example.com",
        role=UserRole.DOCTOR,
        date_of_birth=None,
        preferred_language=None,
        ethnicity=None,
        medical_history=None,
        allergies=None,
        medications=None,
        patients=[],
    )


def override_current_user(user):
    def _override():
        return user

    return _override


def override_db(db):
    def _override():
        yield db

    return _override


def test_get_my_details_as_patient(client):

    patient = make_patient()

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    response = client.get("/users/me")

    app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == patient.id
    assert data["username"] == patient.username
    assert data["name"] == patient.name
    assert data["email"] == patient.email


def test_get_my_details_without_token(client):

    response = client.get("/users/me")

    assert response.status_code == 401

def test_update_my_settings(client):

    patient = make_patient()

    db = MagicMock()

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.patch(
        "/users/me",
        json={
            "preferred_language": "zh-CN",
            "ethnicity": "Updated ethnicity",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["preferred_language"] == "zh-CN"
    assert data["ethnicity"] == "Updated ethnicity"

    db.commit.assert_called_once()
    db.refresh.assert_called_once()

def test_patient_can_list_doctors(client):

    patient = make_patient()
    doctor = make_doctor()

    db = MagicMock()

    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        doctor
    ]

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.get("/users/doctors")

    app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert len(data["doctors"]) == 1
    assert data["doctors"][0]["id"] == doctor.id
    assert data["doctors"][0]["name"] == doctor.name


def test_patient_can_assign_doctor(client):

    patient = make_patient()
    doctor = make_doctor()

    db = MagicMock()

    db.get.return_value = doctor

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.put(
        "/users/me/doctor",
        json={
            "doctor_id": doctor.id
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["patient_id"] == patient.id
    assert data["doctor_id"] == doctor.id


def test_assign_nonexistent_doctor(client):

    patient = make_patient()

    db = MagicMock()

    db.get.return_value = None

    app.dependency_overrides[get_current_user] = (
        override_current_user(patient)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.put(
        "/users/me/doctor",
        json={
            "doctor_id": 999999
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "GP not found"

def test_doctor_can_view_assigned_patient(client):

    doctor = make_doctor()
    patient = make_patient()

    patient.doctor_id = doctor.id

    db = MagicMock()
    db.get.return_value = patient

    app.dependency_overrides[get_current_user] = (
        override_current_user(doctor)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.get(
        f"/users/patients/{patient.id}"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == patient.id
    assert data["name"] == patient.name


def test_doctor_cannot_view_another_doctors_patient(client):

    doctor = make_doctor()
    patient = make_patient()

    patient.doctor_id = 999

    db = MagicMock()
    db.get.return_value = patient

    app.dependency_overrides[get_current_user] = (
        override_current_user(doctor)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.get(
        f"/users/patients/{patient.id}"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403

    assert (
            response.json()["detail"]
            == "Patient is not assigned to this doctor"
    )


def test_doctor_can_update_assigned_patient(client):

    doctor = make_doctor()
    patient = make_patient()

    patient.doctor_id = doctor.id

    db = MagicMock()
    db.get.return_value = patient

    app.dependency_overrides[get_current_user] = (
        override_current_user(doctor)
    )

    app.dependency_overrides[get_db] = override_db(db)

    response = client.patch(
        f"/users/patients/{patient.id}",
        json={
            "medical_history": "Updated history",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["medical_history"] == "Updated history"