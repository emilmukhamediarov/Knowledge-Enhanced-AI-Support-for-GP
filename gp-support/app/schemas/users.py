from pydantic import BaseModel


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