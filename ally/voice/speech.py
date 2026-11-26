"""Text-to-speech with Microsoft Edge neural voices (edge-tts): a Hindi and an Indian-English voice."""

from __future__ import annotations

import base64
from typing import Any

import edge_tts

from config import TTS_VOICE_EN, TTS_VOICE_HI


async def synthesize(text: str, language: str) -> dict[str, Any]:
    language = language if language in ("hi-IN", "en-IN") else "en-IN"
    voice = TTS_VOICE_HI if language == "hi-IN" else TTS_VOICE_EN
    audio = bytearray()
    async for chunk in edge_tts.Communicate(text[:1500], voice).stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    if not audio:
        raise RuntimeError("edge-tts returned no audio")
    return {
        "audio_base64": base64.b64encode(bytes(audio)).decode(),
        "mime_type": "audio/mpeg",
        "text": text,
        "language": language,
        "provider": f"edge-tts:{voice}",
    }
