from datetime import date
from pydantic import BaseModel

from app.db.models import LanguagePreference


class UserCreate(BaseModel):
    id: int
    name: str
    password: str
    username: str

class UserResponse(BaseModel):
    id: int
    username: str
    name: str

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