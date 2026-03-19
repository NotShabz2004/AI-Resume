# RunReady Motivation (Full-Stack)

A full app for runners and marathoners that:
- asks 3 personal questions,
- generates personalized motivational quotes on the spot using **Gemini API**,
- and supports **Text-to-Speech (TTS)** with either browser voice (free) or ElevenLabs.

## Stack

- **Backend:** FastAPI (`backend/app/main.py`)
- **Frontend:** Vanilla HTML/CSS/JS (`frontend/`)
- **AI Quote Generation:** Gemini API (with local fallback templates if unavailable)
- **TTS:** Browser Speech Synthesis or ElevenLabs API

## Features

1. Personalized context collection:
   - Name
   - Who/what the runner is running for
   - Biggest challenge
2. On-demand AI motivational quote generation
3. Race type and tone controls
4. Quote playback with TTS
5. Fallback mode when AI provider is unavailable

## Project structure

```text
backend/
  app/
    main.py
frontend/
  index.html
  styles.css
  app.js
```

## Setup

### 1) Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2) Configure environment variables

Create a `.env` file (or export variables in shell):

```bash
export GEMINI_API_KEY="your_gemini_api_key"
# optional
export GEMINI_MODEL="gemini-2.0-flash"

# optional for premium TTS
export ELEVENLABS_API_KEY="your_elevenlabs_key"
export ELEVENLABS_VOICE_ID="EXAVITQu4vr4xnSDxMaL"
```

### 3) Run the app

```bash
uvicorn backend.app.main:app --reload
```

Open: http://127.0.0.1:8000

## API endpoints

- `POST /api/quotes`
  - Generates personalized motivational quotes via Gemini (or fallback templates).
- `POST /api/tts`
  - `provider: "browser"` returns browser-mode response.
  - `provider: "elevenlabs"` returns base64 MP3 audio.
- `GET /health`
  - Health check.

## Notes

- If `GEMINI_API_KEY` is not configured or API call fails, the app uses a local quote engine fallback.
- Browser TTS requires no API key and is ideal for local demos.
- ElevenLabs requires backend API key configuration.

## Can this be extended further?

Yes — this foundation is meant for iterative changes. We can add:
- user authentication,
- saved training sessions,
- quote history,
- scheduled notifications,
- smartwatch integration,
- voice selection UI,
- production deployment setup.
