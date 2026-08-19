import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.services.chat_service import client

from app.db.database import get_db
from app.db.models import Consultation, Message, User, Summary

from app.schemas.consultations import ConsultationCreate
from app.schemas.messages import MessageCreate, ChatMessage


router = APIRouter(prefix="/consultations", tags=["consultations"])



@router.post("")
def create_consultation(
    data: ConsultationCreate,
    db: Session = Depends(get_db)
):
    user = db.get(User, data.user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    consultation = Consultation(
        user_id=data.user_id
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    return {
        "consultation_id": consultation.id,
        "user_id": consultation.user_id
    }

@router.post("/{consultation_id}/messages")
def create_message(
    consultation_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db)
):
    consultation = db.get(Consultation, consultation_id)

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found"
        )

    message = Message(
        consultation=consultation,
        role=data.role,
        content=data.content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

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
    consultation = db.get(Consultation, consultation_id)

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found"
        )

    messages = db.scalars(
        select(Message)
        .where(Message.consultation_id == consultation_id)
        .order_by(
            Message.created_at,
            Message.id
        )
    ).all()

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


@router.post("/consultations/{consultation_id}/chat")
def chat(
    consultation_id: int,
    data: ChatMessage,
    db: Session = Depends(get_db)
):
    consultation = db.get(Consultation, consultation_id)

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found"
        )

    user_message = Message(
        consultation=consultation,
        role="user",
        content=data.message
    )

    db.add(user_message)
    db.commit()

    messages = db.scalars(
        select(Message)
        .where(Message.consultation_id == consultation_id)
        .order_by(
            Message.created_at,
            Message.id
        )
    ).all()

    groq_messages = [
        {
            "role": "system",
            "content": """
You are a pre-consultation assistant for a GP clinic.

Your job is to collect relevant information from a patient
before they see their GP.

Ask one short question at a time.

Try to collect:
- main reason for the visit
- symptoms
- when the symptoms started
- severity
- relevant medical history
- current medications
- allergies
- any additional concerns

Do not diagnose the patient.
Do not recommend medication or treatment.

Be polite and conversational.

If the patient has already answered something,
do not ask the same question again.
"""
        }
    ]

    groq_messages.extend(
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    )

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=groq_messages,
        reasoning_format="hidden",
    )

    reply = response.choices[0].message.content

    assistant_message = Message(
        consultation=consultation,
        role="assistant",
        content=reply
    )

    db.add(assistant_message)
    db.commit()

    return {
        "reply": reply
    }

@router.post("/{consultation_id}/summary")
def generate_summary(
    consultation_id: int,
    db: Session = Depends(get_db)
):
    # 1. Make sure the consultation exists
    consultation = db.get(Consultation, consultation_id)

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found"
        )

    # 2. Retrieve the conversation from PostgreSQL
    messages = db.scalars(
        select(Message)
        .where(Message.consultation_id == consultation_id)
        .order_by(
            Message.created_at,
            Message.id
        )
    ).all()

    if not messages:
        raise HTTPException(
            status_code=400,
            detail="Consultation has no messages to summarise"
        )

    # 3. Convert database Message objects into Groq's format
    summary_messages = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    ]

    # 4. Add the summary instruction after the conversation
    summary_messages.append(
        {
            "role": "user",
            "content": """
Create a structured summary of the patient information collected
during this conversation.

Return only valid JSON using exactly this structure:

{
    "main_concern": "",
    "symptoms": [],
    "duration": "",
    "severity": "",
    "medical_history": [],
    "medications": [],
    "allergies": [],
    "additional_concerns": []
}

Only include information actually provided by the patient.
Do not invent missing information.
For information that was not provided, use an empty string or empty list.
"""
        }
    )

    # 5. Ask Groq to generate the summary
    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=summary_messages,
        reasoning_format="hidden",
        response_format={"type": "json_object"}
    )

    summary_content = response.choices[0].message.content

    # 6. Validate that Groq really returned valid JSON
    try:
        summary_json = json.loads(summary_content)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Groq returned an invalid summary format"
        )

    # 7. Check whether this consultation already has a summary
    existing_summary = db.scalar(
        select(Summary)
        .where(Summary.consultation_id == consultation_id)
    )

    # 8. Create or update it
    if existing_summary:
        existing_summary.content = summary_content
        summary = existing_summary
    else:
        summary = Summary(
            consultation=consultation,
            content=summary_content
        )

        db.add(summary)

    db.commit()
    db.refresh(summary)

    # 9. Return the persisted result
    return {
        "summary_id": summary.id,
        "consultation_id": summary.consultation_id,
        "summary": summary_json,
        "created_at": summary.created_at
    }
