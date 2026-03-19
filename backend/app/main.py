from __future__ import annotations

import base64
import json
import os
import random
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

app = FastAPI(title="RunReady Motivation App", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuoteRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    running_for: str = Field(min_length=1, max_length=200)
    main_challenge: str = Field(min_length=1, max_length=200)
    race_type: str = Field(default="Marathon", max_length=100)
    quote_count: int = Field(default=5, ge=1, le=8)
    tone: Literal["intense", "supportive", "balanced"] = "balanced"


class QuoteResponse(BaseModel):
    quotes: list[str]
    source: Literal["gemini", "fallback"]


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=700)
    provider: Literal["browser", "elevenlabs"] = "browser"
    voice_id: str | None = None


class TTSResponse(BaseModel):
    provider: Literal["browser", "elevenlabs"]
    audio_base64: str | None = None
    mime_type: str | None = None


async def generate_quotes_with_gemini(payload: QuoteRequest) -> list[str]:
    prompt = f"""
You are an elite running coach and motivational speaker.
Create exactly {payload.quote_count} short, emotionally powerful motivational quotes for a {payload.race_type} runner.
Runner context:
- Name: {payload.name}
- Running for: {payload.running_for}
- Biggest challenge: {payload.main_challenge}
- Tone: {payload.tone}

Requirements:
- Return JSON only in this exact format: {{"quotes": ["quote1", "quote2"]}}
- Each quote must be 1-2 sentences max.
- Mention the runner's personal motivation naturally.
- Keep language family-friendly.
""".strip()

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "responseMimeType": "application/json"},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=body)

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Gemini error: {response.text}")

    data = response.json()
    candidate_text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
        .strip()
    )
    if not candidate_text:
        raise HTTPException(status_code=502, detail="Gemini returned an empty response")

    parsed = json.loads(candidate_text)
    quotes = parsed.get("quotes", [])
    clean_quotes = [str(q).strip() for q in quotes if str(q).strip()]
    if not clean_quotes:
        raise HTTPException(status_code=502, detail="Gemini returned no usable quotes")
    return clean_quotes[: payload.quote_count]


def fallback_quotes(payload: QuoteRequest) -> list[str]:
    templates = [
        "{name}, when {main_challenge} hits, remember who you're doing this for: {running_for}. One more step.",
        "Run this {race_type} with heart. Every mile honors {running_for}.",
        "You don't need perfect conditions—just purpose. Your purpose is {running_for}.",
        "{name}, discomfort is temporary. Pride lasts far beyond this {race_type}.",
        "When your mind says slow down, answer with intention: {running_for} is worth this effort.",
        "Strong legs, calm breath, focused mind—this is how you beat {main_challenge}.",
        "Every stride rewrites your story, {name}. Finish this for {running_for}.",
        "You're not chasing a medal only—you're proving you can overcome {main_challenge}.",
    ]

    if payload.tone == "intense":
        templates.append(
            "No excuses today, {name}. Attack each kilometer and make {running_for} proud."
        )
    elif payload.tone == "supportive":
        templates.append(
            "Be kind to yourself, {name}. Progress over perfection—keep moving for {running_for}."
        )

    selected = random.sample(templates, k=min(payload.quote_count, len(templates)))
    return [q.format(**payload.model_dump()) for q in selected]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/quotes", response_model=QuoteResponse)
async def create_quotes(payload: QuoteRequest) -> QuoteResponse:
    if GEMINI_API_KEY:
        try:
            quotes = await generate_quotes_with_gemini(payload)
            return QuoteResponse(quotes=quotes, source="gemini")
        except Exception:
            # fall back to deterministic local quotes when AI call fails
            pass

    return QuoteResponse(quotes=fallback_quotes(payload), source="fallback")


@app.post("/api/tts", response_model=TTSResponse)
async def tts(payload: TTSRequest) -> TTSResponse:
    if payload.provider == "browser":
        return TTSResponse(provider="browser")

    if not ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="ELEVENLABS_API_KEY is not configured. Switch to browser TTS or set the key.",
        )

    voice_id = payload.voice_id or ELEVENLABS_VOICE_ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    body = {
        "text": payload.text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.75},
    }

    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(url, headers=headers, json=body)

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"ElevenLabs error: {response.text}")

    return TTSResponse(
        provider="elevenlabs",
        audio_base64=base64.b64encode(response.content).decode("utf-8"),
        mime_type="audio/mpeg",
    )


app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
