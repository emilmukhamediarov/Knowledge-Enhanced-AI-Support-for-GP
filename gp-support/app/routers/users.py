from app.dependencies.auth import require_role
from app.db.models import User, UserRole

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db


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

@router.get("/{patient_id}")
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