# tests/test_tts.py

from app.main import app
from app.services.tts_service import TTSServiceError


def test_tts_success(client, monkeypatch):

    def fake_synthesize_speech(text, language_code):
        return {
            "audio": "fake-audio",
            "language_code": language_code,
        }

    monkeypatch.setattr(
        "app.routers.tts.synthesize_speech",
        fake_synthesize_speech,
    )

    response = client.post(
        "/tts/tts",
        json={
            "text": "Hello",
            "language_code": "en-US",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["audio"] == "fake-audio"
    assert data["language_code"] == "en-US"


def test_tts_uses_default_language(client, monkeypatch):

    captured = {}

    def fake_synthesize_speech(text, language_code):
        captured["text"] = text
        captured["language_code"] = language_code

        return {"ok": True}

    monkeypatch.setattr(
        "app.routers.tts.synthesize_speech",
        fake_synthesize_speech,
    )

    response = client.post(
        "/tts/tts",
        json={
            "text": "Hello"
        },
    )

    assert response.status_code == 200

    assert captured["text"] == "Hello"
    assert captured["language_code"] == "en-US"


def test_tts_service_error_returns_500(client, monkeypatch):

    def fake_synthesize_speech(text, language_code):
        raise TTSServiceError("TTS failed")

    monkeypatch.setattr(
        "app.routers.tts.synthesize_speech",
        fake_synthesize_speech,
    )

    response = client.post(
        "/tts/tts",
        json={
            "text": "Hello",
            "language_code": "en-US",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "TTS failed"