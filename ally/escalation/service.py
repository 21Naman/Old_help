"""Family escalation lifecycle around the workflow in `escalation.machine`.

start → (workflow asks children one by one, then the parent about the neighbour) → reply/stop.
"""

from __future__ import annotations

from typing import Any, Literal

from core import clock
from core.errors import Conflict, Forbidden, NotFound
from core.ids import new_id
from core.log import log
from core.names import display
from escalation import machine
from proactive import channel
from store.repo import get_repo

Decision = Literal["accept", "decline", "arrived", "confirm", "deny"]


async def start(parent_id: str, alert: dict[str, Any], severity: str) -> dict[str, Any]:
    repo = get_repo()
    esc_id = new_id()
    if not repo.acquire_escalation_lock(parent_id, esc_id):
        existing = repo.active_escalation_id(parent_id)
        log("escalation_already_active", parent_id=parent_id, esc_id=existing)
        return repo.get_escalation(parent_id, existing) or {"id": existing}
    esc = {
        "id": esc_id,
        "alert_id": alert["id"],
        "alert_created_at": alert["created_at"],
        "severity": severity,
        "status": "starting",
        "token_version": 0,
        "created_at": clock.iso(clock.now()),
        "timeline": [{"at": clock.iso(clock.now()), "event": "started", "severity": severity}],
        "contacted": [],
    }
    repo.put_escalation(parent_id, esc)
    repo.update_alert(parent_id, alert, status="escalating", escalation_id=esc_id, tier=2)
    await machine.start(parent_id, esc_id)
    return repo.get_escalation(parent_id, esc_id) or esc


async def stop(parent_id: str, reason: str) -> dict[str, Any] | None:
    """Parent is okay: stop asking people, tell anyone already asked."""
    repo = get_repo()
    esc_id = repo.active_escalation_id(parent_id)
    if not esc_id:
        return None
    esc = repo.get_escalation(parent_id, esc_id) or {}
    repo.set_escalation_due(parent_id, esc_id, None)
    repo.append_escalation_event(parent_id, esc_id, {"event": "stopped", "reason": reason})
    repo.expire_pending_messages(parent_id, f"esc#{esc_id}#ask#")
    repo.update_escalation(parent_id, esc_id, status="stopped", awaiting=None, current_contact=None)
    profile = repo.get_profile(parent_id) or {}
    for member_id in esc.get("contacted", []):
        await channel.post(
            parent_id,
            audience=member_id,
            kind="all_clear",
            body=f"{profile.get('name', 'Amma')} says she's okay. No need to go.",
            related_id=f"esc#{esc_id}#allclear#{member_id}",
        )
    repo.release_escalation_lock(parent_id, esc_id)
    return repo.get_escalation(parent_id, esc_id)


async def reply(
    parent_id: str,
    esc_id: str,
    *,
    responder: str,
    decision: Decision,
    token_version: int | None = None,
) -> dict[str, Any]:
    """A child (accept/decline/arrived) or the parent (confirm/deny neighbour) answers."""
    repo = get_repo()
    esc = repo.get_escalation(parent_id, esc_id)
    if not esc:
        raise NotFound("That request no longer exists.")

    if decision == "arrived":
        if esc.get("responder") != responder:
            raise Forbidden("Only the person who said they'd go can mark arrival.")
        return await _arrived(parent_id, esc)

    if responder in (esc.get("parallel") or []) and esc.get("current_contact") != responder:
        if esc.get("status") not in ("asking", "asking_parent", "asking_neighbour", "running"):
            raise Conflict("Someone else is already going.")
        repo.append_escalation_event(parent_id, esc_id, {"event": "reply", "by": responder, "decision": decision, "parallel": True})
        if decision == "accept":
            await machine.parallel_accept(parent_id, esc_id)
        else:
            repo.update_escalation(parent_id, esc_id, parallel=[p for p in esc.get("parallel", []) if p != responder])
        return repo.get_escalation(parent_id, esc_id) or esc

    if esc.get("current_contact") != responder or esc.get("status") not in ("asking", "asking_parent", "asking_neighbour"):
        raise Conflict("Ally has already asked someone else.")
    version = int(esc.get("token_version", 0)) if token_version is None else token_version
    if repo.consume_escalation_token(parent_id, esc_id, version) is None:
        raise Conflict("Ally has already asked someone else.")
    repo.append_escalation_event(parent_id, esc_id, {"event": "reply", "by": responder, "decision": decision})
    await machine.resume(parent_id, esc_id, decision)
    return repo.get_escalation(parent_id, esc_id) or esc


async def _arrived(parent_id: str, esc: dict[str, Any]) -> dict[str, Any]:
    repo = get_repo()
    esc_id = esc["id"]
    repo.append_escalation_event(parent_id, esc_id, {"event": "arrived", "by": esc.get("responder")})
    repo.update_escalation(parent_id, esc_id, status="resolved", resolved_at=clock.iso(clock.now()))
    alert = repo.get_alert(parent_id, esc["alert_id"])
    if alert:
        repo.update_alert(parent_id, alert, status="resolved", resolved_by=esc.get("responder"))
    member = repo.get_member(parent_id, esc.get("responder", "")) or {}
    profile = repo.get_profile(parent_id) or {}
    hi = profile.get("language") == "hi-IN"
    await channel.post(
        parent_id,
        audience="parent",
        kind="escalation_update",
        body=(
            f"{display(member, 'hi-IN', 'आपका परिवार')} आ गए हैं।" if hi else f"{member.get('name', 'Family')} is here now."
        ),
        related_id=f"esc#{esc_id}#arrived",
    )
    repo.release_escalation_lock(parent_id, esc_id)
    return repo.get_escalation(parent_id, esc_id) or esc


def view(parent_id: str, esc_id: str) -> dict[str, Any]:
    esc = get_repo().get_escalation(parent_id, esc_id, consistent=False)
    if not esc:
        raise NotFound("That request no longer exists.")
    return {k: v for k, v in esc.items() if k not in ("machine",)}
