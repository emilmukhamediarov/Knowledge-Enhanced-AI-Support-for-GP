from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db.models import User, Consultation, Message


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
    db.execute(text("DELETE FROM data_rag_chunks"))
    db.commit()