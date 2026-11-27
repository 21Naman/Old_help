"""Ally runtime config. Every value is an env var so local, Render and tests share one code path."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ALLY_ROOT = Path(__file__).resolve().parent
load_dotenv(ALLY_ROOT / ".env")
load_dotenv(ALLY_ROOT.parent / ".env")


def _s(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()


def _i(key: str, default: int) -> int:
    raw = _s(key)
    return int(raw) if raw else default


def _b(key: str) -> bool:
    return _s(key).lower() in ("1", "true", "yes", "on")


PARENT_ID = _s("ALLY_PARENT_ID", "amma")
# Demo switch: the old "she said she's okay, so close it" behaviour (bible v5 Naive mode).
NAIVE_MODE = _b("SURAKSHA_NAIVE_MODE")
HOST = _s("ALLY_HOST", "0.0.0.0")
PORT = _i("PORT", _i("ALLY_PORT", 8002))  # Render sets PORT
TZ = _s("ALLY_TZ", "Asia/Kolkata")

# SQLAlchemy URL. Neon/Render give `postgresql://…`; locally and in tests SQLite is enough.
DATABASE_URL = _s("DATABASE_URL", f"sqlite:///{ALLY_ROOT / 'ally.db'}")

# Any LiteLLM model id. Keys come from the provider's own env var (GROQ_API_KEY, GEMINI_API_KEY).
LLM_MODEL = _s("LLM_MODEL", "groq/llama-3.3-70b-versatile")
# A second provider. A turn that fails on the primary is re-run here before Ally reports llm_unavailable.
LLM_FALLBACK_MODEL = _s("LLM_FALLBACK_MODEL", "gemini/gemini-2.5-flash")
LLM_MAX_TOKENS = _i("LLM_MAX_TOKENS", 800)
LLM_TIMEOUT_S = _i("LLM_TIMEOUT_S", 25)


def llm_model_for(task: str) -> str:
    """Per-task override, e.g. LLM_MODEL_MORNING_CHECKIN=groq/llama-3.1-8b-instant to save quota."""
    return _s(f"LLM_MODEL_{task.upper()}", LLM_MODEL)


# Speech-to-text: Wispr Flow first, Groq Whisper when Wispr has no key or fails.
WISPR_API_KEY = _s("WISPR_API_KEY")
WISPR_API_URL = _s("WISPR_API_URL", "https://platform-api.wisprflow.ai/api/v1/dash/api")
GROQ_STT_MODEL = _s("GROQ_STT_MODEL", "whisper-large-v3")

# Text-to-speech (Microsoft Edge neural voices via edge-tts), one voice per language.
TTS_VOICE_HI = _s("ALLY_TTS_VOICE_HI", "hi-IN-SwaraNeural")
TTS_VOICE_EN = _s("ALLY_TTS_VOICE_EN", "en-IN-NeerjaNeural")


# Login tokens are HS256 JWTs signed with this secret. Required when deployed.
JWT_SECRET = _s("ALLY_JWT_SECRET")
JWT_TTL_H = _i("ALLY_JWT_TTL_H", 24 * 30)

# The per-minute sweep: an external cron calls POST /ally/cron/sweep with this header value.
CRON_SECRET = _s("ALLY_CRON_SECRET")
# Local runs (and a single always-on instance) can run the sweep in-process instead.
INPROC_SCHEDULER = _b("ALLY_INPROC_SCHEDULER")

VAPID_SUBJECT = _s("ALLY_VAPID_SUBJECT", "mailto:team@ally.care")
PUBLIC_WEB_URL = _s("PUBLIC_WEB_URL", "http://localhost:3000")
CORS_ORIGINS = [
    o.strip()
    for o in _s("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if o.strip()
]

# Dev-only conveniences (reset endpoint, header-based identity). Never set on the deployed stack.
DEV_TOOLS = _b("ALLY_DEV_TOOLS")

ESCALATION_CONTACT_TIMEOUT = _i("ESCALATION_CONTACT_TIMEOUT", 180)
INVESTIGATION_WINDOW_MIN = _i("INVESTIGATION_WINDOW_MIN", 15)
# A possible fall is asked about first, but waits far less before involving family.
FALL_WINDOW_MIN = _i("FALL_WINDOW_MIN", 2)
WAKE_GRACE_MIN = _i("WAKE_GRACE_MIN", 15)
FAMILY_ASK_DAILY_LIMIT = _i("FAMILY_ASK_DAILY_LIMIT", 20)
MESSAGE_EXPIRY_MIN = _i("MESSAGE_EXPIRY_MIN", 120)

