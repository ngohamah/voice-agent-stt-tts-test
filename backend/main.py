import base64
import logging

from dotenv import load_dotenv

load_dotenv()  # must run before the service modules read os.environ at import time

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from services import llm, stt, tts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single global conversation history — fine for a one-user local demo,
# not safe for multiple concurrent users.
history: list[dict] = []


@app.post("/api/converse")
async def converse(audio: UploadFile = File(...)):
    logger.info("=== /api/converse: new turn (history has %d turns) ===", len(history))
    audio_bytes = await audio.read()

    transcript = await stt.transcribe(
        audio_bytes, audio.filename or "audio.webm", audio.content_type or "audio/webm"
    )

    reply_text = llm.reply(history, transcript)
    history.append({"role": "user", "text": transcript})
    history.append({"role": "model", "text": reply_text})

    reply_audio = tts.synthesize(reply_text)

    logger.info("=== /api/converse: turn complete ===")
    return {
        "transcript": transcript,
        "reply": reply_text,
        "audio_base64": base64.b64encode(reply_audio).decode("ascii"),
    }


@app.post("/api/reset")
def reset():
    logger.info("Conversation history reset (%d turns cleared)", len(history))
    history.clear()
    return {"ok": True}


app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
