from datetime import datetime, UTC

from sqlalchemy import String, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    consultations: Mapped[list["Consultation"]] = relationship(
        back_populates="user"
    )


class Consultation(Base):
    __tablename__ = "consultations"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    user: Mapped["User"] = relationship(
        back_populates = "consultations"
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="consultation"
    )

    summary: Mapped["Summary | None"] = relationship(
        back_populates="consultation"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    consultation_id: Mapped[int] = mapped_column(
        ForeignKey("consultations.id")
    )

    role: Mapped[str]  = mapped_column(String(20))

    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    consultation: Mapped["Consultation"] = relationship(
        back_populates="messages"
    )

class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(primary_key=True)

    consultation_id: Mapped[int] = mapped_column(
        ForeignKey("consultations.id")
    )

    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    consultation: Mapped["Consultation"] = relationship(
        back_populates="summary"
    )

    __table_args__ = (
        UniqueConstraint("consultation_id"),
    )

