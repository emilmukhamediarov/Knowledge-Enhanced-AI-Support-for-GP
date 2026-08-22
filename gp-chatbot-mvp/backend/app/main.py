import asyncio

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .chatbot import ConsultationSummary, chat_service
from .config import settings
from .transcribe import TranscriptionError, transcribe_service
from app.knowledge_rag import (
    build_query_from_consultation_summary,
    ask_structured,
    build_index
)

app = FastAPI(title="GP Chatbot MVP", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=50)
    message: str = Field(min_length=1, max_length=100)


class SessionRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        reply = await asyncio.to_thread(
            chat_service.chat, request.session_id, request.message.strip()
        )
        return {"reply": reply}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Bedrock request failed: {exc}") from exc


async def get_transcript(audio: UploadFile) -> str:
    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="Say something??")
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Say too much. ")
    try:
        return await asyncio.to_thread(
            transcribe_service.transcribe_upload, audio, content
        )
    except TranscriptionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/audio-chat")
async def audio_chat(session_id: str = Form(...), audio: UploadFile = File(...)):
    transcript = await get_transcript(audio)
    try:
        reply = await asyncio.to_thread(chat_service.chat, session_id, transcript)
        return {"transcript": transcript, "reply": reply}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Bedrock request failed: {exc}") from exc


@app.post("/rag-summary")
async def rag_summary(request: SessionRequest):
    try:
        # get patient summary from chatbot
        summary = await asyncio.to_thread(
            chat_service.summary,
            request.session_id
        )
        # convert summary to RAG query
        query = build_query_from_consultation_summary(
            summary
        )
        # ask RAG
        result = ask_structured(
            index,
            query
        )
        return {
            "patient_summary": summary,
            "rag_response": result
        }
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"RAG request failed: {exc}"
        )


@app.post("/reset")
def reset(request: SessionRequest):
    chat_service.reset(request.session_id)
    return {"status": "reset"}


@app.on_event("startup")
async def startup_event():
    global index
    index = build_index()
