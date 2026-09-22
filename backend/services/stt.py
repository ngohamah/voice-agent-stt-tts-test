"""Speech-to-text via Mistral's Voxtral transcription endpoint.

Uses the raw REST API (mirrors OpenAI's /audio/transcriptions shape) rather
than the mistralai SDK, so it doesn't depend on that package's audio-API
version. Double check the endpoint/model name against Mistral's current docs
before relying on this in production.
"""

import logging
import os

import httpx

MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]
TRANSCRIPTION_URL = "https://api.mistral.ai/v1/audio/transcriptions"
MODEL = "voxtral-mini-latest"

logger = logging.getLogger(__name__)


async def transcribe(audio_bytes: bytes, filename: str, content_type: str) -> str:
    logger.info(
        "STT request: filename=%s content_type=%s bytes=%d",
        filename, content_type, len(audio_bytes),
    )

    files = {"file": (filename, audio_bytes, content_type)}
    data = {"model": MODEL}
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            TRANSCRIPTION_URL, headers=headers, data=data, files=files
        )
    if response.status_code >= 400:
        logger.error("STT error %d: %s", response.status_code, response.text)
        raise RuntimeError(f"Mistral STT error {response.status_code}: {response.text}")

    transcript = response.json()["text"]
    logger.info("STT response: transcript=%r", transcript)
    return transcript
