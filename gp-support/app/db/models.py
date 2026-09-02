from datetime import datetime, UTC
from enum import Enum

from sqlalchemy import String, ForeignKey, DateTime, Text, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"


class LanguagePreference(str, Enum):
    ENGLISH = "en-US"
    CHINESE = "zh-CN"
    THAI = "th-TH"
    RUSSIAN = "ru-RU"
    SPANISH = "es-US"



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255)
    )

    name: Mapped[str] = mapped_column(String(100))

    nationality: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    preferred_language: Mapped[LanguagePreference] = mapped_column(
        SQLEnum(
            LanguagePreference,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        default=LanguagePreference.ENGLISH,
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        default=UserRole.PATIENT,
        nullable=False
    )

    medical_history: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    allergies: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    medications: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=True
    )

    doctor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    doctor: Mapped["User | None"] = relationship(
        "User",
        remote_side=[id],
        back_populates="patients",
        foreign_keys=[doctor_id]
    )

    patients: Mapped[list["User"]] = relationship(
        "User",
        back_populates="doctor",
        foreign_keys=[doctor_id]
    )

    consultations: Mapped[list["Consultation"]] = relationship(
        back_populates="user"
    )


class ConsultationStatus(str, Enum):
    IN_PROGRESS = "in-progress"
    CLOSED = "closed"


class Consultation(Base):
    __tablename__ = "consultations"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    status: Mapped[ConsultationStatus] = mapped_column(
        SQLEnum(
            ConsultationStatus,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        default=ConsultationStatus.IN_PROGRESS,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    user: Mapped["User"] = relationship(
        back_populates="consultations"
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="consultation",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    summary: Mapped["Summary | None"] = relationship(
        back_populates="consultation",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    consultation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "consultations.id",
            ondelete="CASCADE"
        )
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
        ForeignKey(
            "consultations.id",
            ondelete="CASCADE"
        )
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



