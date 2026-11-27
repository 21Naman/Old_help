"""Deterministic event engine. The model handles language and judgement; code decides what happens.

Events: parent turn, device signal (watch or phone), "I'm okay", and the one-minute sweep
(reminders, wake window, investigation and escalation timeouts).
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from agents import companion
from agents.schemas import CompanionReply, DeviationJudgment
from config import FALL_WINDOW_MIN, INVESTIGATION_WINDOW_MIN, NAIVE_MODE, PEELA_TIMEOUT_S, WAKE_GRACE_MIN
from core import clock
from core.errors import LLMError, NotConfigured
from core.ids import new_id
from core.names import display
from core.log import log
from escalation import machine as escalation_machine
from escalation import service as escalation
from getup import vote as getup_vote
from policy import consent
from policy.tiers import TIER_LABEL, decide
from proactive import channel, morning, reminders
from scoring import deviation, judge
from store.repo import get_repo

# ---- parent turns ---------------------------------------------------------------------------


async def on_parent_turn(
    parent_id: str,
    text: str,
    *,
    source: str,
    language: str | None = None,
    duration_sec: float | None = None,
) -> dict[str, Any]:
    repo = get_repo()
    profile = _profile(parent_id)
    today = clock.local_date()
    investigation = repo.open_investigation(parent_id)

    if text:
        repo.add_turn(parent_id, "parent", text, source=source, language=language)
        repo.set_day_if_absent(parent_id, today, "checkin_at", clock.iso(clock.now()))

    reply, effects, guard = await companion.respond(
        parent_id, text, investigating=bool(investigation), source=source
    )
    say = _compose_say(reply, effects, profile)
    rule = _resolve_pending_rule(parent_id, reply, effects)

    day_fields: dict[str, Any] = {}
    if reply.mood != "unknown":
        day_fields["mood"] = reply.mood
    if reply.parent_reports_unwell:
        day_fields["unwell_reported"] = True
    if day_fields:
        repo.update_day(parent_id, today, **day_fields)

    outcome: dict[str, Any] = {"escalated": False}
    if text:
        outcome = await _assess_parent_words(
            parent_id, profile, text, reply, investigation=investigation, duration_sec=duration_sec
        )
    repo.add_turn(parent_id, "ally", say, agent="companion", language=reply.language)
    return {
        "say": say,
        "language": reply.language,
        "mood": reply.mood,
        "pending_rule": rule,
        "reminders_created": [saved["id"] for _, saved in effects.reminders],
        "messages_sent": effects.messages_sent,
        "denied_tools": guard.denied_tools,
        **outcome,
    }


def _compose_say(reply: CompanionReply, effects: companion.RunEffects, profile: dict[str, Any]) -> str:
    """Tool effects use template confirmations so what Ally says always matches what was saved."""
    language = reply.language
    if effects.proposed_rule:
        desc = effects.proposed_rule["description_hi" if language == "hi-IN" else "description"]
        return f"{desc} ठीक है?" if language == "hi-IN" else f"{desc} Is that right?"
    if effects.reminders:
        return " ".join(reminders.confirmation(spec, language) for spec, _ in effects.reminders)
    return reply.say


def _resolve_pending_rule(
    parent_id: str, reply: CompanionReply, effects: companion.RunEffects
) -> dict[str, Any] | None:
    if effects.proposed_rule:
        return effects.proposed_rule
    pending = consent.pending_rule(parent_id)
    if pending and reply.confirms_pending_rule in ("yes", "no"):
        return consent.confirm_rule(parent_id, pending["id"], reply.confirms_pending_rule == "yes")
    return pending


async def _assess_parent_words(
    parent_id: str,
    profile: dict[str, Any],
    text: str,
    reply: CompanionReply,
    *,
    investigation: dict[str, Any] | None,
    duration_sec: float | None,
) -> dict[str, Any]:
    repo = get_repo()
    if reply.parent_says_okay and not reply.parent_reports_unwell:
        if _is_fall(investigation) and not NAIVE_MODE:
            # After a fall her "theek hoon" is one vote; her body has to agree (bible v5 L4).
            return await verify_fall_answer(parent_id, profile, investigation, text=text, duration_sec=duration_sec)
        if investigation or repo.active_escalation_id(parent_id):
            await on_im_okay(parent_id, source="parent_words")
            return {"escalated": False, "resolved": True}
        return {"escalated": False}

    gate = deviation.combine(
        deviation.utterance_gate(text),
        deviation.vocal_gate(text, duration_sec, profile["baseline"]),
    )
    if not gate.tripped and not reply.parent_reports_unwell:
        if investigation:
            # She answered and nothing is wrong in her words: that's a real response.
            repo.close_investigation(parent_id, investigation["id"], "answered")
            _resolve_alert(parent_id, investigation.get("alert_id"), "parent_answered")
        return {"escalated": False}

    judgment = await _judge_or_none(
        parent_name=profile["name"],
        baseline=profile["baseline"],
        gate=gate,
        utterance=text,
        recent_days=_recent_days(parent_id),
    )
    tier = decide(
        judgment,
        parent_name=profile["name"],
        parent_reports_unwell=reply.parent_reports_unwell,
        after_fall=bool(investigation and investigation.get("reason") == "fall"),
    )
    alert = _alert_for(parent_id, investigation, kind="parent_words", gate=gate, judgment=judgment, tier=tier.tier)
    if investigation:
        repo.close_investigation(parent_id, investigation["id"], "concern_confirmed")
    if not tier.escalate:
        return {"escalated": False, "alert_id": alert["id"], "tier": tier.tier}
    return await _escalate(parent_id, alert, tier.severity)


# ---- devices (watch or phone) & I'm okay -----------------------------------------------------


async def on_watch(
    parent_id: str,
    kind: str,
    *,
    steps: int | None = None,
    heart_rate: int | None = None,
    source: str = "watch",
) -> dict[str, Any]:
    """A sensor event from the watch or the phone. Both may be worn; events dedupe by day / window."""
    repo = get_repo()
    now = clock.now()
    signal = repo.add_signal(parent_id, kind, steps=steps, heart_rate=heart_rate, source=source)
    if kind == "im_okay":
        investigation = repo.open_investigation(parent_id)
        if _is_fall(investigation) and not NAIVE_MODE:
            return {"signal": signal, **(await verify_fall_answer(parent_id, _profile(parent_id), investigation, text="", duration_sec=None))}
        return {"signal": signal, **(await on_im_okay(parent_id, source=source))}
    if kind == "fall":
        return {"signal": signal, **(await on_possible_fall(parent_id, now, source=source))}
    if kind not in ("wake", "first_movement"):
        return {"signal": signal}

    today = clock.local_date(now)
    if not repo.set_day_if_absent(parent_id, today, "wake_at", clock.iso(now)):
        return {"signal": signal, "first_wake": False}
    repo.update_day(parent_id, today, wake_source=source)

    scheduled = reminders.schedule_after_wake(parent_id, now)
    resolved = False
    if repo.open_investigation(parent_id) or repo.active_escalation_id(parent_id):
        await on_im_okay(parent_id, source=f"{source}_wake")
        resolved = True
    result: dict[str, Any] = {"signal": signal, "first_wake": True, "after_wake_reminders": scheduled, "resolved": resolved}
    try:
        msg = await morning.run(parent_id, now)
        result["morning_message_id"] = msg["id"] if msg else None
    except Exception as exc:  # the wake is recorded either way; the failure is logged and returned
        log("morning_checkin_failed", parent_id=parent_id, error=repr(exc))
        result["morning_error"] = str(exc)
    return result


async def on_possible_fall(parent_id: str, now: Any, *, source: str = "watch") -> dict[str, Any]:
    """The watch or phone thinks she fell. Ask her first — one short question — then escalate fast if she can't answer.

    A fall is never a silent alert and never an immediate blast to the family: she gets a moment to
    say she is fine, and the window is minutes rather than the quarter hour a late wake-up gets.
    """
    repo = get_repo()
    profile = _profile(parent_id)
    # One tumble can fire twice, or on both the watch and the phone; one question per window.
    if not repo.claim_dedupe(parent_id, f"alert#fall#{clock.iso(now)[:15]}"):
        return {"fall": True, "skipped": "duplicate"}
    if repo.active_escalation_id(parent_id):
        return {"fall": True, "skipped": "already_escalating"}

    gate = deviation.GateResult(True, 0.8, [{"code": f"{source}_detected_possible_fall", "level": "strong"}])
    alert = _new_alert(parent_id, kind="fall", gate=gate, judgment=None, tier=1, status="investigating", source=source)
    inv = _open_investigation(parent_id, alert, now, minutes=FALL_WINDOW_MIN, reason="fall")
    hi = profile.get("language") == "hi-IN"
    body = (
        f"{display(profile, 'hi-IN')}, मुझे लगा कि आप गिर गई हैं। आप ठीक हैं?"
        if hi
        else f"{profile['name']}, it looked like you may have fallen. Are you alright?"
    )
    await channel.post(
        parent_id,
        audience="parent",
        kind="investigation",
        body=body,
        related_id=f"investigation#{inv['id']}",
        data={"reason": "fall"},
    )
    log("possible_fall", parent_id=parent_id, alert_id=alert["id"], window_min=FALL_WINDOW_MIN)
    return {"fall": True, "alert_id": alert["id"], "asked_parent": True}


def _is_fall(investigation: dict[str, Any] | None) -> bool:
    return bool(investigation and investigation.get("reason") == "fall")


def fall_evidence(parent_id: str, profile: dict[str, Any], investigation: dict[str, Any], *, text: str, duration_sec: float | None) -> getup_vote.FallEvidence:
    """Collect what the device reported since we asked her (`getup_ref` once, `getup_sample` every few seconds)."""
    asked = clock.parse_iso(investigation["asked_at"])
    signals = get_repo().signals_between(parent_id, asked - timedelta(seconds=30), clock.now())
    ref = next((s for s in reversed(signals) if s.get("kind") == "getup_ref"), {})
    samples = [s for s in signals if s.get("kind") == "getup_sample"]
    t0 = asked.timestamp()

    def secs(s: dict[str, Any]) -> float:
        return clock.parse_iso(s["at"]).timestamp() - t0

    steps = [int(s["steps"]) for s in samples if s.get("steps") is not None]
    strides = [int(s["strides"]) for s in samples if s.get("strides") is not None]
    vocal = (profile.get("baseline") or {}).get("vocal_baseline") or {}
    return getup_vote.FallEvidence(
        says_ok=True,
        reply_text=text,
        reply_seconds=duration_sec,
        usual_wpm=float(vocal.get("avg_words_per_min") or 110),
        dropped=bool(ref.get("dropped", False)),
        spin_deg=float(ref.get("spin_deg") or 0),
        on_wrist=ref.get("on_wrist", True),
        charging=bool(ref.get("charging", False)),
        p_ref_hpa=ref.get("p_ref_hpa"),
        pressure=[getup_vote.PressureSample(secs(s), float(s["p_hpa"]), float(s.get("arm_var") or 0)) for s in samples if s.get("p_hpa") is not None],
        step_events=max(steps) if steps else None,
        strides=max(strides) if strides else None,
        heart=[getup_vote.HeartSample(secs(s), int(s["hr"])) for s in samples if s.get("hr") is not None],
        spo2=min((int(s["spo2"]) for s in samples if s.get("spo2") is not None), default=None),
        ppg_lost=any(s.get("ppg_lost") for s in samples),
    )


async def verify_fall_answer(
    parent_id: str, profile: dict[str, Any], investigation: dict[str, Any], *, text: str, duration_sec: float | None
) -> dict[str, Any]:
    """She says she's fine after a fall. Decide HARA / PEELA / LAAL / GREY from her words and her body."""
    repo = get_repo()
    result = getup_vote.decide(fall_evidence(parent_id, profile, investigation, text=text, duration_sec=duration_sec))
    alert = repo.get_alert(parent_id, investigation.get("alert_id") or "")
    outcome: dict[str, Any] = {"escalated": False, "fall_tier": result.tier, "votes": result.votes, "flags": result.flags}
    log("fall_vote", parent_id=parent_id, tier=result.tier, votes=result.votes, flags=result.flags)

    if result.tier == "HARA":
        await on_im_okay(parent_id, source="fall_verified")
        return {**outcome, "resolved": True}
    if result.tier == "GREY":
        repo.close_investigation(parent_id, investigation["id"], "grey")
        _resolve_alert(parent_id, investigation.get("alert_id"), "grey_cannot_tell")
        return {**outcome, "resolved": True}
    if result.tier == "LAAL":
        repo.close_investigation(parent_id, investigation["id"], "concern_confirmed")
        if alert:
            alert = repo.update_alert(parent_id, alert, status="escalating", tier=2, fall_tier="LAAL", votes=result.votes)
            return {**outcome, **(await _escalate(parent_id, alert, "critical"))}
        return outcome
    # PEELA: she says she's fine but her body doesn't confirm it. Believe her out loud, and ask the
    # nearest child to call. No siren, no health detail. No answer turns it red.
    repo.close_investigation(parent_id, investigation["id"], "peela")
    peela = await _start_peela(parent_id, profile, alert, votes=result.votes, spoken_reply=bool(text))
    return {**outcome, "resolved": False, **peela}


