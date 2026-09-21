from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.db import models
from app.schemas.users import UserCreate, UserResponse, Token, SendEmailCodeRequest, VerifyEmailCodeRequest, MessageResponse
from app.services.auth_service import get_password_hash, verify_password, create_access_token

from app.services.email_service import EmailDeliveryError
from app.services.email_validate_service import (
    InvalidVerificationCodeError,
    VerificationError,
    VerificationTooSoonError,
    issue_verification_code,
    normalize_email,
    verify_email_code,
)

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
    
    email = normalize_email(str(user_data.email))
    if (db.query(models.User).filter(func.lower(models.User.email) == email).first()):
        raise HTTPException(status_code=400,detail="Email already registered",)

    new_user = models.User(
        username=user_data.username,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
        email=email,
        email_verified_at=None,  # Email is not verified upon registration
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
# EXPECTED RESPONSE: { "access_token": "eyJhb...", "token_type": "bearer", "user_id": 1 }
# ACTION REQUIRED: Save 'access_token' to localStorage immediately upon success.
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if user.email_verified_at is None:
        raise HTTPException(status_code=403,detail="Please verify your email before logging in",)
    
    token = create_access_token(data={"sub": user.username, "role": user.role})

    return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "role": user.role,
            "name": user.name
        }


@router.post(
    "/send-code",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def send_code(
    data: SendEmailCodeRequest,
    db: Session = Depends(get_db),
):
    email = normalize_email(str(data.email))
    user = (
        db.query(models.User)
        .filter(func.lower(models.User.email) == email)
        .first()
    )

    if user is None:
        raise HTTPException(status_code=404,detail="User not found",)

    if user.email_verified_at is not None:
        raise HTTPException(status_code=400,detail="You have already verified your email, go to reset password or login",)

    try:
        issue_verification_code(
            db=db,
            email=email,
        )

    except VerificationTooSoonError as exc:
        raise HTTPException(status_code=429,detail=str(exc),) from exc

    except EmailDeliveryError as exc:
        raise HTTPException(status_code=502,detail="Unable to send verification email",) from exc

    return {
        "message": "Verification code sent",
    }


@router.post(
    "/verify-code",
    response_model=MessageResponse,
)
def verify_code(
    data: VerifyEmailCodeRequest,
    db: Session = Depends(get_db),
):
    try:
        verify_email_code(db=db,email=str(data.email), code=data.code)

    except InvalidVerificationCodeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except VerificationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "message": "Email verified successfully",
    }