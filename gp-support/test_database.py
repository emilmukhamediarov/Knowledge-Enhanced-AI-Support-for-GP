from sqlalchemy import select
from zoneinfo import ZoneInfo

from database import SessionLocal
from models import User, Consultation, Message


session = SessionLocal()

user = User(name="Bob")

consultation = Consultation(user=user)

message1 = Message(
    consultation=consultation,
    role="user",
    content="I have had a headache for three days."
)

message2 = Message(
    consultation=consultation,
    role="assistant",
    content="How severe is the headache?"
)

session.add(consultation)
session.commit()

consultations = session.scalars(
    select(Consultation)
).all()

for consultation in consultations:

    print("Consultation:", consultation.id)

    for message in consultation.messages:
        auckland = ZoneInfo("Pacific/Auckland")
        print(
            message.role,
            message.content,
            message.created_at.astimezone(auckland).isoformat()
        )


session.close()