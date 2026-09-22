# Voice Agent Scaffold

Basic record-and-send voice agent: browser records a clip, backend runs
STT → LLM → TTS, and returns the transcript, reply text, and spoken reply.

- **STT**: Voxtral (`voxtral-mini-latest`) via Mistral's REST API
- **LLM**: Llama 3.3 70B via Groq's API (`groq` SDK, free tier)
- **TTS**: Cartesia (`sonic-2`) via the `cartesia` SDK

##
[Architecture]()
## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:

```
MISTRAL_API_KEY=...
GROQ_API_KEY=...        # free key from https://console.groq.com/keys
CARTESIA_API_KEY=...
CARTESIA_VOICE_ID=...   # pick one from https://play.cartesia.ai/voices
```

## Run

```bash
cd backend
uvicorn main:app --reload
```

Open http://localhost:8000 — click "Start Recording", speak, click "Stop
Recording", and wait for the reply to play back.

## Notes / known limitations

- This is a minimal scaffold, not production-ready: conversation history is
  a single in-memory list shared by all requests (fine for one local user,
  wrong for multiple concurrent users — move it to a per-session store to
  fix that).
- No streaming: each turn is record → full round trip → playback. Latency
  will be a few seconds per turn.
- Verify the exact Voxtral endpoint/model name and Cartesia model/voice
  parameters against current docs — these APIs move fast and the code here
  reflects patterns as of this scaffold's creation, not necessarily the
  latest version.
- Browser mic access requires HTTPS or `localhost` — the dev setup above
  works locally as-is, but you'll need TLS to deploy this anywhere else.
