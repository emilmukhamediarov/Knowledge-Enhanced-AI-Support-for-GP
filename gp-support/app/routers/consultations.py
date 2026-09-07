import asyncio
import json
from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect, Body

from app.services.transcribe_service import (
    TranscriptionError,
    transcribe_service,
)

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ConsultationStatus
from app.services.chat_rules import (
    is_advice_request,
    has_high_severity_rating,
    keep_one_question,
    remove_medical_advice,
    get_missing_background_field,
)

from app.schemas.messages import MessageCreate, ChatMessage
from app.repositories import repository
from app.services import chat_service
from app.services.prompts import build_system_prompt
from app.services.state_service import get_empty_state
from app.services.knowledge_rag import (
    build_query_from_consultation_summary,
    ask_structured,

)

from app.dependencies.auth import get_current_user, require_role
from app.db import models


router = APIRouter(prefix="/consultations", tags=["consultations"])


def _get_doctor_consultation(
    db: Session,
    consultation_id: int,
    current_user: models.User
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

    if consultation.user.doctor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Patient is not assigned to this doctor"
        )

    return consultation



@router.post("")
def create_consultation(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.PATIENT])
    )
):
    consultation = repository.create_consultation(
        db,
        current_user.id
    )

    return {
        "consultation_id": consultation.id,
        "user_id": consultation.user_id,
        "related_consultation_id": consultation.related_consultation_id,
        "title": consultation.title,
        "status": consultation.status,
        "created_at": consultation.created_at,
        "closed_at": consultation.closed_at,
    }

@router.delete("/{consultation_id}/messages")
def clear_conversation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.PATIENT])
    )
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

    if consultation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to access this consultation"
        )

    repository.clear_conversation(
        db,
        consultation
    )

    return {
        "message": "Conversation cleared"
    }

@router.delete("/{consultation_id}")
def delete_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.PATIENT])
    )
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

    if consultation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to access this consultation"
        )

    db.delete(consultation)
    db.commit()

    return {
        "message": "Consultation deleted"
    }

@router.patch("/{consultation_id}/close")
def close_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.PATIENT])
    )
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

    if consultation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to access this consultation"
        )

    consultation.status = ConsultationStatus.CLOSED
    consultation.closed_at = datetime.now(UTC)

    db.commit()
    db.refresh(consultation)

    return {
        "consultation_id": consultation.id,
        "user_id": consultation.user_id,
        "related_consultation_id": consultation.related_consultation_id,
        "title": consultation.title,
        "status": consultation.status,
        "created_at": consultation.created_at,
        "closed_at": consultation.closed_at,
    }

