"""Stay with her (bible v5 L7): status every minute, ETA only from the helper, still-on-floor, overdue."""

from datetime import timedelta

import pytest

from agents import companion, orchestrator
from agents.schemas import CompanionReply
from core import clock
from escalation import service as escalation

P_REF = 920.00


@pytest.fixture
def red(repo, seeded, monkeypatch):
    repo.put_profile("amma", {**seeded, "city": "Bengaluru"})
    for m in repo.list_members("amma"):
        city = {"rahul": "Pune", "priya": "Bengaluru", "sunita": "Bengaluru"}[m["id"]]
        repo.put_member("amma", {**m, "city": city})

    async def fake_respond(parent_id, text, *, investigating, source):
        reply = CompanionReply(say="अच्छा।", language="hi-IN", parent_says_okay=True)
        return reply, companion.RunEffects(), type("G", (), {"denied_tools": []})()

    monkeypatch.setattr(companion, "respond", fake_respond)

    async def go():
        await orchestrator.on_watch("amma", "fall")
        await orchestrator.on_parent_turn("amma", "theek hoon bas thoda dard hai", source="voice", duration_sec=2.5)
        return repo.list_escalations("amma")[0]["id"]

    return go


def stays(pushes):
    return [p["body"] for p in pushes if p["audience"] == "parent" and p["type"] == "stay"]


async def tick(minutes=1):
    clock.set_now(clock.now() + timedelta(minutes=minutes))
    return await orchestrator.stay_ticks(clock.now())


async def test_before_anyone_accepts_it_never_says_someone_is_coming(red, repo, pushes):
    await red()
    assert await tick() == 1
    assert stays(pushes)[-1] == "मैं यहीं हूँ, मदद बुला रही हूँ।"


async def test_after_accept_it_relays_who_and_their_own_eta(red, repo, pushes):
    esc_id = await red()
    await escalation.reply("amma", esc_id, responder="priya", decision="accept", eta_min=20)
    await tick()
    last = stays(pushes)[-1]
    assert "Priya" in last and "19 मिनट" in last and "मैं यहीं हूँ" in last


async def test_accept_without_minutes_gives_no_made_up_eta(red, repo, pushes):
    esc_id = await red()
    await escalation.reply("amma", esc_id, responder="priya", decision="accept")
    await tick()
    assert "मिनट" not in stays(pushes)[-1]


async def test_one_status_per_minute(red, repo, pushes):
    await red()
    await tick()
    await orchestrator.stay_ticks(clock.now())  # same minute again
    assert len(stays(pushes)) == 1


async def test_still_on_floor_flag_from_the_watch(red, repo, pushes):
    esc_id = await red()
    repo.add_signal("amma", "getup_ref", p_ref_hpa=P_REF)
    clock.set_now(clock.now() + timedelta(seconds=30))
    repo.add_signal("amma", "getup_sample", p_hpa=P_REF + 0.09)
    await orchestrator.stay_ticks(clock.now())
    assert repo.get_escalation("amma", esc_id)["still_on_floor"] is True
    clock.set_now(clock.now() + timedelta(seconds=30))
    repo.add_signal("amma", "getup_sample", p_hpa=P_REF + 0.01)
    await orchestrator.stay_ticks(clock.now())
    assert repo.get_escalation("amma", esc_id)["still_on_floor"] is False


async def test_overdue_helper_is_asked_once_if_they_are_still_coming(red, repo, pushes):
    esc_id = await red()
    await escalation.reply("amma", esc_id, responder="priya", decision="accept", eta_min=10)
    await tick(26)
    await tick(1)
    asked = [p for p in pushes if p["audience"] == "priya" and "still on your way" in p["body"]]
    assert len(asked) == 1


async def test_stops_after_arrival(red, repo, pushes):
    esc_id = await red()
    await escalation.reply("amma", esc_id, responder="priya", decision="accept", eta_min=5)
    await escalation.reply("amma", esc_id, responder="priya", decision="arrived")
    assert await tick() == 0
