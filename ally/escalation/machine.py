"""FamilyEscalation workflow, run from the database instead of AWS Step Functions.

Same shape as the old state machine: ask each child in order (a reply or a timeout moves on) →
ask the parent about the neighbour → contact the neighbour only if Cedar allows, and wait for them →
otherwise (or if the neighbour can't come) notify every child. Any error goes to the failsafe, which notifies every child and releases the lock.

Progress lives on the ESC item under `machine`. While someone is being asked, the item carries
`awaiting` and a `due_at`; the per-minute sweep resumes anything past due as a timeout, and a reply
resumes it straight away. `token_version` makes the two race-safe: whichever consumes it first wins.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from config import ESCALATION_CONTACT_TIMEOUT
from core import clock
from core.log import log
from escalation import steps
from store.repo import get_repo

_FINAL = ("accepted", "resolved", "stopped", "closed", "failed")


def _ids(parent_id: str, esc_id: str) -> dict[str, Any]:
    return {"parent_id": parent_id, "esc_id": esc_id}


def _wait(parent_id: str, esc_id: str, state: str, machine: dict[str, Any]) -> None:
    due = clock.iso(clock.now() + timedelta(seconds=ESCALATION_CONTACT_TIMEOUT))
    get_repo().update_escalation(parent_id, esc_id, machine={**machine, "state": state})
    get_repo().set_escalation_due(parent_id, esc_id, due)


async def start(parent_id: str, esc_id: str) -> None:
    try:
        plan = await steps.init(_ids(parent_id, esc_id))
        machine = {"contacts": plan["contacts"], "index": 0, "count": plan["count"], "state": "init"}
        get_repo().update_escalation(parent_id, esc_id, status="running", machine=machine)
        await _ask_next(parent_id, esc_id, machine)
    except Exception as exc:  # noqa: BLE001 — any failure must still reach the family
        log("escalation_machine_error", parent_id=parent_id, esc_id=esc_id, error=repr(exc))
        await steps.failsafe(_ids(parent_id, esc_id))


async def _ask_next(parent_id: str, esc_id: str, machine: dict[str, Any]) -> None:
    # Children who can't be asked (Cedar deny) are skipped without waiting.
    while machine["index"] < machine["count"]:
        event = {**_ids(parent_id, esc_id), "contacts": machine["contacts"], "index": machine["index"]}
        if (await steps.ask_contact(event))["asked"]:
            _wait(parent_id, esc_id, "ask_child", machine)
            return
        nxt = await steps.next_contact({**event, "reply": {"decision": "not_permitted"}})
        machine = {**machine, "index": nxt["index"]}
    if (await steps.ask_parent_neighbour(_ids(parent_id, esc_id)))["asked"]:
        _wait(parent_id, esc_id, "ask_parent", machine)
        return
    await _after_parent(parent_id, esc_id, "no_neighbour", machine)


async def _after_parent(parent_id: str, esc_id: str, decision: str, machine: dict[str, Any]) -> None:
    if (await steps.contact_neighbour({**_ids(parent_id, esc_id), "reply": {"decision": decision}}))["contacted"]:
        _wait(parent_id, esc_id, "ask_neighbour", machine)
        return
    await _give_up(parent_id, esc_id)


async def _give_up(parent_id: str, esc_id: str) -> None:
    await steps.notify_all(_ids(parent_id, esc_id))
    await steps.finish(_ids(parent_id, esc_id))


async def resume(parent_id: str, esc_id: str, decision: str) -> None:
    """Continue after a reply (accept/decline/confirm/deny) or a timeout."""
    repo = get_repo()
    esc = repo.get_escalation(parent_id, esc_id) or {}
    machine = esc.get("machine") or {}
    if esc.get("status") in _FINAL:
        return
    try:
        if machine.get("state") == "ask_child":
            event = {**_ids(parent_id, esc_id), "contacts": machine["contacts"], "index": machine["index"]}
            if decision == "accept":
                await steps.accepted(event)
                repo.update_escalation(parent_id, esc_id, machine={**machine, "state": "done"})
                return
            nxt = await steps.next_contact({**event, "reply": {"decision": decision}})
            await _ask_next(parent_id, esc_id, {**machine, "index": nxt["index"]})
        elif machine.get("state") == "ask_parent":
            await _after_parent(parent_id, esc_id, decision, machine)
        elif machine.get("state") == "ask_neighbour":
            repo.update_escalation(parent_id, esc_id, machine={**machine, "state": "done"})
            if decision == "accept":
                await steps.neighbour_accepted(_ids(parent_id, esc_id))
            else:
                await _give_up(parent_id, esc_id)
        else:
            log("escalation_resume_ignored", parent_id=parent_id, esc_id=esc_id, state=machine.get("state"))
    except Exception as exc:  # noqa: BLE001
        log("escalation_machine_error", parent_id=parent_id, esc_id=esc_id, error=repr(exc))
        await steps.failsafe(_ids(parent_id, esc_id))


async def sweep_timeouts() -> int:
    """Called every minute: anyone asked and past due counts as a timeout."""
    repo = get_repo()
    fired = 0
    for esc in repo.due_escalations(clock.now()):
        parent_id, esc_id = esc["parent_id"], esc["id"]
        # Consuming the token first means a reply arriving now gets a clean Conflict.
        if repo.consume_escalation_token(parent_id, esc_id, int(esc.get("token_version", 0))) is None:
            repo.set_escalation_due(parent_id, esc_id, None)
            continue
        await resume(parent_id, esc_id, "timeout")
        fired += 1
    return fired
