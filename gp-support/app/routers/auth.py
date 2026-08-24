from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.db import models
from app.schemas.users import UserCreate, UserResponse, Token
from app.services.auth_service import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# """
#  default role is patient
# POST /auth/register
# PURPOSE: Create a new patient account.
# REQUEST TYPE: JSON
# BODY TO SEND:
# {
#     "username": "John10",
#     "name": "John Doe",
#     "password": "password123"
# }
# EXPECTED RESPONSE: { "id": 1, "username": "John10", "name": "John Doe" }
# """
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = models.User(
        username=user_data.username,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
# POST /auth/login
# PURPOSE: Log in and get the security token.
# CRITICAL NOTE: This endpoint requires FormData (application/x-www-form-urlencoded), NOT JSON
# BODY TO SEND (FormData): username=John10 & password=password123
# EXPECTED RESPONSE: { "access_token": "eyJhb...", "token_type": "bearer" }
# ACTION REQUIRED: Save 'access_token' to localStorage immediately upon success.
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}