def nearest_child(parent_id: str, profile: dict[str, Any]) -> dict[str, Any] | None:
    """The child most likely to reach her: same city first, then the family's own order."""
    children = [m for m in get_repo().list_members(parent_id) if m.get("role") == "child"]
    if not children:
        return None
    city = (profile.get("city") or "").strip().lower()
    same_city = [m for m in children if city and (m.get("city") or "").strip().lower() == city]
    return (same_city or children)[0]


async def _start_peela(
    parent_id: str, profile: dict[str, Any], alert: dict[str, Any] | None, *, votes: dict[str, Any], spoken_reply: bool
) -> dict[str, Any]:
    repo = get_repo()
    child = nearest_child(parent_id, profile)
    hi = profile.get("language") == "hi-IN"
    who = display(child, "hi-IN" if hi else "en-IN", "")
    say = (
        f"ठीक है {display(profile, 'hi-IN')}, आपकी बात मान ली। बस {who} को बोल रही हूँ एक बार कॉल कर ले।"
        if hi
        else f"Okay {profile['name']}, I believe you. I'm just asking {who} to give you a call."
    )
    due = clock.iso(clock.now() + timedelta(seconds=PEELA_TIMEOUT_S))
    if alert:
        alert = repo.update_alert(
            parent_id, alert, status="peela", fall_tier="PEELA", votes=votes,
            peela_member=child["id"] if child else None, peela_due_at=due,
        )
    if child and alert:
        await channel.post(
            parent_id,
            audience=child["id"],
            kind="peela_call",
            body=f"Please give {profile['name']} a call when you can.",
            related_id=f"peela#{alert['id']}",
            data={"alert_id": alert["id"], "actions": ["spoke", "no_answer"], "due_at": due},
        )
    if not spoken_reply and alert:
        # She pressed the button instead of speaking, so tell her on the watch/tablet too.
        await channel.post(parent_id, audience="parent", kind="peela_said", body=say, related_id=f"peela_parent#{alert['id']}")
    log("peela_started", parent_id=parent_id, member=child["id"] if child else None, due_at=due)
    return {"say": say, "peela_member": child["id"] if child else None, "peela_due_at": due}