@router.get("/user/{user_id}")
def get_user_consultations(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user = repository.get_user_by_id(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Patient can only access their own consultations
    if (
        current_user.role == models.UserRole.PATIENT
        and current_user.id != user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not allowed to access this user's consultations"
        )

    # Doctor can only access assigned patients
    if (
        current_user.role == models.UserRole.DOCTOR
        and user.doctor_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Patient is not assigned to this doctor"
        )

    consultations = repository.get_consultations_by_user(
        db,
        user_id
    )

    consultation_list = []

    for consultation in consultations:
        consultation_data = {
            "consultation_id": consultation.id,
            "user_id": consultation.user_id,
            "related_consultation_id": consultation.related_consultation_id,
            "title": consultation.title,
            "status": consultation.status,
            "created_at": consultation.created_at,
            "closed_at": consultation.closed_at,
        }

        if current_user.role == models.UserRole.DOCTOR:
            consultation_data.update({
                "subjective": consultation.subjective,
                "objective": consultation.objective,
                "assessment": consultation.assessment,
                "plan": consultation.plan,
            })

        consultation_list.append(consultation_data)

    return {
        "user_id": user_id,
        "consultations": consultation_list
    }


@router.get("/{consultation_id}/messages")
def get_messages(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
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

    # Patient can only access their own consultation
    if (
        current_user.role == models.UserRole.PATIENT
        and consultation.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not allowed to access this consultation"
        )

    # Doctor can only access consultations of assigned patients
    if (
        current_user.role == models.UserRole.DOCTOR
        and consultation.user.doctor_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Patient is not assigned to this doctor"
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.PATIENT])
    )
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

    # Fetch the user to get their language preference
    user = repository.get_user_by_id(db, consultation.user_id)
    user_lang = user.preferred_language if user else "en-US"

    # Determine the language code to use for the LLM
    language_code = (
        user_lang.value
        if isinstance(user_lang, models.LanguagePreference)
        else user_lang
    )

    # Map the enum to a human-readable language for the LLM
    LANGUAGE_MAP = {
        "en-US": "English (en-US)",
        "zh-CN": "Simplified Chinese (zh-CN)",
        "th-TH": "Thai (th-TH)",
        "ru-RU": "Russian (ru-RU)",
        "es-US": "Spanish (es-US)",
    }

    # Use the mapped language or default to English if not found
    target_language = LANGUAGE_MAP.get(
        language_code,
        "English (en-US)",
    )

    if consultation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to access this consultation"
        )
    # 1. Fetch history BEFORE the new message to calculate current state
    existing_messages = repository.get_messages(db, consultation_id)

    if not existing_messages:
        current_state = get_empty_state()
    else:
        prepared_history = [
            {"role": m.role, "content": m.content}
            for m in existing_messages
        ]
        # Use existing Bedrock summary extraction to populate the state
        current_state = chat_service.summary_aws(prepared_history, consultation_id)

    # Set consultation title once the reason for visit is known
    reason_for_visit = current_state.get(
        "reason_for_visit"
    )

    if (
            consultation.title is None
            and reason_for_visit
    ):
        consultation.title = reason_for_visit[:255]

        db.commit()
        db.refresh(consultation)

    # 2. Save the new user message
    repository.save_user_message(db, consultation, data.message)

    # 3. Fetch the updated history (including the message we just saved)
    all_messages = repository.get_messages(db, consultation_id)

    # 4. Inject the state into the system prompt
    prepared_messages = [
        {
            "role": "system",
            "content": build_system_prompt(target_language, current_state)
        }
    ]

    # Apply safety rule prompts
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

    # Append the actual conversation
    prepared_messages.extend(
        {
            "role": message.role,
            "content": message.content
        }
        for message in all_messages
    )

    # 5. Get the LLM reply
    reply = chat_service.chat_aws(prepared_messages)

    # Clean the reply using your remaining rules
    reply = remove_medical_advice(reply)
    reply = keep_one_question(reply)

    # 6. Save and return
    repository.save_assistant_message(
        db,
        consultation,
        reply
    )

    return {
        "reply": reply,
        "language_code": language_code
    }

@router.get("/{consultation_id}/summary")
def get_summary(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.DOCTOR])
    )
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

    if consultation.user.doctor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Patient is not assigned to this doctor"
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.DOCTOR])
    )
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

    if consultation.user.doctor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Patient is not assigned to this doctor"
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


#audio-stream
@router.websocket("/{consultation_id}/audio-stream")
async def audio_stream(consultation_id: int, websocket: WebSocket):
    """Relay browser PCM audio to Amazon Transcribe in real time."""
    await websocket.accept()

    async def send_transcript(text: str, is_final: bool) -> None:
        await websocket.send_json(
            {"event": "transcript", "text": text, "is_final": is_final}
        )

    try:
        stream, handler = await transcribe_service.start_stream(send_transcript)
        handler_task = asyncio.create_task(handler.handle_events())

        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
            if message.get("bytes") is not None:
                await stream.input_stream.send_audio_event(
                    audio_chunk=message["bytes"]
                )
                continue
            if message.get("text") and json.loads(message["text"]).get("event") == "stop":
                break

        await stream.input_stream.end_stream()
        await handler_task
        await websocket.send_json(
            {"event": "complete", "transcript": handler.transcript}
        )
    except WebSocketDisconnect:
        return
    except Exception as exc:
        await websocket.send_json({"event": "error", "detail": str(exc)})
    finally:
        await websocket.close()

