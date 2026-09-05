import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BUILD_RAG_INDEX = False
AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-southeast-2",
)

AWS_PROFILE = os.getenv("AWS_PROFILE")
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "amazon.nova-lite-v1:0",
)

AUTH_SECRET_KEY = os.getenv(
    "AUTH_SECRET_KEY",
    "my_super_secret_key_for_gp_support"
)

AUTH_ALGORITHM = os.getenv(
    "AUTH_ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30"
    )
)

class Settings:
    aws_region = AWS_REGION
    aws_profile = AWS_PROFILE
    bedrock_model_id = BEDROCK_MODEL_ID

    transcribe_language_options = [
        code.strip()
        for code in os.getenv(
            "TRANSCRIBE_LANGUAGE_OPTIONS",
            "en-US,zh-CN,th-TH,ru-RU,es-US",
        ).split(",")
        if code.strip()
    ]

    frontend_origin = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    )

settings = Settings()