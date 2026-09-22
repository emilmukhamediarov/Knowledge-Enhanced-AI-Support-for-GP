from typing import Literal
from typing import Optional
from pydantic import BaseModel, Field,  field_validator, model_validator

class ConsultationCreate(BaseModel):
    user_id: int
    previous_consultation_id: Optional[int] = None

class AnswerList(BaseModel):
    status: Literal["unknown", "confirmed_none", "confirmed"] = "unknown"
    items: list[str] = Field(default_factory=list)

    #format validator
    @field_validator("items", mode="before")
    @classmethod
    def normalise_items(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return value

    # check JSON
    @model_validator(mode="after")
    def keep_status_consistent(self):
        if self.items and self.status != "confirmed":
            self.status = "confirmed"
        elif not self.items and self.status == "confirmed":
            self.status = "unknown"
        return self
