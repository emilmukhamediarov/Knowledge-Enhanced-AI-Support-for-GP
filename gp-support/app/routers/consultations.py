import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.services.chat_service import client
from groq import Groq
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from database import get_db
from models import User, Consultation, Message
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

class ChatMessage(BaseModel):
    message: str

class ConsultationCreate(BaseModel):
    user_id: int

class MessageCreate(BaseModel):
    role: str
    content: str



app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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



@app.get("/")
def home():
    return {"message": "GP Support API is running"}

@app.post("/chat")
def chat(data: ChatMessage):

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

@app.get("/summary")
def get_summary():

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

@app.post("/reset")
def reset_chat():

    del conversation[1:]

    return {
        "message": "Conversation reset"
    }

@app.post("/consultations")
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

@app.post("/consultations/{consultation_id}/messages")
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

@app.get("/consultations/{consultation_id}/messages")
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

@app.post("/consultations/{consultation_id}/chat")
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