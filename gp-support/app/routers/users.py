from app.db.models import User, UserRole
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.dependencies.auth import require_role, get_current_user
from datetime import date
from app.schemas.users import (
    UserDetailsResponse,
    PatientDetailsUpdate,
    DoctorPatientDetailsUpdate,
)


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/me/patients")
def get_my_patients(
    current_user: User = Depends(
        require_role([UserRole.DOCTOR])
    )
):
    return {
        "patients": [
            {
                "id": patient.id,
                "name": patient.name,
                "date_of_birth": patient.date_of_birth,
                "age": calculate_age(patient.date_of_birth),
                "ethnicity": patient.ethnicity,
            }
            for patient in current_user.patients
        ]
    }

@router.get(
    "/patients/{patient_id}",
    response_model=UserDetailsResponse
)
def get_patient_details(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.DOCTOR])
    )
):
    patient = db.get(User, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    if patient.doctor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Patient is not assigned to this doctor"
        )

    return {
        "id": patient.id,
        "username": patient.username,
        "name": patient.name,
        "email": patient.email,
        "date_of_birth": patient.date_of_birth,
        "age": calculate_age(patient.date_of_birth),
        "preferred_language": patient.preferred_language,
        "ethnicity": patient.ethnicity,
        "medical_history": patient.medical_history,
        "allergies": patient.allergies,
        "medications": patient.medications,
    }


@router.get("/me", response_model=UserDetailsResponse)
def get_my_details(
    current_user: User = Depends(
        require_role([UserRole.PATIENT, UserRole.DOCTOR])
    )
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "name": current_user.name,
        "email": current_user.email,
        "date_of_birth": current_user.date_of_birth,
        "age": calculate_age(current_user.date_of_birth),
        "preferred_language": current_user.preferred_language,
        "ethnicity": current_user.ethnicity,
        "medical_history": current_user.medical_history,
        "allergies": current_user.allergies,
        "medications": current_user.medications,
    }


@router.patch("/me", response_model=UserDetailsResponse)
def update_my_settings(
    data: PatientDetailsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.PATIENT, UserRole.DOCTOR])
    )
):
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "username": current_user.username,
        "name": current_user.name,
        "email": current_user.email,
        "date_of_birth": current_user.date_of_birth,
        "age": calculate_age(current_user.date_of_birth),
        "preferred_language": current_user.preferred_language,
        "ethnicity": current_user.ethnicity,
        "medical_history": current_user.medical_history,
        "allergies": current_user.allergies,
        "medications": current_user.medications,
    }

@router.get("/doctors")
def list_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.PATIENT])
    ),
):
    doctors = (
        db.query(User)
        .filter(User.role == UserRole.DOCTOR)
        .order_by(User.name)
        .all()
    )

    return {
        "doctors": [
            {
                "id": doctor.id,
                "name": doctor.name,
                "username": doctor.username,
            }
            for doctor in doctors
        ]
    }

@router.put("/me/doctor")
def assign_my_doctor(
    doctor_id: int = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.PATIENT])
    ),
):
    doctor = db.get(User, doctor_id)

    if doctor is None or doctor.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=404,
            detail="GP not found",
        )

    current_user.doctor_id = doctor.id
    db.commit()
    db.refresh(current_user)

    return {
        "patient_id": current_user.id,
        "doctor_id": current_user.doctor_id,
    }

def calculate_age(date_of_birth: date | None) -> int | None:
    if date_of_birth is None:
        return None

    today = date.today()

    return (
        today.year
        - date_of_birth.year
        - (
            (today.month, today.day)
            < (date_of_birth.month, date_of_birth.day)
        )
    )


@router.patch(
    "/patients/{patient_id}",
    response_model=UserDetailsResponse
)
def update_patient_details(
    patient_id: int,
    data: DoctorPatientDetailsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.DOCTOR])
    )
):
    patient = db.get(User, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    if patient.doctor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Patient is not assigned to this doctor"
        )

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)

    return {
        "id": patient.id,
        "username": patient.username,
        "name": patient.name,
        "email": patient.email,
        "date_of_birth": patient.date_of_birth,
        "age": calculate_age(patient.date_of_birth),
        "preferred_language": patient.preferred_language,
        "ethnicity": patient.ethnicity,
        "medical_history": patient.medical_history,
        "allergies": patient.allergies,
        "medications": patient.medications,
    }

@router.get("/me/doctor")
def get_my_doctor(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.PATIENT])
    ),
):
    if current_user.doctor_id is None:
        return {"doctor": None}

    doctor = db.get(User, current_user.doctor_id)

    if doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return {
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "username": doctor.username,
            "email": doctor.email,
        }
    }