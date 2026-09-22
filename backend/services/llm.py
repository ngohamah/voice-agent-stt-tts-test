"""Conversation logic via Groq (Llama 3.3 70B)."""

import logging
import os

from groq import Groq

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
MODEL = "openai/gpt-oss-120b"

SYSTEM_INSTRUCTION = (
    "You are a helpful voice assistant. Keep replies short and conversational "
    "since they will be spoken aloud."
)

logger = logging.getLogger(__name__)

_client = Groq(api_key=GROQ_API_KEY)

_ROLE_MAP = {"user": "user", "model": "assistant"}


def reply(history: list[dict], user_text: str) -> str:
    """history is a list of {"role": "user"|"model", "text": str}, oldest first."""
    logger.info("LLM request: history_turns=%d user_text=%r", len(history), user_text)

    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    messages += [
        {"role": _ROLE_MAP[turn["role"]], "content": turn["text"]} for turn in history
    ]
    messages.append({"role": "user", "content": user_text})

    try:
        response = _client.chat.completions.create(model=MODEL, messages=messages)
    except Exception:
        logger.exception("LLM request failed")
        raise

    reply_text = response.choices[0].message.content
    logger.info("LLM response: reply=%r", reply_text)
    return reply_text
