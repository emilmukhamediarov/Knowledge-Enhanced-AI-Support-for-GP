import secrets
from datetime import UTC, datetime, timedelta
from sqlalchemy.orm import Session
from app.config import (
    EMAIL_CODE_MAX_ATTEMPTS,
    EMAIL_CODE_RESEND_SECONDS,
    EMAIL_CODE_TTL_MINUTES,
)
from app.db import models
from app.services.email_service import send_verification_email


class VerificationError(RuntimeError):
    pass

class VerificationTooSoonError(VerificationError):
    pass

class InvalidVerificationCodeError(VerificationError):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()

#generate a random 6-digit code
def _create_code() -> str:
    number = secrets.randbelow(1_000_000)
    return f"{number:06d}"

def issue_verification_code(
    db: Session,
    email: str,
) -> None:
    email = normalize_email(email)
    now = datetime.now(UTC)

    # Check when the last code was sent
    latest = (
        db.query(models.EmailVerificationCode)
        .filter(models.EmailVerificationCode.email == email)
        .order_by(models.EmailVerificationCode.created_at.desc())
        .first()
    )

    # User must wait before requesting another code
    if latest is not None:
        next_allowed_at = latest.created_at + timedelta(
            seconds=EMAIL_CODE_RESEND_SECONDS
        )
        if now < next_allowed_at:
            raise VerificationTooSoonError(
                "Please wait before requesting another code"
            )

    # Generate a new 6-digit code
    code = _create_code()

    # Create a new record in the database
    new_record = models.EmailVerificationCode(
        email=email,
        code=code,
        expires_at=now + timedelta(
            minutes=EMAIL_CODE_TTL_MINUTES
        ),
        attempt_count=0,
    )

    db.add(new_record)

    # Send the email with the verification code
    try:
        send_verification_email(
            recipient_email=email,
            verification_code=code,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise


def verify_email_code(
    db: Session,
    email: str,
    code: str,
) -> models.EmailVerificationCode:
    
    email = normalize_email(email)
    now = datetime.now(UTC)

    # Get the latest code for this email
    record = (
        db.query(models.EmailVerificationCode)
        .filter(
            models.EmailVerificationCode.email == email,
            ~models.EmailVerificationCode.code.like("r:%"),
        )
        .order_by(models.EmailVerificationCode.created_at.desc())
        .with_for_update()
        .first()
    )

    if record is None:
        raise InvalidVerificationCodeError(
            "Invalid verification code"
        )

    # Check whether the code has expired
    if record.expires_at <= now:
        raise InvalidVerificationCodeError(
            "Verification code has expired"
        )

    # Check maximum attempts
    if record.attempt_count >= EMAIL_CODE_MAX_ATTEMPTS:
        raise InvalidVerificationCodeError(
            "Too many verification attempts"
        )

    # Check the code if it matches
    if record.code != code:
        record.attempt_count += 1
        db.commit()
        raise InvalidVerificationCodeError(
            "Invalid verification code"
        )
        
    return record