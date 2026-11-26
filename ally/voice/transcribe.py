"""Speech-to-text for 16 kHz PCM16 WAV clips from the browser recorder.

Wispr Flow is the primary provider; it takes the WAV as-is. Groq Whisper is the second provider,
used when Wispr has no key or fails. Both handle Hindi, Indian English and a mix of the two, and
both are told the parent's language first so she never has to choose one.
"""

from __future__ import annotations

import base64
import io
import wave
from dataclasses import dataclass

import httpx

from config import GROQ_STT_MODEL, WISPR_API_KEY, WISPR_API_URL
from core.errors import AllyError
from core.log import log

MAX_CLIP_SECONDS = 12
LANGUAGE_OPTIONS = ["en-IN", "hi-IN"]


class BadAudio(AllyError):
    status = 400
    code = "bad_audio"


@dataclass
class Transcript:
    text: str
    language: str
    duration_sec: float
    provider: str = ""


def pcm_from_wav(raw: bytes) -> tuple[bytes, int, float]:
    try:
        with wave.open(io.BytesIO(raw), "rb") as wav:
            rate, width, channels = wav.getframerate(), wav.getsampwidth(), wav.getnchannels()
            frames = wav.readframes(wav.getnframes())
    except (wave.Error, EOFError) as exc:
        raise BadAudio("That recording could not be read. Please try again.", detail=repr(exc)) from exc
    if width != 2 or channels != 1:
        raise BadAudio("Unsupported recording format.", detail=f"width={width} channels={channels}")
    duration = len(frames) / 2 / rate
    if duration > MAX_CLIP_SECONDS + 0.5:
        raise BadAudio("That recording was too long. Please keep it short.", detail=f"{duration:.1f}s")
    return frames, rate, duration


def _bcp47(code: str | None, preferred: str) -> str:
    """Providers answer with "hi"/"en" (or "hindi"); the rest of Ally speaks hi-IN / en-IN."""
    code = (code or "").lower()
    if code.startswith("hi"):
        return "hi-IN"
    if code.startswith("en"):
        return "en-IN"
    return preferred if preferred in LANGUAGE_OPTIONS else "hi-IN"


async def _wispr(raw: bytes, preferred: str) -> tuple[str, str]:
    first = "hi" if preferred == "hi-IN" else "en"
    body = {
        "audio": base64.b64encode(raw).decode(),
        "language": [first, "en" if first == "hi" else "hi"],
        "context": {"app": {"type": "other"}},
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(WISPR_API_URL, json=body, headers={"Authorization": f"Bearer {WISPR_API_KEY}"})
    resp.raise_for_status()
    data = resp.json()
    return str(data.get("text") or ""), _bcp47(data.get("detected_language"), preferred)


async def _groq_whisper(raw: bytes, preferred: str) -> tuple[str, str]:
    import litellm

    clip = io.BytesIO(raw)
    clip.name = "clip.wav"
    resp = await litellm.atranscription(
        model=f"groq/{GROQ_STT_MODEL}",
        file=clip,
        response_format="verbose_json",
        prompt="Hindi, Hinglish or Indian English.",
    )
    language = getattr(resp, "language", None) or (resp.get("language") if hasattr(resp, "get") else None)
    return str(resp.text or ""), _bcp47(language, preferred)


async def transcribe_wav(raw: bytes, preferred_language: str) -> Transcript:
    _, _, duration = pcm_from_wav(raw)
    if WISPR_API_KEY:
        try:
            text, language = await _wispr(raw, preferred_language)
            return Transcript(text.strip(), language, duration, "wispr")
        except Exception as exc:  # fall through to the second provider; logged, not hidden
            log("stt_failover", frm="wispr", to="groq_whisper", error=repr(exc))
    text, language = await _groq_whisper(raw, preferred_language)
    return Transcript(text.strip(), language, duration, "groq_whisper")
