from app.db.models import User, UserRole
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.dependencies.auth import require_role, get_current_user
from app.schemas.users import PatientSettingsUpdate


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
                "nationality": patient.nationality,
            }
            for patient in current_user.patients
        ]
    }

@router.get("/patients/{patient_id}")
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
        "name": patient.name,
        "date_of_birth": patient.date_of_birth,
        "nationality": patient.nationality,
        "preferred_language": patient.preferred_language,
        "medical_history": patient.medical_history,
        "allergies": patient.allergies,
        "medications": patient.medications,
    }


@router.get("/me")
def get_my_details(
    current_user: User = Depends(
        require_role([UserRole.PATIENT])
    )
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "date_of_birth": current_user.date_of_birth,
        "nationality": current_user.nationality,
        "preferred_language": current_user.preferred_language,
        "medical_history": current_user.medical_history,
        "allergies": current_user.allergies,
        "medications": current_user.medications,
    }


@router.patch("/me")
def update_my_settings(
    data: PatientSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.PATIENT])
    )
):
    if data.preferred_language is not None:
        current_user.preferred_language = data.preferred_language

    if data.date_of_birth is not None:
        current_user.date_of_birth = data.date_of_birth

    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "name": current_user.name,
        "date_of_birth": current_user.date_of_birth,
        "nationality": current_user.nationality,
        "preferred_language": current_user.preferred_language,
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