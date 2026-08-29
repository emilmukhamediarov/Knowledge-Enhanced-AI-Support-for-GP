import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BUILD_RAG_INDEX = True if os.getenv("BUILD_RAG_INDEX", "false").lower() == "true" else False


class Settings:
    aws_region = os.getenv("AWS_REGION", "ap-southeast-2")
    bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
    transcribe_s3_bucket = os.getenv("TRANSCRIBE_S3_BUCKET", "")
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    transcribe_language_options = [
        code.strip()
        for code in os.getenv("TRANSCRIBE_LANGUAGE_OPTIONS", "").split(",")
        if code.strip()
    ]

    transcribe_timeout_seconds = int(os.getenv("TRANSCRIBE_TIMEOUT_SECONDS", "180"))

settings = Settings()

AWS_REGION = settings.aws_region
BEDROCK_MODEL_ID = settings.bedrock_model_id