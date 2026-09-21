from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db.models import User, Consultation, Message, Summary


def get_user_by_id(
    db: Session,
    user_id: int
):
    return db.get(User, user_id)


def create_user(
    db: Session,
    user_id: int,
    name: str
):
    user = User(
        id=user_id,
        name=name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_consultation_by_id(
    db: Session,
    consultation_id: int
):
    return db.get(Consultation, consultation_id)

def get_consultations_by_user(
    db: Session,
    user_id: int
):
    return (
        db.query(Consultation)
        .filter(Consultation.user_id == user_id)
        .order_by(Consultation.created_at.desc())
        .all()
    )


def create_consultation(
    db: Session,
    user_id: int
):
    consultation = Consultation(
        user_id=user_id
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    return consultation


def create_message(
    db: Session,
    consultation: Consultation,
    role: str,
    content: str
):
    message = Message(
        consultation=consultation,
        role=role,
        content=content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_messages(
    db: Session,
    consultation_id: int
):
    return db.scalars(
        select(Message)
        .where(Message.consultation_id == consultation_id)
        .order_by(
            Message.created_at,
            Message.id
        )
    ).all()


def clear_conversation(
    db: Session,
    consultation: Consultation
):
    for message in consultation.messages:
        db.delete(message)

    db.commit()


def save_assistant_message(
    db: Session,
    consultation: Consultation,
    content: str
):
    message = Message(
        consultation=consultation,
        role="assistant",
        content=content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def save_user_message(
    db: Session,
    consultation: Consultation,
    content: str
):
    message = Message(
        consultation=consultation,
        role="user",
        content=content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message

def clear_rag_chunks(db: Session):
    table_exists = db.execute(
        text("SELECT to_regclass('public.data_rag_chunks')")
    ).scalar()

    if table_exists:
        db.execute(text("DELETE FROM data_rag_chunks"))
        db.commit()

def get_consultations_by_user_id(
    db: Session,
    user_id: int
):
    return (
        db.query(Consultation)
        .filter(Consultation.user_id == user_id)
        .order_by(Consultation.id.desc())
        .all()
    )

def get_summary_by_consultation_id(
    db: Session,
    consultation_id: int
):
    return db.scalar(
        select(Summary)
        .where(
            Summary.consultation_id == consultation_id
        )
    )


def save_patient_summary(
    db: Session,
    consultation: Consultation,
    patient_summary: dict
):
    summary = get_summary_by_consultation_id(
        db,
        consultation.id
    )

    if summary is None:
        summary = Summary(
            consultation=consultation,
            patient_summary=patient_summary
        )
        db.add(summary)
    else:
        summary.patient_summary = patient_summary

    db.commit()
    db.refresh(summary)

    return summary


def save_rag_response(
    db: Session,
    consultation: Consultation,
    rag_response: dict
):
    summary = get_summary_by_consultation_id(
        db,
        consultation.id
    )

    if summary is None:
        summary = Summary(
            consultation=consultation,
            rag_response=rag_response
        )
        db.add(summary)
    else:
        summary.rag_response = rag_response

    db.commit()
    db.refresh(summary)

    return summary