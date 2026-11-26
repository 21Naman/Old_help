# Suraksha research plan

*Started 25 Nov 2026. Modelled on the PAKKA research method: one track at a time, one file per track, and a review by you after each.*

## The goal

We already have a bible (`../SURAKSHA_BIBLE_v3.md`). The research has three jobs:

1. **Confirm or kill the core claims.** Does the Theek Hoon Trap really exist in shipped products? Is the barometer idea physically workable? Are elderly people really known to under-report, or to not use alarms?
2. **Find mechanisms to borrow** from products, patents and papers.
3. **Find what nobody built.** That's the gap and the USP.

We only want numbers if they reveal a mechanism, a gap, or a line for the pitch.

## How we work

1. One track at a time, done fully.
2. Write its findings file.
3. **Stop and ask you whether it's good.**
4. Fix it, or move on when you say go.

## The tracks

| # | Track | What it settles | Status |
|---|---|---|---|
| 1 | **How fall detection actually behaves** (Samsung, Apple, Google Pixel Watch, medical alert pendants, Indian elder-care services): read official support docs, not marketing | Whether "I'm OK" cancels everything, i.e. whether the trap is real | **Done, approved** |
| 2 | **Research papers**: unused alarms, the long lie, barometer + accelerometer fall detection, recovery and get-up detection, real-world false alarm rates | The physics and the human behaviour behind the trap | **Done, approved** |
| 3 | **Patents**: fall verification, post-fall get-up detection, barometric height, escalation to caregivers | Mechanisms to borrow; what's protected | **Done, approved** |
| 4 | **User complaints**: reviews, Reddit and forums on false alarms, cancelled alerts, watches taken off | Real-world failure modes | **Done, approved** (Reddit blocked; redo that part when Firecrawl credits reset) |
| 5 | **Indian elder-care landscape**: startups and services (what they built and their core mechanism) | The competitor table; the India-specific gap | **Done, approved** (Anvayaa site to retry with Firecrawl) |
| 6 | **Hackathon projects** on fall detection and elder care (Devpost, GitHub) | What everyone builds, so we avoid it | **Done, approved** |
| 7 | **Hardware and stack feasibility**: Galaxy Watch 4 sensors (barometer, off-body), the Samsung Health Sensor SDK, battery life, Polly and Transcribe language support | Whether the build plan is possible | **Done, approved** |
| 8 | **Synthesis**: what's crowded, what's empty, proposed bible v4 changes | The verdict | **Done, approved → applied in `../SURAKSHA_BIBLE_v4.md`** |
| 9 | **Real conversations** (you do these): one elderly parent living alone, one adult child living away | Ground truth for "theek hoon" | Not started |

## What each track file must have

1. **Sources read:** links, with a one-line note on what each showed.
2. **The mechanism table:** who / what they built / the real core mechanism / evidence.
3. **What we can pick.**
4. **What nobody built.**
5. **What this changes for Suraksha:** proposed edits to the bible, which stay proposals until you agree.

## Depth rules

- Read primary sources: support docs, papers, patent claims. Not listicles.
- Ask "what's the actual mechanism?" of every source.
- Cross-check across source types.
- Mark anything we couldn't confirm.
