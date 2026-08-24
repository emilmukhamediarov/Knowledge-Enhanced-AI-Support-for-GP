
from app.schemas.consultations import AnswerList
from pydantic import BaseModel, Field, field_validator




class ConsultationSummary(BaseModel):
    consultation_id: int
    reason_for_visit: str | None = None
    symptoms: list[str] = Field(default_factory=list)
    symptom_location: str | None = None
    onset: str | None = None
    duration: str | None = None
    severity: str | None = None
    medical_history: AnswerList = Field(default_factory=AnswerList)
    current_medications: AnswerList = Field(default_factory=AnswerList)
    allergies: AnswerList = Field(default_factory=AnswerList)
    additional_concerns: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    conversation_complete: bool = False
    summary: str = ""

    @field_validator("symptoms", "missing_information", mode="before")
    @classmethod
    def normalise_lists(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return value

    def calculate_completion(self) -> None:
        missing = []
        if not self.reason_for_visit:
            missing.append("reason_for_visit")
        if not self.symptoms:
            missing.append("symptoms")
        for field_name in ("onset", "duration", "severity"):
            if not getattr(self, field_name):
                missing.append(field_name)
        for field_name in ("medical_history", "current_medications", "allergies"):
            if getattr(self, field_name).status == "unknown":
                missing.append(field_name)
        self.missing_information = missing
        self.conversation_complete = not missing

