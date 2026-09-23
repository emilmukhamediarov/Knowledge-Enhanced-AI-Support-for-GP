from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, model_validator

from app.db.models import LanguagePreference


class UserCreate(BaseModel):
    name: str
    password: str
    username: str
    email: EmailStr
    validation_code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )

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
    username: str | None = None

class VerifyEmailCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )

class MessageResponse(BaseModel):
    message: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")
    
    new_password: str
    confirm_password: str

    @model_validator(mode="after")
    def check_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self