@router.get("/doctor")
def get_doctor_consultations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != models.UserRole.DOCTOR:
        raise HTTPException(
            status_code=403,
            detail="Only doctors can access this endpoint"
        )

    consultations = (
        db.query(
            models.Consultation,
            models.User.name.label("patient_name")
        )
        .join(
            models.User,
            models.Consultation.user_id == models.User.id
        )
        .filter(
            models.User.doctor_id == current_user.id
        )
        .order_by(
            models.Consultation.created_at.desc()
        )
        .all()
    )

    return {
        "consultations": [
            {
                "consultation_id": consultation.id,
                "user_id": consultation.user_id,
                "patient_name": patient_name,
                "related_consultation_id": consultation.related_consultation_id,
                "title": consultation.title,
                "status": consultation.status,
                "created_at": consultation.created_at,
                "closed_at": consultation.closed_at,
                "subjective": consultation.subjective,
                "objective": consultation.objective,
                "assessment": consultation.assessment,
                "plan": consultation.plan,
            }
            for consultation, patient_name in consultations
        ]
    }

@router.get("/{consultation_id}/subjective")
def get_subjective(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.DOCTOR])
    )
):
    consultation = _get_doctor_consultation(
        db,
        consultation_id,
        current_user
    )

    return {
        "subjective": consultation.subjective
    }


@router.patch("/{consultation_id}/subjective")
def update_subjective(
    consultation_id: int,
    subjective: str | None = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.DOCTOR])
    )
):
    consultation = _get_doctor_consultation(
        db,
        consultation_id,
        current_user
    )

    consultation.subjective = subjective

    db.commit()
    db.refresh(consultation)

    return {
        "subjective": consultation.subjective
    }

@router.get("/{consultation_id}/objective")
def get_objective(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.DOCTOR])
    )
):
    consultation = _get_doctor_consultation(
        db,
        consultation_id,
        current_user
    )

    return {
        "objective": consultation.objective
    }


@router.patch("/{consultation_id}/objective")
def update_objective(
    consultation_id: int,
    objective: str | None = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.DOCTOR])
    )
):
    consultation = _get_doctor_consultation(
        db,
        consultation_id,
        current_user
    )

    consultation.objective = objective

    db.commit()
    db.refresh(consultation)

    return {
        "objective": consultation.objective
    }

@router.get("/{consultation_id}/assessment")
def get_assessment(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.DOCTOR])
    )
):
    consultation = _get_doctor_consultation(
        db,
        consultation_id,
        current_user
    )

    return {
        "assessment": consultation.assessment
    }


@router.patch("/{consultation_id}/assessment")
def update_assessment(
    consultation_id: int,
    assessment: str | None = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.DOCTOR])
    )
):
    consultation = _get_doctor_consultation(
        db,
        consultation_id,
        current_user
    )

    consultation.assessment = assessment

    db.commit()
    db.refresh(consultation)

    return {
        "assessment": consultation.assessment
    }

@router.get("/{consultation_id}/plan")
def get_plan(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.DOCTOR])
    )
):
    consultation = _get_doctor_consultation(
        db,
        consultation_id,
        current_user
    )

    return {
        "plan": consultation.plan
    }


@router.patch("/{consultation_id}/plan")
def update_plan(
    consultation_id: int,
    plan: str | None = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.DOCTOR])
    )
):
    consultation = _get_doctor_consultation(
        db,
        consultation_id,
        current_user
    )

    consultation.plan = plan

    db.commit()
    db.refresh(consultation)

    return {
        "plan": consultation.plan
    }

@router.patch("/{consultation_id}/related-consultation")
def update_related_consultation(
    consultation_id: int,
    related_consultation_id: int | None = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role([models.UserRole.PATIENT])
    )
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

    # Patient can only modify their own consultation
    if consultation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to modify this consultation"
        )

    # NULL means remove the relationship
    if related_consultation_id is None:
        consultation.related_consultation_id = None

        db.commit()
        db.refresh(consultation)

        return {
            "consultation_id": consultation.id,
            "related_consultation_id": None
        }

    # Consultation cannot point to itself
    if related_consultation_id == consultation_id:
        raise HTTPException(
            status_code=400,
            detail="A consultation cannot be related to itself"
        )

    related_consultation = repository.get_consultation_by_id(
        db,
        related_consultation_id
    )

    if related_consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Related consultation not found"
        )

    # Related consultation must also belong to this patient
    if related_consultation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to relate to this consultation"
        )

    consultation.related_consultation_id = related_consultation.id

    db.commit()
    db.refresh(consultation)

    return {
        "consultation_id": consultation.id,
        "related_consultation_id": consultation.related_consultation_id
    }