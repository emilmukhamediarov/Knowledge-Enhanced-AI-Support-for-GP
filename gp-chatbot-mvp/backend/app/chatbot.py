import json
import threading     #mutiple user
from collections import defaultdict
from typing import Literal

import boto3
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from .config import settings

SYSTEM_PROMPT = """Your name is MidBit. You are a concise GP pre-consultation assistant.

Ask one short, direct question at a time. Collect: reason for visit, symptoms, symptom location when
relevant, onset, duration, severity, medical history, current medications, allergies, and any
additional concerns.

Response style:
- Start directly with the next question.
- Do not use greetings, sympathy, reassurance, acknowledgements, or conversational filler.
- Do not say phrases such as "I'm sorry to hear that", "I understand", "Thank you for sharing",
  "That sounds difficult", or "I appreciate you telling me".
- Do not repeat or summarise the patient's answer before asking the next question.
- Keep each response to one sentence whenever possible.
- Ask only one question per response.
- Prefer plain, short language.

Answer validation:
- Before asking a new question, check whether the patient's latest message actually answers the
  previous question.
- Do not assume a message is an answer merely because it follows a question.
- If the answer is unrelated, unclear, or insufficient, do not move to the next field.
- Rephrase and ask the same question again using simpler words.
- Do not claim that the patient answered the question.
- If the unrelated message contains useful medical information, remember it, but still ask for the
  missing answer.
- If the patient explicitly says "I don't know", "I'm not sure", or refuses to answer, accept the
  field as unknown and move on.

Prioritise missing information and never repeat an answered question. Do not diagnose, prescribe,
or invent information. When all required information has been addressed, say only:
"Your pre-consultation information is complete."

Only assign a patient statement to a field when it semantically answers that field. Do not treat an
unrelated statement following an assistant question as the answer to that question.

If there may be an immediate emergency, briefly advise the patient to contact local emergency
services now. This emergency instruction overrides the normal response style."""

MAX_HISTORY_MESSAGES = 10 #modify later
CHAT_MAX_TOKENS = 150 #modify later
SUMMARY_MAX_TOKENS = 500 #modify later

SUMMARY_PROMPT = """Extract a structured pre-consultation record using ONLY explicit patient
statements in the conversation. Never infer, diagnose, or turn missing information into a negative.
Return exactly one JSON object without markdown using this shape:
{
  "reason_for_visit": string or null,
  "symptoms": array of strings,
  "symptom_location": string or null,
  "onset": string or null,
  "duration": string or null,
  "severity": string or null,
  "medical_history": {"status": "unknown" | "confirmed_none" | "confirmed", "items": array of strings},
  "current_medications": {"status": "unknown" | "confirmed_none" | "confirmed", "items": array of strings},
  "allergies": {"status": "unknown" | "confirmed_none" | "confirmed", "items": array of strings},
  "additional_concerns": string or null,
  "missing_information": array of strings,
  "red_flags": array of explicit concerning patient statements,
  "requires_urgent_attention": boolean,
  "conversation_complete": boolean,
  "summary": concise factual string
}
Use null, an empty array, and status "unknown" for information that was not discussed. Use
"confirmed_none" only when the patient explicitly says none. Do not copy an assistant question
into the record as if it were a patient answer. Return JSON only, without markdown fences.
"""

REQUIRED_INFORMATION = [
    "reason_for_visit",
    "symptoms",
    "onset",
    "duration",
    "severity",
    "medical_history",
    "current_medications",
    "allergies",
]


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


class ConsultationSummary(BaseModel):
    session_id: str
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
    red_flags: list[str] = Field(default_factory=list)
    requires_urgent_attention: bool = False
    conversation_complete: bool = False
    summary: str = ""

    @field_validator("symptoms", "missing_information", "red_flags", mode="before")
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


class ChatService:
    def __init__(self):
        self.client = boto3.client("bedrock-runtime", region_name=settings.aws_region) #creat Bedrock
        self._conversations = defaultdict(list)
        self._lock = threading.RLock()

    def chat(self, session_id: str, text: str) -> str:
        with self._lock:
            full_history = list(self._conversations[session_id])
        recent_history = full_history[-MAX_HISTORY_MESSAGES:]
        recent_history.append({"role": "user", "content": [{"text": text}]})

        #AWS
        response = self.client.converse(
            modelId=settings.bedrock_model_id,
            system=[{"text": SYSTEM_PROMPT}],
            messages=recent_history,
            inferenceConfig={"maxTokens": CHAT_MAX_TOKENS, "temperature": 0.1}, #tem = learning rate
        )

        reply = response["output"]["message"]["content"][0]["text"]
        full_history.extend(
            [
                {"role": "user", "content": [{"text": text}]},
                {"role": "assistant", "content": [{"text": reply}]},
            ]
        )
        with self._lock:
            self._conversations[session_id] = full_history
        return reply

    def summary(self, session_id: str) -> dict:
        with self._lock:
            history = list(self._conversations.get(session_id, []))
        if not history:
            empty_summary = ConsultationSummary(
                session_id=session_id,
                missing_information=REQUIRED_INFORMATION,
                summary="No conversation has been recorded for this session.",
            )
            return empty_summary.model_dump()

        messages = list(history)
        messages.append(
           {
              "role": "user",
              "content": [{"text": SUMMARY_PROMPT}]
           }
        )
        response = self.client.converse(
           modelId=settings.bedrock_model_id,
           messages=messages,
           inferenceConfig={
               "maxTokens": SUMMARY_MAX_TOKENS,
               "temperature": 0
           },
        ) 

        raw = response["output"]["message"]["content"][0]["text"].strip()

        if raw.startswith("```"):
            raw = raw.strip("`").removeprefix("json").strip()
        try:
            payload = json.loads(raw)
            payload["session_id"] = session_id
            validated = ConsultationSummary.model_validate(payload)
            validated.calculate_completion()
            return validated.model_dump()
        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            raise RuntimeError("Model did not return a valid consultation summary") from exc

    def reset(self, session_id: str) -> None:
        with self._lock:
            self._conversations.pop(session_id, None)


chat_service = ChatService()