async def peela_reply(parent_id: str, alert_id: str, member_id: str, answer: str) -> dict[str, Any]:
    """The child answers the yellow ask: "spoke" (she's fine) closes it, "no_answer" turns it red."""
    repo = get_repo()
    alert = repo.get_alert(parent_id, alert_id)
    if not alert or alert.get("status") != "peela":
        return {"ok": False, "status": alert.get("status") if alert else None}
    if answer == "spoke":
        repo.update_alert(parent_id, alert, status="resolved", resolution=f"family_spoke:{member_id}")
        log("peela_resolved", parent_id=parent_id, member=member_id)
        return {"ok": True, "status": "resolved"}
    return {"ok": True, **(await _peela_to_laal(parent_id, alert, reason=f"no_answer:{member_id}"))}


async def _peela_to_laal(parent_id: str, alert: dict[str, Any], *, reason: str) -> dict[str, Any]:
    alert = get_repo().update_alert(parent_id, alert, status="escalating", tier=2, fall_tier="LAAL", peela_outcome=reason)
    log("peela_to_laal", parent_id=parent_id, reason=reason)
    return {"status": "escalating", **(await _escalate(parent_id, alert, "critical"))}


_STAY_ACTIVE = ("starting", "running", "asking", "asking_parent", "asking_neighbour", "accepted")
STILL_DOWN_HPA = 0.05  # wrist this much lower than her pre-fall reading = still on the floor
ETA_GRACE_MIN = 15


