"""The AWS-free pieces: SQL repo semantics, the DB escalation workflow end to end, local sign-in,
route aliases, watch + phone together, the cron sweep, and LLM provider failover."""

import importlib
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from agents import orchestrator
from agents.schemas import HealthProbe
from config import ESCALATION_CONTACT_TIMEOUT
from core import clock
from core.errors import Conflict, LLMError
from escalation import handoff, service, tokens


def _alert(repo, severity="high"):
    alert = {"id": "al1", "created_at": clock.iso(clock.now()), "kind": "fall", "status": "investigating",
             "source": "phone", "judgment": {"severity": severity, "reasons": ["Possible fall, no answer"]}}
    repo.put_alert("amma", alert)
    return alert


def _later(seconds: int) -> None:
    clock.set_now(clock.now() + timedelta(seconds=seconds))


# ---- repository ------------------------------------------------------------------------------


def test_repo_conditional_writes(repo):
    assert repo.set_day_if_absent("amma", "2026-09-18", "wake_at", "t1") is True
    assert repo.set_day_if_absent("amma", "2026-09-18", "wake_at", "t2") is False
    assert repo.get_day("amma", "2026-09-18")["wake_at"] == "t1"

    assert [repo.increment_day("amma", "2026-09-18", "asks", limit=2) for _ in range(3)] == [1, 2, -1]
    assert repo.claim_dedupe("amma", "k") is True and repo.claim_dedupe("amma", "k") is False

    first, created = repo.create_message("amma", audience="parent", kind="k", title="", body="b", related_id="r1")
    again, created2 = repo.create_message("amma", audience="parent", kind="k", title="", body="b", related_id="r1")
    assert created and not created2 and again["id"] == first["id"]
    assert [m["id"] for m in repo.claim_pending_messages("amma", "parent")] == [first["id"]]
    assert repo.claim_pending_messages("amma", "parent") == []  # claimed once

    assert repo.acquire_escalation_lock("amma", "e1") is True
    assert repo.acquire_escalation_lock("amma", "e2") is False
    repo.release_escalation_lock("amma", "e2")  # wrong id: no-op
    assert repo.active_escalation_id("amma") == "e1"


def test_repo_purges_expired_rows(repo):
    repo.add_turn("amma", "parent", "hello")
    _later(31 * 24 * 3600)
    assert repo.purge_expired() == 1
    assert repo.recent_turns("amma") == []


# ---- escalation workflow, no fakes -------------------------------------------------------------


async def test_workflow_walks_children_then_neighbour_then_everyone(seeded, repo, pushes):
    esc = await service.start("amma", _alert(repo), "high")
    esc_id = esc["id"]
    assert repo.get_escalation("amma", esc_id)["current_contact"] == "rahul"

    _later(ESCALATION_CONTACT_TIMEOUT + 1)
    assert await orchestrator.escalation_machine.sweep_timeouts() == 1
    assert repo.get_escalation("amma", esc_id)["current_contact"] == "priya"

    await service.reply("amma", esc_id, responder="priya", decision="decline")
    assert repo.get_escalation("amma", esc_id)["status"] == "asking_parent"

    # Amma doesn't answer; high severity + timeout means Cedar won't let us call the neighbour.
    _later(ESCALATION_CONTACT_TIMEOUT + 1)
    await orchestrator.escalation_machine.sweep_timeouts()
    final = repo.get_escalation("amma", esc_id)
    assert final["status"] == "closed"
    assert repo.active_escalation_id("amma") is None
    assert {p["audience"] for p in pushes if p.get("title", "").startswith("Please check on")} == {"rahul", "priya"}


async def test_neighbour_answers_from_the_guard_handset(seeded, repo, pushes):
    esc_id = (await service.start("amma", _alert(repo), "high"))["id"]
    await service.reply("amma", esc_id, responder="rahul", decision="decline")
    await service.reply("amma", esc_id, responder="priya", decision="decline")
    assert handoff.guard_call("amma") == {"ringing": False}
    await service.reply("amma", esc_id, responder="parent", decision="confirm")

    call = handoff.guard_call("amma")
    assert call["ringing"] and call["guard_name"] == "Sunita aunty"
    claims = tokens.verify(call["reply_token"])
    await service.reply("amma", esc_id, responder=claims["contact"], decision="accept", token_version=claims["token_version"])
    esc = repo.get_escalation("amma", esc_id)
    assert esc["status"] == "accepted" and esc["responder"] == "sunita"
    assert handoff.guard_call("amma") == {"ringing": False}
    with pytest.raises(Conflict):
        await service.reply("amma", esc_id, responder="sunita", decision="accept", token_version=claims["token_version"])


async def test_reply_racing_a_timeout_loses_cleanly(seeded, repo, pushes):
    esc_id = (await service.start("amma", _alert(repo), "high"))["id"]
    version = repo.get_escalation("amma", esc_id)["token_version"]
    _later(ESCALATION_CONTACT_TIMEOUT + 1)
    await orchestrator.escalation_machine.sweep_timeouts()
    with pytest.raises(Conflict):
        await service.reply("amma", esc_id, responder="rahul", decision="accept", token_version=version)


