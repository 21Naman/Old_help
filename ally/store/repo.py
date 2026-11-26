"""Single-table repository on SQL (Postgres in production, SQLite locally and in tests).

The layout mirrors the original DynamoDB design: one row per fact, keyed by (pk, sk), with one
secondary index (gsi1pk, gsi1sk) for the cross-parent "due" queries. Item bodies are JSON.

Errors propagate. The only swallowed failures are conditional writes, and only where they mean
"already exists" or "already claimed".
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta
from typing import Any, Callable, Iterable

from sqlalchemy import Column, Index, MetaData, String, Table, Text, create_engine, delete, insert, select, update
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

from config import DATABASE_URL, MESSAGE_EXPIRY_MIN
from core import clock
from core.ids import new_id

TURN_TTL_DAYS = 30

GSI_PENDING = "PENDING"
GSI_DUE_REMINDER = "DUE_REMINDER"
GSI_DUE_INVESTIGATION = "DUE_INVESTIGATION"
GSI_DUE_ESCALATION = "DUE_ESCALATION"

_KEYS = ("pk", "sk", "gsi1pk", "gsi1sk")

# Byte-order comparison on Postgres, so sort keys order exactly as they did in DynamoDB.
_Key = String(255).with_variant(String(255, collation="C"), "postgresql")

metadata = MetaData()
items = Table(
    "items",
    metadata,
    Column("pk", _Key, primary_key=True),
    Column("sk", _Key, primary_key=True),
    Column("gsi1pk", _Key, nullable=True),
    Column("gsi1sk", _Key, nullable=True),
    Column("data", Text, nullable=False),
    Index("ix_items_gsi1", "gsi1pk", "gsi1sk"),
)


class ConditionFailed(Exception):
    """A conditional write found the row in the wrong state."""


Condition = Callable[[dict[str, Any] | None], bool]


def _clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items() if v is not None}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value if v is not None]
    return value


def _pk(parent_id: str) -> str:
    return f"PARENT#{parent_id}"


def _engine_for(url: str) -> Engine:
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    if url.startswith("sqlite"):
        kwargs: dict[str, Any] = {"connect_args": {"check_same_thread": False}}
        if ":memory:" in url or url in ("sqlite://", "sqlite+pysqlite://"):
            kwargs["poolclass"] = StaticPool
        return create_engine(url, **kwargs)
    return create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5)


class Repo:
    def __init__(self, url: str | None = None, *, engine: Engine | None = None) -> None:
        self.engine = engine or _engine_for(url or DATABASE_URL)
        self._postgres = self.engine.dialect.name == "postgresql"
        # Serialises read-modify-write within this process; Postgres row locks cover other processes.
        self._lock = threading.RLock()
        metadata.create_all(self.engine)

    # ---- generic helpers -------------------------------------------------------------------

    def _load(self, conn: Connection, pk: str, sk: str, *, lock: bool = False) -> tuple[dict[str, Any], str | None, str | None] | None:
        stmt = select(items.c.data, items.c.gsi1pk, items.c.gsi1sk).where(items.c.pk == pk, items.c.sk == sk)
        if lock and self._postgres:
            stmt = stmt.with_for_update()
        row = conn.execute(stmt).first()
        if row is None:
            return None
        return json.loads(row.data), row.gsi1pk, row.gsi1sk

    def _store(self, conn: Connection, pk: str, sk: str, data: dict[str, Any], gsi: tuple[str | None, str | None], *, exists: bool) -> None:
        values = {"data": json.dumps(_clean(data), separators=(",", ":")), "gsi1pk": gsi[0], "gsi1sk": gsi[1]}
        if exists:
            conn.execute(update(items).where(items.c.pk == pk, items.c.sk == sk).values(**values))
        else:
            conn.execute(insert(items).values(pk=pk, sk=sk, **values))

    def _put(self, parent_id: str, sk: str, data: dict[str, Any], *, if_absent: bool = False, **extra: Any) -> bool:
        pk = _pk(parent_id)
        gsi = (extra.pop("gsi1pk", None), extra.pop("gsi1sk", None))
        body = {**data, **extra}
        with self._lock:
            try:
                with self.engine.begin() as conn:
                    exists = self._load(conn, pk, sk, lock=True) is not None
                    if exists and if_absent:
                        return False
                    self._store(conn, pk, sk, body, gsi, exists=exists)
                return True
            except IntegrityError:
                # Another process inserted the same key between our read and write.
                if if_absent:
                    return False
                raise

    def _get(self, parent_id: str, sk: str, *, consistent: bool = False) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            found = self._load(conn, _pk(parent_id), sk)
        return found[0] if found else None

    def _query_prefix(
        self, parent_id: str, prefix: str, *, limit: int | None = None, newest_first: bool = False
    ) -> list[dict[str, Any]]:
        order = items.c.sk.desc() if newest_first else items.c.sk.asc()
        stmt = select(items.c.data).where(items.c.pk == _pk(parent_id), items.c.sk.startswith(prefix, autoescape=True))
        stmt = stmt.order_by(order)
        if limit:
            stmt = stmt.limit(limit)
        with self.engine.connect() as conn:
            return [json.loads(r.data) for r in conn.execute(stmt)]

    def _query_between(self, parent_id: str, lo: str, hi: str) -> list[dict[str, Any]]:
        stmt = (
            select(items.c.data)
            .where(items.c.pk == _pk(parent_id), items.c.sk >= lo, items.c.sk <= hi)
            .order_by(items.c.sk.asc())
        )
        with self.engine.connect() as conn:
            return [json.loads(r.data) for r in conn.execute(stmt)]

    def _query_gsi(self, gsi1pk: str, *, until: str | None = None) -> list[tuple[str, dict[str, Any]]]:
        stmt = select(items.c.pk, items.c.sk, items.c.data).where(items.c.gsi1pk == gsi1pk)
        if until is not None:
            stmt = stmt.where(items.c.gsi1sk <= until)
        stmt = stmt.order_by(items.c.gsi1sk.asc())
        with self.engine.connect() as conn:
            return [(r.sk, json.loads(r.data)) for r in conn.execute(stmt)]

    def _update(
        self,
        parent_id: str,
        sk: str,
        set_fields: dict[str, Any] | None = None,
        *,
        remove: Iterable[str] = (),
        condition: Condition | None = None,
        return_new: bool = False,
        return_old: bool = False,
        mutate: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any] | None:
        """Upsert like DynamoDB UpdateItem. `condition` sees the current item (None if absent)."""
        pk = _pk(parent_id)
        with self._lock, self.engine.begin() as conn:
            found = self._load(conn, pk, sk, lock=True)
            old = found[0] if found else None
            if condition is not None and not condition(old):
                raise ConditionFailed(sk)
            gsi = [found[1], found[2]] if found else [None, None]
            new = dict(old or {})
            removals = list(remove)
            for key, value in (set_fields or {}).items():
                if value is None:
                    removals.append(key)
                elif key == "gsi1pk":
                    gsi[0] = value
                elif key == "gsi1sk":
                    gsi[1] = value
                else:
                    new[key] = value
            for key in removals:
                if key == "gsi1pk":
                    gsi[0] = None
                elif key == "gsi1sk":
                    gsi[1] = None
                else:
                    new.pop(key, None)
            if mutate is not None:
                mutate(new)
            self._store(conn, pk, sk, new, (gsi[0], gsi[1]), exists=found is not None)
        if return_new:
            return _clean(new)
        if return_old:
            return old
        return None

    def _delete(self, parent_id: str, sk: str, *, condition: Condition | None = None) -> bool:
        pk = _pk(parent_id)
        with self._lock, self.engine.begin() as conn:
            if condition is not None:
                found = self._load(conn, pk, sk, lock=True)
                if not condition(found[0] if found else None):
                    return False
            conn.execute(delete(items).where(items.c.pk == pk, items.c.sk == sk))
        return True

    # ---- maintenance ----------------------------------------------------------------------

    def purge_expired(self) -> int:
        """Delete rows whose `ttl` has passed (what DynamoDB TTL did in the background)."""
        now_epoch = clock.epoch(clock.now())
        doomed: list[tuple[str, str]] = []
        with self.engine.connect() as conn:
            for r in conn.execute(select(items.c.pk, items.c.sk, items.c.data).where(items.c.data.contains('"ttl":'))):
                ttl = json.loads(r.data).get("ttl")
                if isinstance(ttl, (int, float)) and ttl <= now_epoch:
                    doomed.append((r.pk, r.sk))
        if doomed:
            with self._lock, self.engine.begin() as conn:
                for pk, sk in doomed:
                    conn.execute(delete(items).where(items.c.pk == pk, items.c.sk == sk))
        return len(doomed)

    def list_keys(self, parent_id: str) -> list[str]:
        with self.engine.connect() as conn:
            return [r.sk for r in conn.execute(select(items.c.sk).where(items.c.pk == _pk(parent_id)))]

    def delete_keys(self, parent_id: str, sks: Iterable[str]) -> None:
        with self._lock, self.engine.begin() as conn:
            for sk in sks:
                conn.execute(delete(items).where(items.c.pk == _pk(parent_id), items.c.sk == sk))

    # ---- profile & roster -----------------------------------------------------------------

    def get_profile(self, parent_id: str) -> dict[str, Any] | None:
        return self._get(parent_id, "PROFILE")

    def put_profile(self, parent_id: str, profile: dict[str, Any]) -> None:
        self._put(parent_id, "PROFILE", {**profile, "parent_id": parent_id})

    def list_members(self, parent_id: str) -> list[dict[str, Any]]:
        members = self._query_prefix(parent_id, "MEMBER#")
        return sorted(members, key=lambda m: m.get("order", 99))

    def get_member(self, parent_id: str, member_id: str) -> dict[str, Any] | None:
        return self._get(parent_id, f"MEMBER#{member_id}")

    def put_member(self, parent_id: str, member: dict[str, Any]) -> None:
        self._put(parent_id, f"MEMBER#{member['id']}", member)

    # ---- users (local login) --------------------------------------------------------------

    def put_user(self, user: dict[str, Any]) -> None:
        self._put("_users", f"USER#{user['username'].lower()}", user)

    def get_user(self, username: str) -> dict[str, Any] | None:
        return self._get("_users", f"USER#{username.lower()}")

    # ---- day summaries --------------------------------------------------------------------

    def get_day(self, parent_id: str, day: str) -> dict[str, Any]:
        return self._get(parent_id, f"DAY#{day}") or {"date": day}

    def update_day(self, parent_id: str, day: str, **fields: Any) -> dict[str, Any]:
        return self._update(parent_id, f"DAY#{day}", {"date": day, **fields}, return_new=True) or {}

    def set_day_if_absent(self, parent_id: str, day: str, field: str, value: Any) -> bool:
        """Atomically set a field only once per day (e.g. first wake)."""
        try:
            self._update(
                parent_id,
                f"DAY#{day}",
                {"date": day, field: value},
                condition=lambda cur: cur is None or field not in cur,
            )
            return True
        except ConditionFailed:
            return False

    def increment_day(self, parent_id: str, day: str, field: str, *, limit: int | None = None) -> int:
        result: dict[str, int] = {}

        def bump(item: dict[str, Any]) -> None:
            item[field] = int(item.get(field, 0)) + 1
            result["value"] = item[field]

        try:
            self._update(
                parent_id,
                f"DAY#{day}",
                {"date": day},
                condition=None if limit is None else (lambda cur: int((cur or {}).get(field, 0)) < limit),
                mutate=bump,
            )
        except ConditionFailed:
            return -1
        return result["value"]

    def list_days(self, parent_id: str, first: str, last: str) -> list[dict[str, Any]]:
        return self._query_between(parent_id, f"DAY#{first}", f"DAY#{last}")

    # ---- turns & signals ------------------------------------------------------------------

    def add_turn(self, parent_id: str, speaker: str, text: str, **extra: Any) -> dict[str, Any]:
        at = clock.now()
        turn = {
            "id": new_id(),
            "speaker": speaker,
            "text": text,
            "at": clock.iso(at),
            "ttl": clock.epoch(at + timedelta(days=TURN_TTL_DAYS)),
            **extra,
        }
        self._put(parent_id, f"TURN#{turn['at']}#{turn['id']}", turn)
        return turn

    def recent_turns(self, parent_id: str, limit: int = 12) -> list[dict[str, Any]]:
        now_epoch = clock.epoch(clock.now())
        rows = self._query_prefix(parent_id, "TURN#", limit=limit, newest_first=True)
        return list(reversed([r for r in rows if int(r.get("ttl", now_epoch + 1)) > now_epoch]))

    def add_signal(self, parent_id: str, kind: str, **data: Any) -> dict[str, Any]:
        at = clock.now()
        signal = {
            "id": new_id(),
            "kind": kind,
            "at": clock.iso(at),
            "ttl": clock.epoch(at + timedelta(days=TURN_TTL_DAYS)),
            **data,
        }
        self._put(parent_id, f"SIGNAL#{signal['at']}#{signal['id']}", signal)
        return signal

    def signals_between(self, parent_id: str, start: datetime, end: datetime) -> list[dict[str, Any]]:
        return self._query_between(parent_id, f"SIGNAL#{clock.iso(start)}", f"SIGNAL#{clock.iso(end)}~")

    # ---- dedupe + proactive messages ------------------------------------------------------

    def claim_dedupe(self, parent_id: str, key: str, value: str = "1") -> bool:
        return self._put(parent_id, f"DEDUPE#{key}", {"value": value, "at": clock.iso(clock.now())}, if_absent=True)

    def create_message(
        self,
        parent_id: str,
        *,
        audience: str,
        kind: str,
        title: str,
        body: str,
        related_id: str,
        data: dict[str, Any] | None = None,
        expires_min: int = MESSAGE_EXPIRY_MIN,
    ) -> tuple[dict[str, Any], bool]:
        """Create a message exactly once per related_id. Returns (message, created)."""
        at = clock.now()
        msg = {
            "id": new_id(),
            "audience": audience,
            "kind": kind,
            "title": title,
            "body": body,
            "related_id": related_id,
            "data": data or {},
            "status": "pending",
            "created_at": clock.iso(at),
            "expires_at": clock.iso(at + timedelta(minutes=expires_min)),
            "ttl": clock.epoch(at + timedelta(days=TURN_TTL_DAYS)),
        }
        pk = _pk(parent_id)
        dedupe_sk = f"DEDUPE#msg#{related_id}"
        try:
            with self._lock, self.engine.begin() as conn:
                if self._load(conn, pk, dedupe_sk, lock=True) is None:
                    self._store(conn, pk, dedupe_sk, {"msg_id": msg["id"]}, (None, None), exists=False)
                    self._store(
                        conn,
                        pk,
                        f"MSG#{msg['id']}",
                        msg,
                        (f"{GSI_PENDING}#{parent_id}#{audience}", msg["created_at"]),
                        exists=False,
                    )
                    return msg, True
        except IntegrityError:
            pass
        existing = self._get(parent_id, dedupe_sk) or {}
        found = self._get(parent_id, f"MSG#{existing.get('msg_id')}")
        return found or msg, False

    def claim_pending_messages(self, parent_id: str, audience: str) -> list[dict[str, Any]]:
        now_iso = clock.iso(clock.now())
        claimed: list[dict[str, Any]] = []
        for sk, raw in self._query_gsi(f"{GSI_PENDING}#{parent_id}#{audience}"):
            try:
                item = self._update(
                    parent_id,
                    sk,
                    {"status": "delivered", "delivered_at": now_iso},
                    remove=["gsi1pk", "gsi1sk"],
                    condition=lambda cur: bool(cur) and cur.get("status") == "pending" and cur.get("expires_at", "") > now_iso,
                    return_new=True,
                )
            except ConditionFailed:
                if raw.get("expires_at", "") <= now_iso:
                    self._update(parent_id, sk, {"status": "expired"}, remove=["gsi1pk", "gsi1sk"])
                continue
            if item:
                claimed.append(item)
        return sorted(claimed, key=lambda m: m["created_at"])

    def expire_pending_messages(self, parent_id: str, related_prefix: str) -> int:
        """Retire questions that no longer need an answer (e.g. after an all-clear)."""
        retired = 0
        for row in self._query_prefix(parent_id, "MSG#", newest_first=True, limit=200):
            if row.get("status") != "pending" or not str(row.get("related_id", "")).startswith(related_prefix):
                continue
            try:
                self._update(
                    parent_id,
                    f"MSG#{row['id']}",
                    {"status": "superseded"},
                    remove=["gsi1pk", "gsi1sk"],
                    condition=lambda cur: bool(cur) and cur.get("status") == "pending",
                )
            except ConditionFailed:
                continue
            retired += 1
        return retired

    def get_message(self, parent_id: str, msg_id: str) -> dict[str, Any] | None:
        return self._get(parent_id, f"MSG#{msg_id}")

    def ack_message(self, parent_id: str, msg_id: str) -> None:
        self._update(parent_id, f"MSG#{msg_id}", {"status": "acknowledged", "acked_at": clock.iso(clock.now())})

    def messages_since(self, parent_id: str, since_iso: str, *, kind: str | None = None) -> list[dict[str, Any]]:
        rows = self._query_prefix(parent_id, "MSG#", newest_first=True, limit=200)
        return [r for r in rows if r.get("created_at", "") >= since_iso and (kind is None or r.get("kind") == kind)]

    # ---- reminders ------------------------------------------------------------------------

    def put_reminder(self, parent_id: str, reminder: dict[str, Any]) -> None:
        extra: dict[str, Any] = {}
        if reminder.get("status") == "active" and reminder.get("due_at"):
            extra = {"gsi1pk": GSI_DUE_REMINDER, "gsi1sk": f"{reminder['due_at']}#{parent_id}"}
        self._put(parent_id, f"REMINDER#{reminder['id']}", {**reminder, "parent_id": parent_id}, **extra)

    def list_reminders(self, parent_id: str, *, status: str | None = "active") -> list[dict[str, Any]]:
        rows = self._query_prefix(parent_id, "REMINDER#")
        return [r for r in rows if status is None or r.get("status") == status]

    def get_reminder(self, parent_id: str, reminder_id: str) -> dict[str, Any] | None:
        return self._get(parent_id, f"REMINDER#{reminder_id}")

    def due_reminders(self, until: datetime) -> list[dict[str, Any]]:
        return [row for _, row in self._query_gsi(GSI_DUE_REMINDER, until=f"{clock.iso(until)}#~")]

    # ---- consent rules & audit ------------------------------------------------------------

    def put_consent(self, parent_id: str, rule: dict[str, Any]) -> None:
        self._put(parent_id, f"CONSENT#{rule['id']}", rule)

    def get_consent(self, parent_id: str, rule_id: str) -> dict[str, Any] | None:
        return self._get(parent_id, f"CONSENT#{rule_id}")

    def list_consents(self, parent_id: str, *, statuses: tuple[str, ...] = ("active",)) -> list[dict[str, Any]]:
        return [r for r in self._query_prefix(parent_id, "CONSENT#") if r.get("status") in statuses]

    def update_consent(self, parent_id: str, rule_id: str, **fields: Any) -> None:
        self._update(parent_id, f"CONSENT#{rule_id}", fields)

    def put_audit(self, parent_id: str, row: dict[str, Any]) -> str:
        sk = f"AUDIT#{row['at']}#{row['id']}"
        self._put(parent_id, sk, row)
        return sk

    def update_audit(self, parent_id: str, sk: str, **fields: Any) -> None:
        self._update(parent_id, sk, fields)

    def list_audit(self, parent_id: str, limit: int = 100) -> list[dict[str, Any]]:
        return self._query_prefix(parent_id, "AUDIT#", limit=limit, newest_first=True)

    # ---- alerts & investigations ----------------------------------------------------------

    def put_alert(self, parent_id: str, alert: dict[str, Any]) -> None:
        self._put(parent_id, f"ALERT#{alert['created_at']}#{alert['id']}", alert)

    def update_alert(self, parent_id: str, alert: dict[str, Any], **fields: Any) -> dict[str, Any]:
        return self._update(
            parent_id, f"ALERT#{alert['created_at']}#{alert['id']}", fields, return_new=True
        ) or {}

    def list_alerts(self, parent_id: str, limit: int = 30) -> list[dict[str, Any]]:
        return self._query_prefix(parent_id, "ALERT#", limit=limit, newest_first=True)

    def get_alert(self, parent_id: str, alert_id: str) -> dict[str, Any] | None:
        for alert in self.list_alerts(parent_id, limit=100):
            if alert["id"] == alert_id:
                return alert
        return None

    def open_alert(self, parent_id: str) -> dict[str, Any] | None:
        for alert in self.list_alerts(parent_id, limit=10):
            if alert.get("status") in ("investigating", "escalating"):
                return alert
        return None

    def put_investigation(self, parent_id: str, inv: dict[str, Any]) -> None:
        extra: dict[str, Any] = {}
        if inv.get("status") == "open":
            extra = {"gsi1pk": GSI_DUE_INVESTIGATION, "gsi1sk": f"{inv['due_at']}#{parent_id}"}
        self._put(parent_id, f"INVESTIGATION#{inv['id']}", {**inv, "parent_id": parent_id}, **extra)

    def close_investigation(self, parent_id: str, inv_id: str, status: str) -> bool:
        """Close exactly once; returns False if it was already closed."""
        try:
            self._update(
                parent_id,
                f"INVESTIGATION#{inv_id}",
                {"status": status, "closed_at": clock.iso(clock.now())},
                remove=["gsi1pk", "gsi1sk"],
                condition=lambda cur: bool(cur) and cur.get("status") == "open",
            )
            return True
        except ConditionFailed:
            return False

    def open_investigation(self, parent_id: str) -> dict[str, Any] | None:
        rows = self._query_prefix(parent_id, "INVESTIGATION#", newest_first=True, limit=5)
        return next((r for r in rows if r.get("status") == "open"), None)

    def due_investigations(self, until: datetime) -> list[dict[str, Any]]:
        return [row for _, row in self._query_gsi(GSI_DUE_INVESTIGATION, until=f"{clock.iso(until)}#~")]

    # ---- escalations ----------------------------------------------------------------------

    def acquire_escalation_lock(self, parent_id: str, esc_id: str, stale_after_h: int = 6) -> bool:
        """One open escalation per parent. A lock older than `stale_after_h` (nobody marked arrival) is reclaimable."""
        now = clock.now()
        stale = clock.iso(now - timedelta(hours=stale_after_h))
        try:
            self._update(
                parent_id,
                "ESC_ACTIVE",
                {"esc_id": esc_id, "at": clock.iso(now)},
                condition=lambda cur: cur is None or cur.get("at", "") < stale,
            )
            return True
        except ConditionFailed:
            return False

    def active_escalation_id(self, parent_id: str) -> str | None:
        row = self._get(parent_id, "ESC_ACTIVE", consistent=True)
        return row.get("esc_id") if row else None

    def release_escalation_lock(self, parent_id: str, esc_id: str) -> None:
        self._delete(parent_id, "ESC_ACTIVE", condition=lambda cur: bool(cur) and cur.get("esc_id") == esc_id)

    def put_escalation(self, parent_id: str, esc: dict[str, Any]) -> None:
        extra: dict[str, Any] = {}
        if esc.get("due_at") and esc.get("status") not in ("resolved", "failed", "stopped"):
            extra = {"gsi1pk": GSI_DUE_ESCALATION, "gsi1sk": f"{esc['due_at']}#{parent_id}"}
        self._put(parent_id, f"ESC#{esc['id']}", {**esc, "parent_id": parent_id}, **extra)

    def get_escalation(self, parent_id: str, esc_id: str, *, consistent: bool = True) -> dict[str, Any] | None:
        return self._get(parent_id, f"ESC#{esc_id}", consistent=consistent)

    def update_escalation(self, parent_id: str, esc_id: str, **fields: Any) -> dict[str, Any]:
        return self._update(parent_id, f"ESC#{esc_id}", fields, return_new=True) or {}

    def set_escalation_due(self, parent_id: str, esc_id: str, due_at: str | None) -> None:
        """Schedule (or clear) the escalation's next timeout for the sweep."""
        if due_at:
            fields = {"due_at": due_at, "gsi1pk": GSI_DUE_ESCALATION, "gsi1sk": f"{due_at}#{parent_id}"}
            self._update(parent_id, f"ESC#{esc_id}", fields)
        else:
            self._update(parent_id, f"ESC#{esc_id}", remove=["due_at", "gsi1pk", "gsi1sk"])

    def due_escalations(self, until: datetime) -> list[dict[str, Any]]:
        return [row for _, row in self._query_gsi(GSI_DUE_ESCALATION, until=f"{clock.iso(until)}#~")]

    def consume_escalation_token(self, parent_id: str, esc_id: str, token_version: int) -> dict[str, Any] | None:
        """Single-use: bump the version only if it still matches and a reply is awaited.

        Returns the item as it was *before* consumption, or None if the token was already used or
        superseded.
        """
        try:
            return self._update(
                parent_id,
                f"ESC#{esc_id}",
                {"token_version": token_version + 1, "awaiting": None},
                remove=["due_at", "gsi1pk", "gsi1sk"],
                condition=lambda cur: bool(cur) and cur.get("token_version") == token_version and bool(cur.get("awaiting")),
                return_old=True,
            )
        except ConditionFailed:
            return None

    def append_escalation_event(self, parent_id: str, esc_id: str, event: dict[str, Any]) -> None:
        entry = _clean({"at": clock.iso(clock.now()), **event})
        self._update(
            parent_id,
            f"ESC#{esc_id}",
            mutate=lambda item: item.setdefault("timeline", []).append(entry),
        )

    def list_escalations(self, parent_id: str, limit: int = 10) -> list[dict[str, Any]]:
        rows = self._query_prefix(parent_id, "ESC#")
        return sorted(rows, key=lambda e: e.get("created_at", ""), reverse=True)[:limit]

    # ---- push subscriptions ---------------------------------------------------------------

    def put_push_subscription(self, parent_id: str, audience: str, endpoint_hash: str, sub: dict[str, Any]) -> None:
        self._put(
            parent_id,
            f"PUSH#{audience}#{endpoint_hash}",
            {"audience": audience, "subscription": sub, "hash": endpoint_hash},
        )

    def list_push_subscriptions(self, parent_id: str, audience: str) -> list[dict[str, Any]]:
        return self._query_prefix(parent_id, f"PUSH#{audience}#")

    def delete_push_subscription(self, parent_id: str, audience: str, endpoint_hash: str) -> None:
        self._delete(parent_id, f"PUSH#{audience}#{endpoint_hash}")


_repo: Repo | None = None


def get_repo() -> Repo:
    global _repo
    if _repo is None:
        _repo = Repo()
    return _repo


def set_repo(repo: Repo | None) -> None:
    """Tests only."""
    global _repo
    _repo = repo