def still_on_floor(parent_id: str, now: Any) -> bool | None:
    """From the watch's last minute of readings. None when there is no recent data (never guessed)."""
    signals = get_repo().signals_between(parent_id, now - timedelta(minutes=30), now)
    ref = next((x for x in reversed(signals) if x.get("kind") == "getup_ref" and x.get("p_ref_hpa") is not None), None)
    recent = [x for x in signals if x.get("kind") == "getup_sample" and x.get("p_hpa") is not None
              and clock.parse_iso(x["at"]) >= now - timedelta(seconds=60)]
    if not ref or not recent:
        return None
    return float(recent[-1]["p_hpa"]) - float(ref["p_ref_hpa"]) > STILL_DOWN_HPA


async def stay_ticks(now: Any) -> int:
    """Stay with her (bible v5 L7): every minute while help is on the way, tell her where it stands.

    Status lines come from the escalation record only (No False Comfort): nobody is "coming" unless they
    accepted, and the minutes are the helper's own estimate.
    """
    repo = get_repo()
    ticks = 0
    for parent_id in _parent_ids():
        esc_id = repo.active_escalation_id(parent_id)
        esc = repo.get_escalation(parent_id, esc_id) if esc_id else None
        if not esc or esc.get("status") not in _STAY_ACTIVE:
            continue
        profile = _profile(parent_id)
        hi = profile.get("language") == "hi-IN"
        responder = repo.get_member(parent_id, esc.get("responder") or "") if esc.get("status") == "accepted" else None
        eta_at = esc.get("eta_at")
        mins = max(1, round((clock.parse_iso(eta_at) - now).total_seconds() / 60)) if eta_at else None
        if responder:
            who = display(responder, "hi-IN" if hi else "en-IN", "")
            if hi:
                body = f"{who} आ रहे हैं" + (f", लगभग {mins} मिनट" if mins else "") + "। मैं यहीं हूँ।"
            else:
                body = f"{who} is on the way" + (f", about {mins} minutes" if mins else "") + ". I'm right here."
        else:
            body = "मैं यहीं हूँ, मदद बुला रही हूँ।" if hi else "I'm right here. I'm getting help."
        await channel.post(parent_id, audience="parent", kind="stay", body=body, related_id=f"stay#{esc['id']}#{clock.iso(now)[:16]}")

        down = still_on_floor(parent_id, now)
        if down is not None and down != esc.get("still_on_floor"):
            repo.update_escalation(parent_id, esc["id"], still_on_floor=down)

        if responder and eta_at and not esc.get("overdue_asked") and now > clock.parse_iso(eta_at) + timedelta(minutes=ETA_GRACE_MIN):
            await channel.post(
                parent_id,
                audience=responder["id"],
                kind="escalation_update",
                body=f"Are you still on your way to {profile['name']}? Tap Arrived when you're with her.",
                related_id=f"stay#{esc['id']}#overdue",
            )
            repo.update_escalation(parent_id, esc["id"], overdue_asked=True)
            log("stay_eta_overdue", parent_id=parent_id, esc_id=esc["id"], responder=responder["id"])
        ticks += 1
    return ticks


