from pydantic import BaseModel

class ConsultationCreate(BaseModel):
    user_id: int