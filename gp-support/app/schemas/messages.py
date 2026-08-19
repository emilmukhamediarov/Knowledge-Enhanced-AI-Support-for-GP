from pydantic import BaseModel


class MessageCreate(BaseModel):
    role: str
    content: str

class ChatMessage(BaseModel):
    message: str