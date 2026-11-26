"""Seed Amma's profile, family roster and 13 days of *simulated* history (dated relative to today).

Optionally creates sign-in users for the parent tablet and each family member (username = member id,
the parent's username is "amma").

    python scripts/seed.py                                  # profile + roster + history
    python scripts/seed.py --users --password 'Temp#Pass123'   # also create/refresh sign-in users

`--password` may be omitted when ALLY_SEED_PASSWORD is set (handy on a Render shell).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from auth import hash_password  # noqa: E402
from core import clock  # noqa: E402
from store.repo import get_repo  # noqa: E402

SEED = ROOT / "seed" / "amma.json"


def seed_data() -> None:
    data = json.loads(SEED.read_text(encoding="utf-8"))
    parent_id = data["parent_id"]
    repo = get_repo()
    repo.put_profile(parent_id, data["profile"])
    for member in data["members"]:
        repo.put_member(parent_id, member)
    template = data["history_template"]
    for offset, day_t in enumerate(template):
        day = clock.days_ago(len(template) - offset)
        repo.update_day(
            parent_id,
            day,
            wake_at=clock.iso(clock.at_local(day, day_t["wake"])),
            checkin_at=clock.iso(clock.at_local(day, day_t["checkin"])),
            mood=day_t["mood"],
            reminders_done=day_t["reminders_done"],
            notes=day_t["notes"],
            simulated=True,
            score=0.05,
        )
    print(f"seeded {parent_id}: profile, {len(data['members'])} members, {len(template)} simulated days")


def seed_users(password: str) -> None:
    data = json.loads(SEED.read_text(encoding="utf-8"))
    repo = get_repo()
    users = [("amma", "parent", "parent")] + [(m["id"], m["id"], "family") for m in data["members"]]
    hashed = hash_password(password)
    for username, member_id, group in users:
        repo.put_user(
            {"username": username, "member_id": member_id, "group": group, "parent_id": data["parent_id"], "password_hash": hashed}
        )
        print(f"user {username} → {group}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", action="store_true")
    parser.add_argument("--password", default=os.getenv("ALLY_SEED_PASSWORD", ""))
    args = parser.parse_args()
    seed_data()
    if args.users:
        if not args.password:
            raise SystemExit("--password (or ALLY_SEED_PASSWORD) is required with --users")
        seed_users(args.password)
