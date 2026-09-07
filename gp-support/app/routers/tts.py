from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.tts_service import (
    TTSServiceError,
    synthesize_speech,
)

router = APIRouter(
    prefix="/tts",
    tags=["tts"],
)

class TTSRequest(BaseModel):
    text: str
    language_code: str = "en-US"

@router.post("/tts")
def synthesize(data: TTSRequest):
    try:
        return synthesize_speech(
            data.text,
            data.language_code
        )

    except TTSServiceError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