async def peela_timeouts(now: Any) -> int:
    count = 0
    for parent_id in _parent_ids():
        for alert in get_repo().list_alerts(parent_id, limit=20):
            due = alert.get("peela_due_at")
            if alert.get("status") == "peela" and due and clock.parse_iso(due) <= now:
                await _peela_to_laal(parent_id, alert, reason="timeout")
                count += 1
    return count


def _open_investigation(
    parent_id: str, alert: dict[str, Any], now: Any, *, minutes: int, reason: str
) -> dict[str, Any]:
    inv = {
        "id": new_id(),
        "alert_id": alert["id"],
        "asked_at": clock.iso(now),
        "due_at": clock.iso(now + timedelta(minutes=minutes)),
        "status": "open",
        "reason": reason,
    }
    get_repo().put_investigation(parent_id, inv)
    return inv


async def on_im_okay(parent_id: str, *, source: str) -> dict[str, Any]:
    repo = get_repo()
    now = clock.now()
    repo.update_day(parent_id, clock.local_date(now), im_okay_at=clock.iso(now))
    investigation = repo.open_investigation(parent_id)
    if investigation:
        repo.close_investigation(parent_id, investigation["id"], "parent_okay")
        _resolve_alert(parent_id, investigation.get("alert_id"), f"parent_okay:{source}")
    stopped = await escalation.stop(parent_id, reason=f"parent_okay:{source}")
    if stopped:
        alert = repo.get_alert(parent_id, stopped.get("alert_id", ""))
        if alert:
            repo.update_alert(parent_id, alert, status="resolved", resolution=f"parent_okay:{source}")
    return {"okay": True, "investigation_closed": bool(investigation), "escalation_stopped": bool(stopped)}


