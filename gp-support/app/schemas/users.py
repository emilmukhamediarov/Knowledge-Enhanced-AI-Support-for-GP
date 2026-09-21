from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field

from app.db.models import LanguagePreference


class UserCreate(BaseModel):
    id: int
    name: str
    password: str
    username: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    email: EmailStr
    email_verified_at: datetime | None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
    name: str

class PatientSettingsUpdate(BaseModel):
    preferred_language: LanguagePreference | None = None
    date_of_birth: date | None = None


class SendEmailCodeRequest(BaseModel):
    email: EmailStr

class VerifyEmailCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )

class MessageResponse(BaseModel):
    message: str