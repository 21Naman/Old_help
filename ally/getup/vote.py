"""The Get-Up Vote (bible v5 §6 L4). Pure logic, no I/O, so it can also be ported to the watch.

Her words are one vote. Three body voters decide whether to believe them:
  V2 height   - wrist pressure back within 0.03 hPa of her own pre-fall reading, held 15 s, arm still
  V3 movement - at least 6 step-detector events or 6 walking strides after the fall
  V4 voice    - a reply of 4+ words, at least 60% of her usual speaking rate, no pain words
A voter that has no data abstains, and an abstain counts as "not up".

Tiers:
  GREY - the watch was dropped, spun, off her wrist or charging: we can't tell, nobody is alerted
  LAAL - she says she's hurt or can't get up, she didn't answer, or a concern flag fired
  HARA - she says she's fine and at least 2 body voters agree: nobody is told
  PEELA - she says she's fine but her body doesn't confirm it: ask her nearest child to call
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from scoring.deviation import CONCERNING, CONCERNING_DEVANAGARI

Tier = Literal["HARA", "PEELA", "LAAL", "GREY"]
Vote = Literal["up", "down", "abstain"]

HEIGHT_TOLERANCE_HPA = 0.03
HEIGHT_HOLD_S = 15.0
ARM_STILL_MAX_VAR = 1.5  # accelerometer variance (m/s^2)^2 above which the arm is waving
MIN_STEPS = 6
MIN_STRIDES = 6
MIN_REPLY_WORDS = 4
MIN_RATE_FRACTION = 0.6
SPIN_DROP_DEG = 360.0
HR_HIGH, HR_LOW, HR_SUSTAIN_S = 130, 45, 20.0
SPO2_LOW = 90


@dataclass
class PressureSample:
    t: float  # seconds since the fall
    hpa: float
    arm_var: float = 0.0


@dataclass
class HeartSample:
    t: float
    bpm: int


@dataclass
class FallEvidence:
    # What she said (from the companion's structured reply). None means no answer yet.
    says_ok: bool | None = None
    reports_unwell: bool = False
    reply_text: str = ""
    reply_seconds: float | None = None
    usual_wpm: float = 110.0
    silent_seconds: float = 0.0
    silence_limit_s: float = 90.0
    # Is the reading trustworthy at all?
    dropped: bool = False
    spin_deg: float = 0.0
    on_wrist: bool | None = True
    charging: bool = False
    # Body signals after the Do-Check prompt.
    p_ref_hpa: float | None = None
    pressure: list[PressureSample] = field(default_factory=list)
    step_events: int | None = None
    strides: int | None = None
    heart: list[HeartSample] = field(default_factory=list)
    spo2: int | None = None
    ppg_lost: bool = False


@dataclass
class VoteResult:
    tier: Tier
    votes: dict[str, Vote]
    flags: list[str]
    reasons: list[str]


def has_pain_words(text: str) -> bool:
    return bool(text and (CONCERNING.search(text) or CONCERNING_DEVANAGARI.search(text)))


def vote_height(ev: FallEvidence) -> Vote:
    if ev.p_ref_hpa is None or not ev.pressure:
        return "abstain"
    run_start: float | None = None
    for s in sorted(ev.pressure, key=lambda x: x.t):
        ok = abs(s.hpa - ev.p_ref_hpa) <= HEIGHT_TOLERANCE_HPA and s.arm_var <= ARM_STILL_MAX_VAR
        if not ok:
            run_start = None
            continue
        if run_start is None:
            run_start = s.t
        if s.t - run_start >= HEIGHT_HOLD_S:
            return "up"
    return "down"


def vote_movement(ev: FallEvidence) -> Vote:
    if ev.step_events is None and ev.strides is None:
        return "abstain"
    if (ev.step_events or 0) >= MIN_STEPS or (ev.strides or 0) >= MIN_STRIDES:
        return "up"
    return "down"


def vote_voice(ev: FallEvidence) -> Vote:
    words = len(ev.reply_text.split())
    if words < MIN_REPLY_WORDS or not ev.reply_seconds:
        return "abstain"
    if has_pain_words(ev.reply_text):
        return "down"
    wpm = words / (ev.reply_seconds / 60)
    return "up" if wpm >= MIN_RATE_FRACTION * ev.usual_wpm else "down"


def _sustained(samples: list[HeartSample], bad) -> bool:
    start: float | None = None
    for s in sorted(samples, key=lambda x: x.t):
        if bad(s.bpm):
            start = s.t if start is None else start
            if s.t - start >= HR_SUSTAIN_S:
                return True
        else:
            start = None
    return False


def concern_flags(ev: FallEvidence) -> list[str]:
    flags = []
    if _sustained(ev.heart, lambda b: b > HR_HIGH):
        flags.append("hr_high")
    if _sustained(ev.heart, lambda b: b < HR_LOW):
        flags.append("hr_low")
    if ev.spo2 is not None and ev.spo2 < SPO2_LOW:
        flags.append("spo2_low")
    if ev.ppg_lost:
        flags.append("ppg_lost_after_fall")
    if has_pain_words(ev.reply_text):
        flags.append("pain_words")
    return flags


def decide(ev: FallEvidence) -> VoteResult:
    if ev.dropped or ev.spin_deg >= SPIN_DROP_DEG or ev.on_wrist is False or ev.charging:
        return VoteResult("GREY", {}, [], ["watch not on her or dropped; can't tell"])

    votes: dict[str, Vote] = {
        "words": "abstain" if ev.says_ok is None else ("up" if ev.says_ok and not ev.reports_unwell else "down"),
        "height": vote_height(ev),
        "movement": vote_movement(ev),
        "voice": vote_voice(ev),
    }
    flags = concern_flags(ev)

    if ev.says_ok is None:
        if ev.silent_seconds >= ev.silence_limit_s:
            return VoteResult("LAAL", votes, flags, ["no answer after the fall"])
        # Still waiting for her: treat as not resolved; the caller re-runs when she answers.
        return VoteResult("PEELA" if not flags else "LAAL", votes, flags, ["waiting for her answer"])
    if votes["words"] == "down":
        return VoteResult("LAAL", votes, flags, ["she says she's hurt or can't get up"])
    if flags:
        return VoteResult("LAAL", votes, flags, [f"concern flag: {', '.join(flags)}"])

    body_up = sum(1 for k in ("height", "movement", "voice") if votes[k] == "up")
    if body_up >= 2:
        return VoteResult("HARA", votes, flags, [f"words and {body_up} body signals agree"])
    return VoteResult("PEELA", votes, flags, [f"she says she's fine, but only {body_up} body signal agrees"])