# ---- sweep (every minute: external cron or the in-process scheduler) ------------------------


async def sweep() -> dict[str, Any]:
    now = clock.now()
    out: dict[str, Any] = {"reminders": await reminders.fire_due(now), "wake_checks": 0, "investigations": 0}
    repo = get_repo()
    for parent_id in _parent_ids():
        try:
            if await check_wake_window(parent_id, now):
                out["wake_checks"] += 1
        except Exception as exc:
            log("wake_check_failed", parent_id=parent_id, error=repr(exc))
    for inv in repo.due_investigations(now):
        try:
            await investigation_timeout(inv["parent_id"], inv)
            out["investigations"] += 1
        except Exception as exc:
            log("investigation_timeout_failed", parent_id=inv["parent_id"], error=repr(exc))
    try:
        out["stay"] = await stay_ticks(now)
    except Exception as exc:
        log("stay_tick_failed", error=repr(exc))
    try:
        out["peela_timeouts"] = await peela_timeouts(now)
    except Exception as exc:
        log("peela_sweep_failed", error=repr(exc))
    try:
        out["escalations"] = await escalation_machine.sweep_timeouts()
    except Exception as exc:
        log("escalation_sweep_failed", error=repr(exc))
    try:
        out["purged"] = repo.purge_expired()
    except Exception as exc:
        log("purge_failed", error=repr(exc))
    return out


async def check_wake_window(parent_id: str, now: Any) -> bool:
    repo = get_repo()
    profile = _profile(parent_id)
    today = clock.local_date(now)
    day = repo.get_day(parent_id, today)
    gate = deviation.no_wake_gate(profile["baseline"], today, now, WAKE_GRACE_MIN, woke=bool(day.get("wake_at") or day.get("im_okay_at")))
    if not gate.tripped or not repo.claim_dedupe(parent_id, f"alert#no_wake#{today}"):
        return False
    alert = _new_alert(parent_id, kind="no_wake", gate=gate, judgment=None, tier=1, status="investigating")
    inv = _open_investigation(parent_id, alert, now, minutes=INVESTIGATION_WINDOW_MIN, reason="no_wake")
    hi = profile.get("language") == "hi-IN"
    body = (
        f"सुप्रभात {display(profile, 'hi-IN')}। आप आमतौर पर इस समय तक उठ जाती हैं — सब ठीक है?"
        if hi
        else f"Good morning {profile['name']}. You're usually up by now — is everything alright?"
    )
    await channel.post(parent_id, audience="parent", kind="investigation", body=body, related_id=f"investigation#{inv['id']}")
    log("investigation_opened", parent_id=parent_id, alert_id=alert["id"])
    return True


async def investigation_timeout(parent_id: str, inv: dict[str, Any]) -> dict[str, Any]:
    repo = get_repo()
    if not repo.close_investigation(parent_id, inv["id"], "no_response"):
        return {"skipped": "already_closed"}
    profile = _profile(parent_id)
    alert = repo.get_alert(parent_id, inv.get("alert_id", "")) or _new_alert(
        parent_id, kind="no_response", gate=None, judgment=None, tier=1, status="investigating"
    )
    after_fall = inv.get("reason") == "fall" or alert.get("kind") == "fall"
    gate = deviation.GateResult(
        True, 0.6, [*(alert.get("gate") or []), {"code": "no_response_after_check_in", "level": "strong"}]
    )
    judgment = await _judge_or_none(
        parent_name=profile["name"],
        baseline=profile["baseline"],
        gate=gate,
        no_response=True,
        after_fall=after_fall,
        recent_days=_recent_days(parent_id),
    )
    tier = decide(judgment, parent_name=profile["name"], no_response=True, after_fall=after_fall)
    alert = repo.update_alert(
        parent_id, alert, judgment=judgment.model_dump() if judgment else None, gate=gate.reasons, tier=tier.tier
    )
    return await _escalate(parent_id, alert, tier.severity)


# ---- helpers --------------------------------------------------------------------------------


async def _judge_or_none(**kwargs: Any) -> DeviationJudgment | None:
    """A model outage must never silence the family: policy then decides without a judgement."""
    try:
        return await judge.judge(**kwargs)
    except LLMError as exc:
        log("judge_unavailable", detail=exc.detail)
        return None


