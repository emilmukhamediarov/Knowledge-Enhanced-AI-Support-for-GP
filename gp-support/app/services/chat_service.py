from groq import Groq
from app.config import AWS_REGION, BEDROCK_MODEL_ID, GROQ_API_KEY
import boto3
import json
from pydantic import ValidationError
from app.schemas.summaries import ConsultationSummary
from app.services.prompts import SUMMARY_PROMPT

MAX_HISTORY_MESSAGES = 15 #modify later
CHAT_MAX_TOKENS = 150 #modify later
SUMMARY_MAX_TOKENS = 500 #modify later
TEMPERATURE = 0.1

groq_client = Groq(api_key=GROQ_API_KEY)

aws_client = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION
)


def chat_groq(messages):
    response = groq_client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=messages,
        reasoning_format="hidden",
    )

    return response.choices[0].message.content


def chat_aws(messages):
    system_prompt = None
    bedrock_messages = []

    for message in messages:
        if message["role"] == "system":
            system_prompt = message["content"]
        else:
            bedrock_messages.append(
                {
                    "role": message["role"],
                    "content": [
                        {
                            "text": message["content"]
                        }
                    ]
                }
            )

    bedrock_messages = bedrock_messages[-MAX_HISTORY_MESSAGES:]

    response = aws_client.converse(
        modelId=BEDROCK_MODEL_ID,
        system=[
            {
                "text": system_prompt
            }
        ] if system_prompt else [],
        messages=bedrock_messages,
        inferenceConfig={
            "maxTokens": CHAT_MAX_TOKENS,
            "temperature": TEMPERATURE
        }
    )

    return response["output"]["message"]["content"][0]["text"]


def summary_aws(messages, consultation_id):
    bedrock_messages = []

    for message in messages:
        bedrock_messages.append(
            {
                "role": message["role"],
                "content": [
                    {
                        "text": message["content"]
                    }
                ]
            }
        )

    bedrock_messages.append(
        {
            "role": "user",
            "content": [
                {
                    "text": SUMMARY_PROMPT
                }
            ]
        }
    )

    response = aws_client.converse(
        modelId=BEDROCK_MODEL_ID,
        messages=bedrock_messages,
        inferenceConfig={
            "maxTokens": SUMMARY_MAX_TOKENS,
            "temperature": 0
        }
    )

    raw = response["output"]["message"]["content"][0]["text"].strip()

    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()

    try:
        payload = json.loads(raw)

        payload["consultation_id"] = consultation_id

        validated = ConsultationSummary.model_validate(payload)

        validated.calculate_completion()

        return validated.model_dump()

    except (json.JSONDecodeError, ValidationError, TypeError) as exc:
        raise RuntimeError(
            "Model did not return a valid consultation summary"
        ) from exc