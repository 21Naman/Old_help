"""Secrets come from environment variables (Render env groups in production, `.env` locally).

    ALLY_VAPID_PUBLIC_KEY, ALLY_VAPID_PRIVATE_KEY, ALLY_DEVICE_KEY, ALLY_HMAC_SECRET, …
"""

from __future__ import annotations

import os


def secret(name: str) -> str:
    """`name` like VAPID_PRIVATE_KEY → env ALLY_VAPID_PRIVATE_KEY, else VAPID_PRIVATE_KEY."""
    return (os.getenv(f"ALLY_{name}") or os.getenv(name) or "").strip()