async def _escalate(parent_id: str, alert: dict[str, Any], severity: str) -> dict[str, Any]:
    try:
        esc = await escalation.start(parent_id, alert, severity)
    except NotConfigured as exc:
        log("escalation_not_configured", parent_id=parent_id, detail=exc.detail)
        return {"escalated": False, "alert_id": alert["id"], "tier": 2, "escalation_error": str(exc)}
    return {"escalated": True, "alert_id": alert["id"], "escalation_id": esc.get("id"), "tier": 2}


def _new_alert(
    parent_id: str,
    *,
    kind: str,
    gate: deviation.GateResult | None,
    judgment: DeviationJudgment | None,
    tier: int,
    status: str,
    source: str | None = None,
) -> dict[str, Any]:
    alert = {
        "id": new_id(),
        "created_at": clock.iso(clock.now()),
        "kind": kind,
        "status": status,
        "tier": tier,
        "gate": gate.reasons if gate else [],
        "gate_score": gate.score if gate else None,
        "judgment": judgment.model_dump() if judgment else None,
        "source": source,
    }
    get_repo().put_alert(parent_id, alert)
    return alert


def _alert_for(
    parent_id: str,
    investigation: dict[str, Any] | None,
    *,
    kind: str,
    gate: deviation.GateResult,
    judgment: DeviationJudgment | None,
    tier: int,
) -> dict[str, Any]:
    repo = get_repo()
    if investigation and investigation.get("alert_id"):
        existing = repo.get_alert(parent_id, investigation["alert_id"])
        if existing:
            return repo.update_alert(
                parent_id,
                existing,
                gate=[*(existing.get("gate") or []), *gate.reasons],
                judgment=judgment.model_dump() if judgment else None,
                tier=tier,
                status="escalating" if tier >= 2 else "monitoring",
            )
    return _new_alert(parent_id, kind=kind, gate=gate, judgment=judgment, tier=tier, status="escalating" if tier >= 2 else "monitoring")


def _resolve_alert(parent_id: str, alert_id: str | None, resolution: str) -> None:
    if not alert_id:
        return
    repo = get_repo()
    alert = repo.get_alert(parent_id, alert_id)
    if alert and alert.get("status") not in ("resolved",):
        repo.update_alert(parent_id, alert, status="resolved", resolution=resolution)


def _recent_days(parent_id: str) -> list[dict[str, Any]]:
    return get_repo().list_days(parent_id, clock.days_ago(6), clock.days_ago(1))


def _profile(parent_id: str) -> dict[str, Any]:
    profile = get_repo().get_profile(parent_id)
    if not profile:
        raise NotConfigured("This parent has not been set up yet.", detail=f"no PROFILE for {parent_id}")
    return profile


def _parent_ids() -> list[str]:
    from config import PARENT_ID

    return [PARENT_ID]


# ---- read model -----------------------------------------------------------------------------


