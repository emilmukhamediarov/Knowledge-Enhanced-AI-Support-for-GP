"""Real-time Amazon Transcribe support without S3 storage."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

import boto3
from amazon_transcribe.auth import StaticCredentialResolver
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler

from app.config import settings


class TranscriptionError(RuntimeError):
    pass


TranscriptCallback = Callable[[str, bool], Awaitable[None]]


class _TranscriptHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream, on_transcript: TranscriptCallback):
        super().__init__(output_stream)
        self.on_transcript = on_transcript
        self.final_parts: list[str] = []

    async def handle_transcript_event(self, transcript_event) -> None:
        for result in transcript_event.transcript.results:
            if not result.alternatives:
                continue

            text = result.alternatives[0].transcript.strip()
            if not text:
                continue

            is_final = not result.is_partial
            if is_final:
                self.final_parts.append(text)
            await self.on_transcript(text, is_final)

    @property
    def transcript(self) -> str:
        return " ".join(self.final_parts).strip()


class TranscribeService:
    def __init__(self):
        session = boto3.Session(
            profile_name=settings.aws_profile,
            region_name=settings.aws_region,
        )
        credentials = session.get_credentials()
        if credentials is None:
            raise TranscriptionError(
                "No AWS credentials were found for the configured AWS profile"
            )

        frozen_credentials = credentials.get_frozen_credentials()
        self.client = TranscribeStreamingClient(
            region=settings.aws_region,
            credential_resolver=StaticCredentialResolver(
                frozen_credentials.access_key,
                frozen_credentials.secret_key,
                frozen_credentials.token,
            ),
        )

    async def start_stream(self, on_transcript: TranscriptCallback):
        options = settings.transcribe_language_options
        if len(options) < 2:
            raise TranscriptionError(
                "TRANSCRIBE_LANGUAGE_OPTIONS must contain at least two languages"
            )

        try:
            stream = await self.client.start_stream_transcription(
                language_code=None,
                identify_language=True,
                language_options=options,
                media_sample_rate_hz=16000,
                media_encoding="pcm",
            )
        except Exception as exc:
            raise TranscriptionError(
                f"Unable to start real-time transcription: {exc}"
            ) from exc

        return stream, _TranscriptHandler(stream.output_stream, on_transcript)


transcribe_service = TranscribeService()
