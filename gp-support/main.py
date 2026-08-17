from fastapi import FastAPI
from groq import Groq
from pydantic import BaseModel


class ChatMessage(BaseModel):
    message: str

app = FastAPI()
client = Groq()

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
        model="llama-3.1-8b-instant",
        messages=conversation
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
        model="llama-3.1-8b-instant",
        messages=summary_messages,
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