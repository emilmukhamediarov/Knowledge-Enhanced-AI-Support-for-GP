import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.services.chat_service import client
from groq import Groq
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from app.db.database import get_db
from app.db.models import User, Consultation, Message

from app.schemas.consultations import ConsultationCreate
from app.schemas.messages import MessageCreate, ChatMessage
from app.dependencies.auth import RequireRole
router = APIRouter(prefix="/consultations", tags=["consultations"])



# Temporary conversation memory
conversation = [
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



@router.get("/")
def home():
    return {"message": "GP Support API is running"}

@router.post("/chat")
# POST /chat
# PURPOSE: Send a message to the AI and get a reply.
# REQUIRED HEADER: { "Authorization": "Bearer <INSERT_TOKEN_FROM_LOCALSTORAGE_HERE>" }
# REQUEST TYPE: JSON
# BODY TO SEND:
# {
#   "message": "I have been experiencing mild headaches."
# }
# EXPECTED RESPONSE: { "reply": "I am sorry to hear that. How long have..." }
# ERROR HANDLING: If you get a 401 or 403 status, the token is expired/missing, so redirect the user to the login screen.
def chat(data: ChatMessage, user = Depends(RequireRole(["patient", "doctor", "admin"]))):

    # Add patient's new message to conversation
    conversation.append(
        {
            "role": "user",
            "content": data.message
        }
    )

    # Send the ENTIRE conversation to Groq
    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=conversation,
        reasoning_format="hidden",
    )

    reply = response.choices[0].message.content

    # Remember the AI response too
    conversation.append(
        {
            "role": "assistant",
            "content": reply
        }
    )

    return {
        "reply": reply
    }

@router.get("/summary")
def get_summary(user = Depends(RequireRole(["doctor", "admin"]))):

    summary_messages = conversation + [
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
    ]

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=summary_messages,
        reasoning_format="hidden",
        response_format={"type": "json_object"}
    )

    return {
        "summary": response.choices[0].message.content
    }

@router.post("/reset")
def reset_chat():

    del conversation[1:]

    return {
        "message": "Conversation reset"
    }

@router.post("/consultations")
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

@router.post("/consultations/{consultation_id}/messages")
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

@router.get("/consultations/{consultation_id}/messages")
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