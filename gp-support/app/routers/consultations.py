from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.chat_rules import (
    is_advice_request,
    has_high_severity_rating,
    keep_one_question,
    remove_medical_advice,
    get_missing_background_field,
    background_question,
)

from app.schemas.consultations import ConsultationCreate
from app.schemas.messages import MessageCreate, ChatMessage
from app.repositories import repository
from app.services import chat_service
from app.services.prompts import SYSTEM_PROMPT
from fastapi import Request
from app.services.knowledge_rag import (
    build_query_from_consultation_summary,
    ask_structured,
)


router = APIRouter(prefix="/consultations", tags=["consultations"])


@router.get("/")
def home():
    return {"message": "GP Support API is running"}


@router.post("")
def create_consultation(data: ConsultationCreate,db: Session = Depends(get_db)):
    user = repository.get_user_by_id(db,data.user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    consultation = repository.create_consultation(db,data.user_id)

    return {
        "consultation_id": consultation.id,
        "user_id": consultation.user_id
    }

@router.delete("/{consultation_id}/messages")
def clear_conversation(
    consultation_id: int,
    db: Session = Depends(get_db)
):
    consultation = repository.get_consultation_by_id(
        db,
        consultation_id
    )

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found"
        )

    repository.clear_conversation(
        db,
        consultation
    )

    return {
        "message": "Conversation cleared"
    }


@router.post("/{consultation_id}/messages")
def create_message(
    consultation_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db)
):
    consultation = repository.get_consultation_by_id(
        db,
        consultation_id
    )

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found"
        )

    message = repository.create_message(
        db,
        consultation,
        data.role,
        data.content
    )

    return {
        "message_id": message.id,
        "consultation_id": message.consultation_id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at
    }


@router.get("/{consultation_id}/messages")
def get_messages(
    consultation_id: int,
    db: Session = Depends(get_db)
):
    consultation = repository.get_consultation_by_id(
        db,
        consultation_id
    )

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found"
        )

    messages = repository.get_messages(
        db,
        consultation_id
    )

    return {
        "consultation_id": consultation_id,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at
            }
            for message in messages
        ]
    }


@router.post("/{consultation_id}/chat")
def chat(
    consultation_id: int,
    data: ChatMessage,
    db: Session = Depends(get_db)
):
    consultation = repository.get_consultation_by_id(
        db,
        consultation_id
    )

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found"
        )

    repository.save_user_message(
        db,
        consultation,
        data.message
    )

    messages = repository.get_messages(
        db,
        consultation_id
    )

    prepared_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if is_advice_request(data.message):
        prepared_messages.append(
            {
                "role": "system",
                "content": (
                    "The patient has asked for treatment or medication advice. "
                    "Do not provide medical, medication, or treatment advice. "
                    "Briefly explain that your role is to collect information for the GP. "
                    "Do not ignore other useful information contained in the same patient message. "
                    "Continue the consultation naturally based on that information."
                )
            }
        )

    if has_high_severity_rating(data.message):
        prepared_messages.append(
            {
                "role": "system",
                "content": (
                    "The patient has just reported very high symptom severity. "
                    "Prioritise clarifying this symptom and any associated concerning symptoms "
                    "before moving to routine questions such as medications, allergies, or medical history. "
                    "Ask only one follow-up question."
                )
            }
        )

    prepared_messages.extend(
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    )

    reply = chat_service.chat_aws(prepared_messages)
    reply = remove_medical_advice(reply)
    reply = keep_one_question(reply)

    missing_background = get_missing_background_field(messages)

    reply_lower = reply.lower()

    moving_to_background_or_completion = any(
        phrase in reply_lower
        for phrase in [
            "medical history",
            "medical condition",
            "medication",
            "allerg",
            "anything else",
            "other concerns",
            "before we conclude",
            "before we wrap up",
            "pre-consultation information is complete",
        ]
    )

    if (
        missing_background is not None
        and moving_to_background_or_completion
    ):
        reply = background_question(
            missing_background
        )

    repository.save_assistant_message(
        db,
        consultation,
        reply
    )

    return {
        "reply": reply
    }

@router.get("/{consultation_id}/summary")
def get_summary(
    consultation_id: int,
    db: Session = Depends(get_db)
):
    consultation = repository.get_consultation_by_id(
        db,
        consultation_id
    )

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found"
        )

    messages = repository.get_messages(
        db,
        consultation_id
    )

    prepared_messages = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    ]

    summary = chat_service.summary_aws(
        prepared_messages,
        consultation_id
    )

    return summary

@router.get("/{consultation_id}/rag")
def get_rag_result(
    consultation_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    consultation = repository.get_consultation_by_id(
        db,
        consultation_id
    )

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found"
        )

    messages = repository.get_messages(
        db,
        consultation_id
    )

    prepared_messages = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    ]

    summary = chat_service.summary_aws(
        prepared_messages,
        consultation_id
    )

    query = build_query_from_consultation_summary(
        summary
    )

    result = ask_structured(
        request.app.state.rag_index,
        query
    )

    return {
        "patient_summary": summary,
        "rag_response": result
    }


