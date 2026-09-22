"""Text-to-speech via Cartesia."""

import logging
import os

from cartesia import Cartesia

CARTESIA_API_KEY = os.environ["CARTESIA_API_KEY"]
# Pick a voice ID from https://play.cartesia.ai/voices (or your own cloned voice)
# and put it in .env as CARTESIA_VOICE_ID.
VOICE_ID = os.environ["CARTESIA_VOICE_ID"]
MODEL_ID = "sonic-2"

logger = logging.getLogger(__name__)

_client = Cartesia(api_key=CARTESIA_API_KEY)


def synthesize(text: str) -> bytes:
    logger.info("TTS request: text=%r", text)

    try:
        chunks = _client.tts.bytes(
            model_id=MODEL_ID,
            transcript=text,
            voice={"mode": "id", "id": VOICE_ID},
            output_format={
                "container": "wav",
                "encoding": "pcm_f32le",
                "sample_rate": 44100,
            },
        )
        audio_bytes = b"".join(chunks)
    except Exception:
        logger.exception("TTS request failed")
        raise

    logger.info("TTS response: bytes=%d", len(audio_bytes))
    return audio_bytes
