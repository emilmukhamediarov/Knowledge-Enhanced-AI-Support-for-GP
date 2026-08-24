from groq import Groq
from app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def chat(messages):
    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=messages,
        reasoning_format="hidden",
    )

    return response.choices[0].message.content