import os

from dotenv import load_dotenv


load_dotenv()


def get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"true", "1", "yes", "on"}


def get_int(name: str, default: int) -> int:
    value = os.getenv(name)

    if not value:
        return default

    try:
        return int(value)
    except ValueError as error:
        raise ValueError(
            f"{name} must be an integer, but received: {value}"
        ) from error


# General configuration
DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BUILD_RAG_INDEX = get_bool("BUILD_RAG_INDEX", False)

# AWS configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
AWS_PROFILE = os.getenv("AWS_PROFILE")

# Amazon Bedrock
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "amazon.nova-lite-v1:0",
)


class Settings:
    aws_region = AWS_REGION
    aws_profile = AWS_PROFILE
    bedrock_model_id = BEDROCK_MODEL_ID

    transcribe_s3_bucket = os.getenv(
        "TRANSCRIBE_S3_BUCKET",
        "",
    )

    transcribe_language_options = [
        code.strip()
        for code in os.getenv(
            "TRANSCRIBE_LANGUAGE_OPTIONS",
            "en-US,zh-CN,th-TH,ru-RU,es-US",
        ).split(",")
        if code.strip()
    ]

    transcribe_timeout_seconds = get_int(
        "TRANSCRIBE_TIMEOUT_SECONDS",
        180,
    )

    frontend_origin = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    )


settings = Settings()