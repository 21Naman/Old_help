"""Red fall + Amma's prior consent: neighbour and nearest child are asked together (bible v5 L6)."""

import pytest

from agents import companion, orchestrator
from agents.schemas import CompanionReply
from core.errors import Conflict
from escalation import service as escalation


@pytest.fixture
def family(repo, seeded, monkeypatch):
    repo.put_profile("amma", {**seeded, "city": "Bengaluru", "fall_preconsent_neighbour": "sunita"})
    for m in repo.list_members("amma"):
        city = {"rahul": "Pune", "priya": "Bengaluru", "sunita": "Bengaluru"}[m["id"]]
        repo.put_member("amma", {**m, "city": city})

    async def fake_respond(parent_id, text, *, investigating, source):
        reply = CompanionReply(say="अच्छा।", language="hi-IN", parent_says_okay=True)
        return reply, companion.RunEffects(), type("G", (), {"denied_tools": []})()

    monkeypatch.setattr(companion, "respond", fake_respond)


async def red_fall():
    await orchestrator.on_watch("amma", "fall")
    # "I'm fine, just a little pain" -> pain words -> LAAL -> escalation (real workflow, no fake)
    return await orchestrator.on_parent_turn("amma", "theek hoon bas thoda dard hai", source="voice", duration_sec=2.5)


def asks(pushes):
    return [p["audience"] for p in pushes if p["type"] == "escalation_ask"]


async def test_neighbour_and_same_city_child_are_asked_together(family, repo, pushes):
    out = await red_fall()
    assert out["fall_tier"] == "LAAL" and out["escalated"]
    assert set(asks(pushes)) == {"sunita", "priya"}  # not Rahul in Pune first
    esc = repo.list_escalations("amma")[0]
    assert esc["parallel"] == ["sunita"] and esc["current_contact"] == "priya"
    audit = [r for r in repo.list_audit("amma") if r["action"] == "contact_neighbour"]
    assert audit and audit[0]["decision"] == "allow"
    assert "neighbour-first-for-falls" in str(audit[0])  # allowed by the fall pre-consent rule


async def test_neighbour_accepting_first_stops_the_chain(family, repo, pushes):
    await red_fall()
    esc_id = repo.list_escalations("amma")[0]["id"]
    esc = await escalation.reply("amma", esc_id, responder="sunita", decision="accept")
    assert esc["status"] == "accepted" and esc["responder"] == "sunita"
    covered = [p for p in pushes if p["audience"] == "priya" and p["type"] == "escalation_update"]
    assert covered  # Priya is told Sunita is going
    told = [p for p in pushes if p["audience"] == "parent" and p["type"] == "escalation_update"]
    assert told  # Amma hears who is coming


async def test_child_accepting_first_covers_the_neighbour(family, repo, pushes):
    await red_fall()
    esc_id = repo.list_escalations("amma")[0]["id"]
    await escalation.reply("amma", esc_id, responder="priya", decision="accept")
    assert [p for p in pushes if p["audience"] == "sunita" and p["type"] == "escalation_update"]
    with pytest.raises(Conflict):
        await escalation.reply("amma", esc_id, responder="sunita", decision="accept")


async def test_neighbour_declining_leaves_the_child_chain_running(family, repo, pushes):
    await red_fall()
    esc_id = repo.list_escalations("amma")[0]["id"]
    esc = await escalation.reply("amma", esc_id, responder="sunita", decision="decline")
    assert esc["parallel"] == [] and esc["current_contact"] == "priya"


async def test_without_prior_consent_the_neighbour_is_not_asked_first(family, repo, pushes, seeded):
    profile = repo.get_profile("amma")
    profile.pop("fall_preconsent_neighbour")
    repo.put_profile("amma", profile)
    await red_fall()
    assert asks(pushes) == ["priya"]
