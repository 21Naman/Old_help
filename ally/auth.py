"""Identity. Ally issues its own HS256 login tokens (POST /ally/auth/login) and verifies them here.
With ALLY_DEV_TOOLS=1 a dev header identity is also accepted (local only).
"""

from __future__ import annotations

import hmac
import time
from dataclasses import dataclass
from typing import Any

import bcrypt
import jwt
from fastapi import Header

from config import DEV_TOOLS, JWT_SECRET, JWT_TTL_H, PARENT_ID
from core.errors import AllyError, Forbidden
from core.secrets import secret
from store.repo import get_repo

_ALG = "HS256"


class Unauthorized(AllyError):
    status = 401
    code = "unauthorized"


@dataclass(frozen=True)
class Identity:
    sub: str
    parent_id: str
    member_id: str  # "parent" for the parent's own device
    groups: frozenset[str]

    @property
    def is_parent(self) -> bool:
        return "parent" in self.groups

    @property
    def audience(self) -> str:
        return "parent" if self.is_parent else self.member_id


def _identity_from_claims(claims: dict[str, Any]) -> Identity:
    groups = frozenset(str(g) for g in claims.get("groups") or [])
    parent_id = str(claims.get("parent_id") or PARENT_ID)
    member_id = str(claims.get("member_id") or ("parent" if "parent" in groups else ""))
    if not member_id or not groups & {"parent", "family"}:
        raise Forbidden("This account is not linked to a family yet.")
    return Identity(str(claims.get("sub")), parent_id, member_id, groups)


def _signing_key() -> str:
    if not JWT_SECRET:
        raise Unauthorized("Sign-in is not configured.", detail="ALLY_JWT_SECRET missing")
    return JWT_SECRET


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def issue_token(user: dict[str, Any]) -> str:
    now = int(time.time())  # wall clock, not Ally's (testable) clock: PyJWT checks exp against real time
    claims = {
        "sub": user["username"],
        "groups": [user["group"]],
        "parent_id": user["parent_id"],
        "member_id": user["member_id"],
        "iat": now,
        "exp": now + JWT_TTL_H * 3600,
    }
    return jwt.encode(claims, _signing_key(), algorithm=_ALG)


def login(username: str, password: str) -> dict[str, Any]:
    user = get_repo().get_user(username.strip())
    # Compare against a dummy hash when the user is unknown, so timing doesn't reveal usernames.
    stored = (user or {}).get("password_hash") or "$2b$12$C6UzMDM.H6dfI/f/IKcEeO5u8kkD7G0Wf7u0n3u3mJr4l3cJm1o0e"
    if not bcrypt.checkpw(password.encode(), stored.encode()) or not user:
        raise Unauthorized("That username or password didn't match.")
    return {"token": issue_token(user), "member_id": user["member_id"], "group": user["group"]}


def _verify(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, _signing_key(), algorithms=[_ALG])
    except jwt.PyJWTError as exc:
        raise Unauthorized("Please sign in again.", detail=repr(exc)) from exc


def current_identity(
    authorization: str | None = Header(default=None),
    x_dev_member: str | None = Header(default=None),
) -> Identity:
    if DEV_TOOLS and x_dev_member:
        groups = frozenset({"parent"}) if x_dev_member == "parent" else frozenset({"family"})
        return Identity(f"dev-{x_dev_member}", PARENT_ID, x_dev_member, groups)
    if not authorization or not authorization.lower().startswith("bearer "):
        raise Unauthorized("Please sign in.")
    return _identity_from_claims(_verify(authorization.split(" ", 1)[1]))


def require_parent(identity: Identity) -> Identity:
    if not identity.is_parent:
        raise Forbidden("Only Amma's own device can do this.")
    return identity


def require_family(identity: Identity) -> Identity:
    if identity.is_parent or "family" not in identity.groups:
        raise Forbidden("This is for family members.")
    return identity


def verify_device_key(provided: str | None, source: str = "watch") -> None:
    """Each device may have its own key (ALLY_WATCH_DEVICE_KEY / ALLY_PHONE_DEVICE_KEY) so one can be
    revoked alone; both fall back to the shared ALLY_DEVICE_KEY."""
    expected = [k for k in (secret(f"{source.upper()}_DEVICE_KEY"), secret("DEVICE_KEY")) if k]
    if not expected:
        raise Unauthorized("Device key not configured.", detail="ALLY_DEVICE_KEY missing")
    if not provided or not any(hmac.compare_digest(provided, k) for k in expected):
        raise Unauthorized("Unknown device.")
