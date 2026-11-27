"""After a fall, "theek hoon" goes through the Get-Up Vote unless Naive mode is on (bible v5 §6 L4, §17a)."""

from datetime import timedelta

import pytest

from agents import companion, orchestrator
from agents.schemas import CompanionReply
from core import clock


@pytest.fixture
def says(monkeypatch):
    """Fake the companion: each call returns the next queued reply."""
    replies: list[CompanionReply] = []

    async def fake_respond(parent_id, text, *, investigating, source):
        reply = replies.pop(0) if replies else CompanionReply(say="ठीक है।", language="hi-IN")
        return reply, companion.RunEffects(), type("G", (), {"denied_tools": []})()

    monkeypatch.setattr(companion, "respond", fake_respond)
    return replies


OK = CompanionReply(say="अच्छा।", language="hi-IN", parent_says_okay=True)
P_REF = 920.00


def stream(repo, *, p_hpa, steps, seconds=30, arm_var=0.2):
    start = clock.now()
    repo.add_signal("amma", "getup_ref", p_ref_hpa=P_REF, on_wrist=True, charging=False, spin_deg=0)
    for t in range(0, seconds + 1, 2):
        clock.set_now(start + timedelta(seconds=t))
        repo.add_signal("amma", "getup_sample", p_hpa=p_hpa, arm_var=arm_var, steps=steps if t >= 10 else 0)


async def test_theek_hoon_while_still_on_floor_is_peela_not_resolved(seeded, repo, pushes, sfn, says):
    await orchestrator.on_watch("amma", "fall")
    stream(repo, p_hpa=P_REF + 0.09, steps=0, arm_var=4.0)  # on the floor, waving an arm
    says.append(OK)
    out = await orchestrator.on_parent_turn("amma", "theek hoon", source="voice", duration_sec=1.2)

    assert out["fall_tier"] == "PEELA" and out["resolved"] is False
    assert out["votes"]["height"] == "down" and out["votes"]["movement"] == "down"
    assert repo.list_alerts("amma")[0]["status"] == "peela"
    assert not sfn.started  # no siren: the yellow message is the next piece


async def test_theek_hoon_after_getting_up_and_walking_is_hara(seeded, repo, pushes, sfn, says):
    await orchestrator.on_watch("amma", "fall")
    stream(repo, p_hpa=P_REF + 0.01, steps=9)
    says.append(OK)
    out = await orchestrator.on_parent_turn("amma", "haan theek hoon", source="voice", duration_sec=1.5)

    assert out["fall_tier"] == "HARA" and out["resolved"] is True
    assert repo.open_investigation("amma") is None
    assert repo.list_alerts("amma")[0]["status"] == "resolved"


async def test_no_sensor_data_yet_is_peela_because_abstain_means_not_up(seeded, repo, pushes, sfn, says):
    await orchestrator.on_watch("amma", "fall")
    says.append(OK)
    out = await orchestrator.on_parent_turn("amma", "theek hoon", source="voice", duration_sec=1.0)
    assert out["fall_tier"] == "PEELA"


async def test_watch_im_okay_button_after_fall_also_goes_through_vote(seeded, repo, pushes, sfn):
    await orchestrator.on_watch("amma", "fall")
    out = await orchestrator.on_watch("amma", "im_okay")
    assert out["fall_tier"] == "PEELA" and out["resolved"] is False


async def test_naive_mode_keeps_the_old_trap_for_the_demo(seeded, repo, pushes, sfn, says, monkeypatch):
    monkeypatch.setattr(orchestrator, "NAIVE_MODE", True)
    await orchestrator.on_watch("amma", "fall")
    stream(repo, p_hpa=P_REF + 0.09, steps=0)
    says.append(OK)
    out = await orchestrator.on_parent_turn("amma", "theek hoon", source="voice", duration_sec=1.0)
    assert out["resolved"] is True and "fall_tier" not in out
    assert repo.open_investigation("amma") is None


async def test_ok_with_pain_words_escalates(seeded, repo, pushes, sfn, says):
    await orchestrator.on_watch("amma", "fall")
    stream(repo, p_hpa=P_REF + 0.01, steps=9)
    says.append(OK)
    out = await orchestrator.on_parent_turn("amma", "theek hoon bas thoda dard hai", source="voice", duration_sec=2.5)
    assert out["fall_tier"] == "LAAL" and "pain_words" in out["flags"]
    assert sfn.started
