"""Offline fixtures: in-memory SQLite, a frozen IST clock, no network (push/workflow/LLM are faked per test)."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

os.environ.update(
    {
        "DATABASE_URL": "sqlite://",
        "ALLY_HMAC_SECRET": "test-secret",
        "ALLY_DEVICE_KEY": "device-key",
        "ALLY_JWT_SECRET": "test-jwt-secret-at-least-32-bytes-long",
        "ALLY_CRON_SECRET": "cron-secret",
        "ALLY_VAPID_PRIVATE_KEY": "",
        "ALLY_INPROC_SCHEDULER": "",
        "WISPR_API_KEY": "",
    }
)

import pytest  # noqa: E402

from core import clock  # noqa: E402
from policy import consent  # noqa: E402
from store import repo as repo_mod  # noqa: E402


@pytest.fixture(autouse=True)
def db():
    repo_mod.set_repo(repo_mod.Repo("sqlite://"))
    consent._cache.clear()
    yield
    repo_mod.set_repo(None)


@pytest.fixture(autouse=True)
def frozen_clock():
    clock.set_now(datetime.fromisoformat("2026-09-18T09:00:00+05:30"))
    yield
    clock.set_now(None)


@pytest.fixture
def repo() -> repo_mod.Repo:
    return repo_mod.get_repo()


@pytest.fixture
def seeded(repo) -> dict[str, Any]:
    profile = {
        "name": "Amma",
        "language": "hi-IN",
        "baseline": {"wake_window": ["06:30", "07:45"], "vocal_baseline": {"avg_words_per_min": 105}},
    }
    repo.put_profile("amma", profile)
    for m in [
        {"id": "rahul", "name": "Rahul", "relation": "son", "role": "child", "order": 1},
        {"id": "priya", "name": "Priya", "relation": "daughter", "role": "child", "order": 2},
        {"id": "sunita", "name": "Sunita aunty", "relation": "neighbour", "role": "neighbour", "order": 3},
    ]:
        repo.put_member("amma", m)
    return profile


@pytest.fixture
def pushes(monkeypatch) -> list[dict[str, Any]]:
    sent: list[dict[str, Any]] = []

    async def fake_send(parent_id: str, audience: str, payload: dict[str, Any]) -> dict[str, Any]:
        sent.append({"audience": audience, **payload})
        return {"sent": 1, "failed": 0}

    from notify import push

    monkeypatch.setattr(push, "send", fake_send)
    return sent


class FakeMachine:
    """Records workflow starts and resumes so step tests can drive each step themselves."""

    def __init__(self) -> None:
        self.started: list[str] = []
        self.resumed: list[tuple[str, str]] = []

    async def start(self, parent_id: str, esc_id: str) -> None:
        self.started.append(esc_id)

    async def resume(self, parent_id: str, esc_id: str, decision: str) -> None:
        self.resumed.append((esc_id, decision))


@pytest.fixture
def sfn(monkeypatch) -> FakeMachine:
    fake = FakeMachine()
    from escalation import machine

    monkeypatch.setattr(machine, "start", fake.start)
    monkeypatch.setattr(machine, "resume", fake.resume)
    return fake
