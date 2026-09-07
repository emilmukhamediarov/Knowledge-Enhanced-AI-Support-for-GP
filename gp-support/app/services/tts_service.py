import base64
import json
import boto3
from app.config import AWS_REGION, AWS_PROFILE

class TTSServiceError(Exception):
    pass

#connect to AWS Polly and return the client
def _get_polly_client():
    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION,
    )
    return session.client("polly")


def synthesize_speech(text: str):
    if not text or not text.strip():
        raise TTSServiceError("Text cannot be empty.")

    polly = _get_polly_client()

    # Set the voice, language, and engine for speech synthesis
    # You can change these parameters to use different voices, languages, or engines.
    voice_id = "Aria"
    language_code = "en-NZ"
    engine = "neural"


    try:
        # Generate audio
        audio_response = polly.synthesize_speech(
            Text=text,
            VoiceId=voice_id,
            LanguageCode=language_code,
            OutputFormat="mp3",
            Engine=engine,
        )

        audio_bytes = audio_response["AudioStream"].read()

        # Generate word-level speech marks for lip sync
        marks_response = polly.synthesize_speech(
            Text=text,
            VoiceId=voice_id,
            LanguageCode=language_code,
            OutputFormat="json",
            SpeechMarkTypes=["word"],
            Engine=engine,
        )

        marks_text = marks_response["AudioStream"].read().decode("utf-8")

        words = [
            json.loads(line)
            for line in marks_text.splitlines()
            if line.strip()
        ]

        return {
            "audio": base64.b64encode(audio_bytes).decode("utf-8"),
            "words": words,
        }

    except Exception as exc:
        raise TTSServiceError(
            f"Failed to synthesize speech: {exc}"
        ) from exc
