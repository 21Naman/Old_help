"""Speech-to-text entry point: Wispr Flow, then Groq Whisper (see voice.transcribe).

Amma speaks Hindi, Indian English, or a mix of the two in one sentence; the provider detects
which, with her profile language as the tiebreaker, so she never has to choose a language first.

There is no silent fallback to made-up text: if both providers fail the API returns
`stt_unavailable` and the tablet says so.
"""

from __future__ import annotations

from core.errors import AllyError
from core.log import log
from voice.transcribe import BadAudio, Transcript, transcribe_wav


class SttError(AllyError):
    status = 502
    code = "stt_unavailable"


async def transcribe(wav: bytes, preferred_language: str) -> Transcript:
    try:
        return await transcribe_wav(wav, preferred_language)
    except BadAudio:
        raise
    except Exception as exc:
        log("stt_error", error=repr(exc))
        raise SttError("I couldn't hear that clearly. Please try again.", detail=repr(exc)) from exc
