import json
import time
import urllib.request
import uuid
from pathlib import Path

import boto3
from fastapi import UploadFile

from .config import settings


class TranscriptionError(RuntimeError):
    pass


class TranscribeService:
    def __init__(self):
        self.s3 = boto3.client("s3", region_name=settings.aws_region)
        self.transcribe = boto3.client("transcribe", region_name=settings.aws_region)

    def transcribe_upload(self, audio: UploadFile, content: bytes) -> str:
        if not settings.transcribe_s3_bucket:
            raise TranscriptionError("TRANSCRIBE_S3_BUCKET is not configured")

        # Determine file suffix and generate unique S3 key and job name
        suffix = Path(audio.filename or "recording.webm").suffix or ".webm"
        token = uuid.uuid4().hex
        key = f"gp-chatbot-uploads/{token}{suffix}"
        job_name = f"gp-chatbot-{token}"

        media_format = suffix.lstrip(".").lower()
        if media_format == "m4a":
            media_format = "mp4"

        # Upload the audio file to S3
        self.s3.put_object(
            Bucket=settings.transcribe_s3_bucket,
            Key=key,
            Body=content,
            ContentType=audio.content_type or "application/octet-stream",
        )

        #AWS Transcribe job
        try:



            job_options = {
                "TranscriptionJobName": job_name,
                "Media": {
                     "MediaFileUri": f"s3://{settings.transcribe_s3_bucket}/{key}"
                },
                "MediaFormat": media_format,
                "IdentifyLanguage": True,
            }
            if settings.transcribe_language_options:
                if len(settings.transcribe_language_options) < 2:
                    raise TranscriptionError(
                          "TRANSCRIBE_LANGUAGE_OPTIONS must contain at least two languages"
                    )
                job_options["LanguageOptions"] = (
                    settings.transcribe_language_options
                )
            self.transcribe.start_transcription_job(**job_options)



            deadline = time.monotonic() + settings.transcribe_timeout_seconds

            while time.monotonic() < deadline:
                job = self.transcribe.get_transcription_job(
                    TranscriptionJobName=job_name
                )["TranscriptionJob"]
                status = job["TranscriptionJobStatus"]

                if status == "COMPLETED":
                    uri = job["Transcript"]["TranscriptFileUri"]
                    with urllib.request.urlopen(uri, timeout=30) as response:
                        payload = json.load(response)
                    return payload["results"]["transcripts"][0]["transcript"]

                if status == "FAILED":
                    raise TranscriptionError(job.get("FailureReason", "Transcription failed"))
                time.sleep(1)
            raise TranscriptionError("Transcription timed out")

        finally:
            self.s3.delete_object(Bucket=settings.transcribe_s3_bucket, Key=key)
            try:
                self.transcribe.delete_transcription_job(TranscriptionJobName=job_name)
            except self.transcribe.exceptions.BadRequestException:
                pass


transcribe_service = TranscribeService()