def test_handoff_note_respects_health_privacy(seeded, repo):
    repo.put_alert("amma", {"id": "a", "created_at": clock.iso(clock.now()), "kind": "fall", "source": "watch",
                            "judgment": {"reasons": ["Said her chest hurt"]}})
    repo.put_escalation("amma", {"id": "e", "alert_id": "a", "created_at": clock.iso(clock.now()), "timeline": []})
    note = handoff.note("amma", "e", "sunita")
    assert "Said her chest hurt" not in note["facts"] and note["withheld"]
    assert note["what_happened"].startswith("Her watch")


# ---- devices ------------------------------------------------------------------------------------


async def test_watch_and_phone_fall_together_open_one_alert(seeded, repo, pushes):
    first = await orchestrator.on_watch("amma", "fall", source="phone")
    second = await orchestrator.on_watch("amma", "fall", source="watch")
    assert first["asked_parent"] and second["skipped"] == "duplicate"
    alerts = repo.list_alerts("amma")
    assert len(alerts) == 1 and alerts[0]["source"] == "phone"


async def test_wake_from_either_device_counts_once(seeded, repo, pushes, monkeypatch):
    from proactive import morning

    async def no_morning(*a, **k):
        return None

    monkeypatch.setattr(morning, "run", no_morning)
    assert (await orchestrator.on_watch("amma", "wake", source="phone"))["first_wake"] is True
    assert (await orchestrator.on_watch("amma", "wake", source="watch"))["first_wake"] is False
    assert repo.get_day("amma", clock.local_date())["wake_source"] == "phone"


# ---- HTTP: sign-in, aliases, device keys, cron ------------------------------------------------


@pytest.fixture
def client(monkeypatch, seeded, pushes):
    monkeypatch.setenv("ALLY_DEV_TOOLS", "")
    monkeypatch.setenv("ALLY_PHONE_DEVICE_KEY", "phone-key")
    import config

    importlib.reload(config)
    import auth

    importlib.reload(auth)
    import app as app_module

    importlib.reload(app_module)
    from scripts.seed import seed_users

    seed_users("pw-123")
    return TestClient(app_module.app)


def test_login_and_both_prefixes(client):
    assert client.post("/ally/auth/login", json={"username": "amma", "password": "nope"}).status_code == 401
    token = client.post("/suraksha/auth/login", json={"username": "Rahul", "password": "pw-123"}).json()["token"]
    headers = {"authorization": f"Bearer {token}"}
    assert client.get("/suraksha/dashboard", headers=headers).status_code == 200
    assert client.get("/ally/dashboard", headers=headers).status_code == 200
    assert client.get("/ally/dashboard", headers={"authorization": "Bearer junk"}).status_code == 401
    assert client.get("/ally/dashboard", headers={"x-dev-member": "rahul"}).status_code == 401  # dev header off


def test_device_keys_per_source(client):
    activity = {"kind": "activity", "steps": 10}
    assert client.post("/ally/watch", json=activity, headers={"x-ally-device-key": "device-key"}).status_code == 200
    phone = {**activity, "source": "phone"}
    assert client.post("/ally/device", json=phone, headers={"x-ally-device-key": "phone-key"}).status_code == 200
    assert client.post("/suraksha/device", json=phone, headers={"x-suraksha-device-key": "device-key"}).status_code == 200
    assert client.post("/ally/watch", json=activity, headers={"x-ally-device-key": "phone-key"}).status_code == 401


def test_cron_sweep_needs_secret(client):
    assert client.post("/ally/cron/sweep").status_code == 403
    assert client.post("/ally/cron/sweep", headers={"x-cron-secret": "wrong"}).status_code == 403
    res = client.post("/ally/cron/sweep", headers={"x-cron-secret": "cron-secret"})
    assert res.status_code == 200 and "escalations" in res.json()


# ---- LLM failover -------------------------------------------------------------------------------


class _FakeAgent:
    calls: list[str] = []
    failing: set[str] = set()

    def __init__(self, *, model, **_):
        self.model = model

    async def invoke_async(self, *_a, **_k):
        _FakeAgent.calls.append(self.model)
        if self.model in _FakeAgent.failing:
            raise RuntimeError(f"{self.model} is down")
        return type("R", (), {"structured_output": HealthProbe(ok=True, word="ready"), "stop_reason": "end", "metrics": None})()


@pytest.fixture
def fake_llm(monkeypatch):
    from llm import client as llm_client

    _FakeAgent.calls, _FakeAgent.failing = [], set()
    monkeypatch.setattr(llm_client, "Agent", _FakeAgent)
    monkeypatch.setattr(llm_client, "_model", lambda model_id, temperature: model_id)
    monkeypatch.setattr(llm_client, "llm_model_for", lambda task: "groq/primary")
    monkeypatch.setattr(llm_client, "LLM_FALLBACK_MODEL", "gemini/backup")
    return llm_client


async def test_llm_fails_over_to_second_provider(fake_llm):
    _FakeAgent.failing = {"groq/primary"}
    out = await fake_llm.structured("t", "sys", "p", HealthProbe)
    assert out.ok and _FakeAgent.calls == ["groq/primary", "gemini/backup"]


async def test_llm_both_down_is_an_explicit_error(fake_llm):
    _FakeAgent.failing = {"groq/primary", "gemini/backup"}
    with pytest.raises(LLMError):
        await fake_llm.structured("t", "sys", "p", HealthProbe)