def snapshot(parent_id: str, *, viewer: str) -> dict[str, Any]:
    """Backward-compatible AllyState for the web app. Family viewers never get the transcript."""
    repo = get_repo()
    profile = _profile(parent_id)
    now = clock.now()
    today = clock.local_date(now)
    day = repo.get_day(parent_id, today)
    history = repo.list_days(parent_id, clock.days_ago(13), clock.days_ago(1))
    members = repo.list_members(parent_id)
    alert = repo.open_alert(parent_id) or next(iter(repo.list_alerts(parent_id, limit=1)), None)
    esc_id = repo.active_escalation_id(parent_id)
    esc = repo.get_escalation(parent_id, esc_id, consistent=False) if esc_id else None
    investigation = repo.open_investigation(parent_id)
    tier = 1
    narration = "Most days, Ally says nothing at all."
    escalation_state = "none"
    if investigation:
        escalation_state = "investigating"
        narration = f"I'm checking in with {profile['name']} myself first."
    if esc:
        tier = 2
        escalation_state = {
            "accepted": "en_route",
            "resolved": "resolved",
            "asking": "coordinating",
            "asking_parent": "awaiting_confirmation",
        }.get(esc.get("status", ""), "coordinating")
        narration = f"I'm asking {profile['name']}'s family to check in."
    gate_reasons = (alert or {}).get("gate") if alert and alert.get("status") != "resolved" else []
    responder = (esc or {}).get("responder")
    responder_name = next((m["name"] for m in members if m["id"] == responder), None)
    state: dict[str, Any] = {
        "parent_id": parent_id,
        "parent_name": profile["name"],
        "language": profile.get("language", "hi-IN"),
        "honesty": "Days before today are simulated history used to establish a baseline. Today is live.",
        "honesty_label": "simulated history",
        "history_simulated": True,
        "today_live": True,
        "baseline": profile["baseline"],
        "history": [
            {
                "day": i + 1,
                "date": d["date"],
                "wake_detected_at": clock.hhmm(clock.parse_iso(d["wake_at"])) if d.get("wake_at") else None,
                "checkin_at": clock.hhmm(clock.parse_iso(d["checkin_at"])) if d.get("checkin_at") else None,
                "deviation_score": d.get("score", 0),
                "notes": d.get("notes"),
                "simulated": bool(d.get("simulated")),
            }
            for i, d in enumerate(history)
        ],
        "family_roster": [
            {
                "id": m["id"],
                "name": m["name"],
                "relation": m.get("relation", ""),
                "role": m.get("role"),
                "availability": _availability(m["id"], esc),
            }
            for m in members
        ],
        "today": {
            "date": today,
            "wake_detected_at": clock.hhmm(clock.parse_iso(day["wake_at"])) if day.get("wake_at") else None,
            "im_okay_at": clock.hhmm(clock.parse_iso(day["im_okay_at"])) if day.get("im_okay_at") else None,
            "checkin_completed": bool(day.get("checkin_at")),
            "reminders_done": day.get("reminders_done", 0),
            "activity_log": [],
            "call_log": [],
            "deviation_score": (alert or {}).get("gate_score") or 0 if gate_reasons else 0,
            "deviation_reasons": [{"code": r["code"], "weight": 0, "level": r.get("level", "")} for r in gate_reasons or []],
            "simulated": False,
        },
        "escalation_state": escalation_state,
        "escalation_id": esc_id,
        "tier": tier,
        "tier_label": TIER_LABEL[tier],
        "tier_narration": narration,
        "mode": "coordination" if esc else ("investigation" if investigation else "companion"),
        "last_decision": {
            "responder": responder_name,
            "summary": _summary(esc, members, profile),
            "ack": (esc or {}).get("status"),
        }
        if esc
        else None,
        "open_alert": _alert_view(alert) if alert else None,
        "pending_rule": consent.pending_rule(parent_id) if viewer == "parent" else None,
        "transcript": [],
        "updated_at": clock.iso(now),
    }
    if viewer == "parent":
        state["transcript"] = [
            {"speaker": t["speaker"], "text": t["text"], "agent": t.get("agent"), "at": t["at"]}
            for t in repo.recent_turns(parent_id, limit=20)
        ]
    return state


def _availability(member_id: str, esc: dict[str, Any] | None) -> str:
    if not esc:
        return "unknown"
    if esc.get("responder") == member_id:
        return "arrived" if esc.get("status") == "resolved" else "en_route"
    if esc.get("current_contact") == member_id:
        return "asked"
    for event in reversed(esc.get("timeline", [])):
        if event.get("member") == member_id and event.get("event") in ("decline", "timeout", "not_permitted"):
            return "unavailable" if event["event"] == "decline" else "no_answer"
    return "unknown"


def _summary(esc: dict[str, Any] | None, members: list[dict[str, Any]], profile: dict[str, Any]) -> str:
    if not esc:
        return ""
    names = {m["id"]: m["name"] for m in members}
    status = esc.get("status")
    if status == "accepted":
        return f"{names.get(esc.get('responder'), 'Family')} is on the way to {profile['name']}."
    if status == "resolved":
        return f"{names.get(esc.get('responder'), 'Family')} is with {profile['name']} now."
    if status == "asking":
        return f"Ally is asking {names.get(esc.get('current_contact'), 'family')} to check on {profile['name']}."
    if status == "asking_parent":
        return f"No child could go; Ally is asking {profile['name']} about a neighbour."
    return f"Ally is coordinating family for {profile['name']}."


def _alert_view(alert: dict[str, Any]) -> dict[str, Any]:
    return {k: alert.get(k) for k in ("id", "created_at", "kind", "status", "tier", "judgment", "escalation_id", "source")}
