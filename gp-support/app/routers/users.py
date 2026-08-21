from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.users import UserCreate

router = APIRouter(prefix="/users", tags=["users"])



@router.post("")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.get(User, data.id)

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="User with this ID already exists"
        )

    user = User(
        id=data.id,
        name=data.name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "name": user.name
    }