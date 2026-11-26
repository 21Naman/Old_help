"""What a person being asked to help gets told: the family respond page and the guard handset.

Only records and policy write these notes, never the model. Health detail is included only when the
parent shares health with that person; anything held back is listed so nobody mistakes it for "none".
"""

from __future__ import annotations

from typing import Any

from core import clock
from core.errors import NotFound
from escalation import tokens
from policy.consent import authorize
from store.repo import get_repo

EMERGENCY_NUMBER = "112"

_WHAT = {
    "fall": "{device} picked up what looked like a fall, and {name} didn't answer when Suraksha asked if she was alright.",
    "no_wake": "{name} hasn't been up by her usual time, and didn't answer when Suraksha checked in.",
    "no_response": "{name} didn't answer when Suraksha checked in.",
    "unwell": "{name} said she wasn't feeling well.",
}


def _time(iso: str | None) -> str:
    if not iso:
        return ""
    try:
        return clock.parse_iso(iso).strftime("%-I:%M %p")
    except ValueError:
        return iso


def _shares_health(parent_id: str, member_id: str) -> bool:
    member = get_repo().get_member(parent_id, member_id) or {}
    kind = "Neighbour" if member.get("role") == "neighbour" else "Family"
    return authorize(
        parent_id,
        principal=(kind, member_id),
        action="read_day_log",
        topic="health",
        requested_by=f"{kind}::{member_id}",
        audit=False,
    ).allowed


def _facts(parent_id: str, esc: dict[str, Any], alert: dict[str, Any], member_id: str) -> tuple[list[str], list[str]]:
    repo = get_repo()
    profile = repo.get_profile(parent_id) or {}
    facts: list[str] = []
    withheld: list[str] = []
    if alert.get("created_at"):
        facts.append(f"First noticed at {_time(alert['created_at'])}.")
    if alert.get("source"):
        facts.append(f"Signal from her {alert['source']}.")
    day = repo.get_day(parent_id, clock.local_date())
    if day.get("wake_at"):
        facts.append(f"She was up at {_time(day['wake_at'])} today.")
    asked = [e.get("member") for e in esc.get("timeline", []) if e.get("event") == "asked" and e.get("member") != member_id]
    if asked:
        names = [(repo.get_member(parent_id, m) or {}).get("name", m) for m in asked]
        facts.append("Already asked: " + ", ".join(names) + ".")
    reasons = (alert.get("judgment") or {}).get("reasons") or []
    if reasons and _shares_health(parent_id, member_id):
        facts.extend(reasons[:3])
    elif reasons:
        withheld.append(f"{profile.get('name', 'Amma')} keeps her health details private.")
    withheld.append("Her conversations with Suraksha are never shared.")
    return facts, withheld


def note(parent_id: str, esc_id: str, member_id: str) -> dict[str, Any]:
    repo = get_repo()
    esc = repo.get_escalation(parent_id, esc_id)
    if not esc:
        raise NotFound("That request no longer exists.")
    alert = repo.get_alert(parent_id, esc.get("alert_id", "")) or {}
    profile = repo.get_profile(parent_id) or {}
    name = profile.get("name", "Amma")
    device = f"Her {alert['source']}" if alert.get("source") else "Her watch or phone"
    facts, withheld = _facts(parent_id, esc, alert, member_id)
    return {
        "escalation_id": esc_id,
        "severity": esc.get("severity"),
        "status": esc.get("status"),
        "at": alert.get("created_at") or esc.get("created_at"),
        "parent_name": name,
        "headline": f"{name} may need someone to check on her.",
        "what_happened": _WHAT.get(alert.get("kind", ""), _WHAT["no_response"]).format(name=name, device=device),
        "checks": [
            f"Call {name} first.",
            "If she doesn't pick up, go and see her, or ask someone nearby.",
            f"If it's urgent, call {EMERGENCY_NUMBER}.",
        ],
        "facts": facts,
        "withheld": withheld,
        "written_by": "records",
        "emergency_number": EMERGENCY_NUMBER,
    }


def guard_call(parent_id: str) -> dict[str, Any]:
    """Ring the neighbour's handset while the workflow has asked the neighbour and nobody has accepted."""
    repo = get_repo()
    esc_id = repo.active_escalation_id(parent_id)
    esc = repo.get_escalation(parent_id, esc_id) if esc_id else None
    neighbour_id = (esc or {}).get("neighbour_id")
    if not esc or not neighbour_id or esc.get("status") != "asking_neighbour" or not esc.get("awaiting"):
        return {"ringing": False}
    profile = repo.get_profile(parent_id) or {}
    neighbour = repo.get_member(parent_id, neighbour_id) or {"name": neighbour_id}
    name = profile.get("name", "Amma")
    n = note(parent_id, esc["id"], neighbour_id)
    return {
        "ringing": True,
        "escalation_id": esc["id"],
        "reply_token": tokens.sign(parent_id, esc["id"], neighbour_id, int(esc.get("token_version", 0))),
        "caller": "Suraksha",
        "subject": name,
        "guard_name": neighbour.get("name"),
        "address": profile.get("address"),
        "facts": n["facts"],
        "say": f"Hello {neighbour.get('name', '')}. This is Suraksha. {n['what_happened']} Her family couldn't be reached. Could you check on her?",
        "withheld": n["withheld"],
        "emergency_number": EMERGENCY_NUMBER,
    }
