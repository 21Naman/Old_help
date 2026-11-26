# Red-team log — SURAKSHA_BIBLE v1 → v2

Blueprint prompts P4 (×3 rounds) and P5 (mock judge). Severity scale: **CRIT** (the project or demo fails), **HIGH** (a judge catches it, or users get hurt), **MED** (it weakens a claim), **LOW** (polish).

Some flaws were found by **reading the repo**, not only the bible. Those are marked 📂 with the file.

---

## Round 1 — hostile senior engineer

| # | Sev | Flaw | Fix in v2 |
|---|---|---|---|
| 1 | **CRIT** 📂 | A watch fall starts **two brains**. `RakshakViewModel.kt:312` posts `fall` to `ally` *and* opens the legacy `backend/` `/ws` emergency voice link. That means two conversations and two escalation systems, and the bible assumed one. | Ticket #1: the fall path goes to `ally` only. Delete the `EmergencyClient` fall path; the watch voice uses `ally` TTS/STT. |
| 2 | **CRIT** 📂 | `FallDetector.kt` has a "hard impact after stillness" path tuned so "a deliberate drop from ~20–40 cm fires". **The detector itself generates the Charger Trap.** (The constants are named `_G` but are in m/s².) | Split into two signals. The `fall` signal requires free-fall followed by impact with the watch on-wrist. A `drop` signal (impact after stillness, or off-wrist) goes to L2 verify and becomes GREY. The demo uses the real body-fall path. |
| 3 | **CRIT** | **The trap utterance is too short for the voice voter.** "Theek hoon" is 2 words, and `vocal_gate` needs ≥ 2 s of audio and is meaningless at 2 words. V4 would silently abstain on the exact hero case. | 🆕 **Do-Check:** after "theek hoon", Suraksha *asks her to do something*: *"Achha, ek baar uth ke darwaze tak chal ke dikhaiye"* ("Okay, stand up once and walk to the door for me"). Body sensors then verify an **action**, not a feeling. V4 only votes on replies of ≥ 4 words; otherwise it abstains. |
| 4 | **HIGH** | **The heart-rate voter is confounded.** Getting up raises HR, so a real get-up votes "not up". Beta-blockers flatten HR, so "within baseline" gives false comfort. | HR is no longer a "she's up" voter. It becomes a **concern-only flag**: sustained > 130 or < 45 bpm, or PPG contact lost after the fall. A flag can only raise the tier. Same for SpO₂ < 90%. |
| 5 | **HIGH** | **The barometer threshold was absolute** (0.05 hPa) and confounded by her raising an arm while lying down, or sitting up on the floor. The physics: about 0.11–0.12 hPa per metre, so 0.05 hPa ≈ 0.4 m. That's sitting-up height, not standing. | Self-calibrating V3: **"pressure returned to within 0.03 hPa of the pre-fall standing reference, held 15 s, with low arm-motion variance"**. Her own pre-fall wrist height is the reference. Noise is measured on the real watch before tuning (UNVERIFIED until measured). |
| 6 | **HIGH** | **Step counter latency.** `TYPE_STEP_COUNTER` batches and can lag by tens of seconds, and slow elderly gait may undercount. | V2 movement uses `TYPE_STEP_DETECTOR` events, plus our own accelerometer cadence check (≥ 6 strides at 0.5–2 Hz). If the sensor is missing, the voter **abstains**. |
| 7 | **HIGH** | **What does an abstain count as?** v1 didn't say. If an abstain counted as neutral, a missing sensor would make HARA easier. | Rule: **an abstain counts as "not up".** Losing a sensor can only make Suraksha more careful. This is now part of the Floor Invariant. |
| 8 | **HIGH** | **A 3-minute vote window vs. a 3-minute demo.** The demo can't wait 180 s per fall. | Windows are config values: `GETUP_WINDOW_S` = 180 real, 40 for the stage. **Said on camera:** "In real life she gets 3 minutes; on stage we shortened it, it's one config value." |
| 9 | MED | **"No False Comfort" scanned free LLM text in two languages.** That's brittle. | Simpler and stronger: in fall mode, **status sentences are templates filled from the escalation record**. The LLM only writes the comfort sentence, and that sentence is scanned for status claims and dropped if it makes one. |
| 10 | MED 📂 | **No foreground service** in `AndroidManifest.xml`. The sensors only run while the app is open (the `FallDetector` comment even says so). That breaks "plug n play". | 🆕 Ticket: a health foreground service with a persistent notification. If it's not done in time, it's said under "what this is NOT". |
| 11 | MED | **The Floor Invariant test is trivially true** if it tests the vote in isolation. | Run it **through the real orchestrator** with moto DynamoDB and a fake clock. Inject LLM errors, duplicate watch posts, duplicate push replies, out-of-order events and abstaining sensors. |

## Round 2 — hostile judge and demo risk

| # | Sev | Flaw | Fix in v2 |
|---|---|---|---|
| 12 | **CRIT** | **Blueprint kill rule: "the demo depends on venue internet."** Every beat needs AWS (Bedrock, Step Functions, push). | (a) Bring a personal hotspot; no venue Wi-Fi. (b) Promote the **on-watch vote + cached Hindi audio** from STRETCH to SUPPORTING, so the tier appears on the watch even with no network. (c) A full backup video. **We don't claim "offline".** |
| 13 | **CRIT** | **Fall reliability on stage.** A body falling onto a soft mattress may not reach the impact threshold, and the detector was tuned on desk drops (#2). | Use a firm gym mat. **Rehearsal metric: the fall must fire 10/10 on the mat** before demo day, logged in `eval/`. Fallback: a **REPLAY** button injects a recorded real trace, clearly labelled "REPLAY" on the board. |
| 14 | **HIGH** | **Judge-as-Priya over Web Push will fail.** iOS needs a home-screen PWA install, plus a permission prompt and a Cognito login, on a stranger's phone in 10 seconds. | The QR opens a **no-login guest family page** (`/join/<demo-session>`) with a live socket and on-page sound and vibration. No Web Push is needed. Test it on iPhone Safari *and* Android Chrome. |
| 15 | **HIGH** | **Strawman baseline.** "Cancel-on-response = 0% catch" is true by construction (Blueprint 6.4 warns against this). | Three honest baselines: **B0** cancel-on-response (what products are reported to do; UNVERIFIED); **B1** our own Nova judge reading her words *with a prompt told to be sceptical*; **B2** steps-only. B1 is the one that matters. |
| 16 | MED | **The learning beat overclaims.** One "I'm far" decline is a rule, not learning. | Renamed **Nearest-First ordering** (same city first, then past acceptances). It's **adapting**, and we say it's deterministic. Demoted to a one-line supporting beat. |
| 17 | MED | **The demo had six beats and no "it stays quiet" proof.** Judges never saw that it *doesn't* nag. | New beat: a real get-up → Do-Check passes → **HARA, nobody is messaged.** "When she's actually fine, nobody gets bothered." |
| 18 | MED | **The chaos beat cost 25 s** with a separate run. | Flip "AI off" *before* the LAAL beat and reveal it afterwards: *"I switched the AI off before that one."* That saves 20 s and is a stronger reveal. |
| 19 | LOW | **"Isn't this just a confirmation step?"** wasn't in the challenge table. | Answer: "A confirmation step asks *her*. Ours asks her body to show it." |

## Round 3 — ethics and product reality

| # | Sev | Flaw | Fix in v2 |
|---|---|---|---|
| 20 | **HIGH** | **A consent conflict.** If she has the rule "Priya ko tabiyat mat batana" (don't tell Priya about my health), does PEELA's message to Priya break it? | PEELA is Topic `safety` (not forbiddable; she's told on the consent screen), **but its text carries no health detail**: *"Please give Amma a call when you can."* LAAL may say "may have fallen". Cedar still logs both. |
| 21 | **HIGH** | **"You override her when she says she's fine."** A dignity objection. | She's never overridden in front of her. Suraksha says *"aapki baat maan li"* ("I believe you") and tells her **exactly** what it's doing. PEELA only asks for a *call*. **Cost asymmetry table** added: a false PEELA costs one phone call; a missed fall costs a long lie. |
| 22 | **HIGH** | **The bathroom problem.** "The most dangerous room is where she takes the watch off." | The Galaxy Watch is water-resistant (5 ATM, UNVERIFIED for the model), and onboarding asks her to wear it in the shower. Off-wrist at an unusual hour for longer than her usual bath time produces a gentle ask *to her* first (on the watch when it's back on, or the phone). Named as a limitation. |
| 23 | MED | **Cognitive impairment.** Do-Check assumes she understands the request. | "What this is NOT": not designed for dementia. A no-response to Do-Check is treated like silence (→ LAAL after the window), so it fails safe. |
| 24 | MED | **Mic privacy.** Is it always listening? | The mic opens **only** after a fall, a tap or a scheduled check-in. Said explicitly. |
| 25 | MED | **Polly on a watch speaker in a bathroom**, with an elderly listener who may be hard of hearing. | Max volume plus a haptic pattern before each prompt, and short sentences. Tested in an actual bathroom with the door shut. |
| 26 | MED | **20 tickets is too many.** The spine is buried. | CORE is reduced to 9 tickets. The rest are SUPPORTING or STRETCH, plus a cut list. |

---

## Mock judge (P5) — on v1, generic rubric

| Criterion | v1 score | Reason |
|---|---|---|
| Impact / real-world use | 9.0 | Universal stakes; "theek hoon" lands with every Indian judge |
| Novelty | 8.5 | A named trap + category shift; not "an AI chatbot for elders" |
| Technical depth | 8.0 | Strong on paper; the HR/voice voters were weak (#3, #4) |
| **Working product / reliability** | **6.5** | Two brains (#1), desk-drop detector (#2), venue internet (#12), stage fall (#13) |
| Demo / presentation | 8.0 | A great structure, but judge-as-Priya was fragile (#14) |
| Honesty / proof | 7.5 | Strawman baseline (#15) |

**Weakest = working product.** v2 aims most fixes there: #1, #2, #10, #12, #13 and #14.

**Questions the mock judge would ask:** "Show me the fall firing 10 times in a row." "What's your baseline if not 0%?" "What happens if I'm the daughter and I ignore it?" (Answer: a Connect call after 45 s, then the next contact.)

**Estimated v2 after fixes:** reliability 6.5 → ~8, honesty 7.5 → ~8.5. This is an estimate, not a number for the pitch.

---

## Flaws still open (for v3)

- The real noise floor of the barometer on *our* watch is unmeasured (#5).
- Off-body sensor availability on Watch 4 (`TYPE_LOW_LATENCY_OFFBODY_DETECT`) is unverified. The fallback is PPG contact.
- The killer facts in bible §1 are all unsourced.
- The rubric is unknown, so the mapping is generic.

---

# Round 4 — on v2 (clinical safety, daily life, feasibility, owner's goal)

## 4A — Clinical safety

| # | Sev | Flaw | Fix in v3 |
|---|---|---|---|
| 27 | **CRIT** | **The Do-Check tells a possibly injured 72-year-old to stand up and walk.** After a fall with a possible hip fracture, standing can make the injury worse. A judge with any medical background ends the pitch here. | Reword it as a **permission to stay down**: *"Agar dard nahi hai, toh aaram se uthiye aur darwaze tak chaliye. Agar dard hai, toh bilkul mat uthiye, wahin rahiye, main madad bula rahi hoon."* ("If there's no pain, get up slowly and walk to the door. If it hurts, don't get up at all. Stay there, I'm calling for help.") Staying down is **never penalised for her**; it just routes to the right tier. Side effect: offering a dignified "it's okay to say it hurts" also beats the trap psychologically. |
| 28 | MED | **Mobility aids.** With a walker or wheelchair, the steps and standing-height voters are meaningless. | A profile field `mobility: independent / walker / wheelchair`. Walker: the stride band is lowered. Wheelchair: V2 uses seated height as `p_ref`, V3 abstains, and the Do-Check becomes "move back to your chair". Named as a limitation if not built. |

## 4B — Loops that never close

| # | Sev | Flaw | Fix in v3 |
|---|---|---|---|
| 29 | **HIGH** | **PEELA dead end.** Priya is asked to call Amma, but Amma is on the floor and her phone is in the bedroom. The call goes unanswered, and then nothing happens. | PEELA has an **open loop with a timer**. Priya's page has two buttons: "Spoke to her ✓" or "No answer". "No answer" or no tap within 10 min (stage: 30 s) **auto-upgrades to LAAL**. |
| 30 | **HIGH** 📂 | **The neighbour is asked last.** `escalation/steps.py:158` asks Amma about Sunita only *after both children fail*. In a fall, the person 30 s away is the best responder, yet she's contacted 3+ minutes in. That contradicts our own "the one who can arrive" pitch. | 🆕 **Fall pre-consent:** at onboarding Amma says *"gir jaaun toh Sunita ko pehle bulana"* ("if I fall, call Sunita first"). That becomes a Cedar `permit` from a fixed template with `context.reason == "fall"`. For a LAAL fall, the **neighbour and the nearest child are asked in parallel**; the first to accept is "the one coming". Without pre-consent, the old order stays. |
| 31 | MED | **The stay loop never ends** if the responder tapped "On my way" but never arrives. | If there's no "Arrived" by ETA + 15 min, ask the responder "Still coming?" and re-open the chain to the next contact. The watch keeps talking throughout. |

## 4C — Daily life (the "would she keep wearing it" test)

| # | Sev | Flaw | Fix in v3 |
|---|---|---|---|
| 32 | **HIGH** | **Night falls go unmonitored.** The Galaxy Watch 4 battery lasts about 1–1.5 days (UNVERIFIED), and the obvious habit is charging overnight. But night-time bathroom trips are reported as a peak fall time for older adults (UNVERIFIED; source it). The obvious charging habit hits the riskiest hours. | Onboarding sets a **charge window during the morning bath or breakfast** (learned from her routine), not at night. A GREY during the night means a gentle nudge to wear it. **Battery drain per hour is measured** with our sensor load and becomes a proof number. The barometer runs at 1 Hz idle and 5 Hz only after a fall. |
| 33 | **HIGH** | **No false-trigger data from real life.** If the detector fires once a day while she sits down hard, she gets a Do-Check every day and takes the watch off. The eval only has staged traces. | 🆕 **Wear test:** two teammates wear the watch through normal days (≥ 16 h each). Count `fall` triggers per wear-day. That's the honest "nag budget" number, and a strong Q&A answer. |
| 34 | MED | **The daily value disappeared from v2's story.** "Would someone keep using it" is part of the biggest criterion. The morning check-in, voice reminders and the wake-window check ✅ already exist and were dropped from the pitch. | Add one line in the pitch and one card on the board: *"Every other day it's a quiet companion: morning check-in, medicine reminders by voice. That's why she wears it on the day she falls."* |
| 35 | MED | **Language.** She's in Bengaluru, and a Kannada-speaking judge will ask. Polly and Transcribe support for Kannada is UNVERIFIED and likely limited. | The language is a profile field. Hindi, Hinglish and English are live today; others are named as next. |

## 4D — Feasibility

| # | Sev | Flaw | Fix in v3 |
|---|---|---|---|
| 36 | **CRIT** | **The trace plan takes about 9 hours of falling.** v2 asked for 139 traces × (fall + 180 s window + reset ≈ 4 min). That's a lot of falls for a small team, with injury risk. | Cut to **60 traces (36 dev / 24 held-out)** with a **60 s** post-fall stream (the stage window is 40 s anyway), about 2 h in total. Use **controlled falls**: kneel first, then go down sideways onto the mat. The fixed counts are in v3 §9. |
| 37 | **HIGH** | **The live board transport is unspecified.** The `ally` API is HTTP on Lambda with no WebSocket, so "live" was hand-waved. | 📂 The web app already polls (`useSurakshaState.ts`: "Polling replacement for the old WebSocket hook"). The board and `/join` poll a new `GET /ally/live/<session>` every 1 s, a single DynamoDB item. A warm-up pinger runs 10 min before the demo to avoid cold starts. |
| 38 | MED | **No latency budget.** Fall → spoken question → her reply → Transcribe + Nova → Do-Check prompt could take 8+ s. That's dead air on stage. | 🆕 A latency table per hop (Blueprint 6.5), measured on the real stack: fall → question, reply → Do-Check prompt, LAAL → judge's phone. The **first question uses cached Polly audio** (0 s TTS). |
| 39 | LOW | **10,000 Hypothesis cases through moto and the async orchestrator is slow.** | Use 1,000 cases with a fixed seed in CI. The slide number is whatever N the run prints. |

## 4E — Credibility and the owner's goal

| # | Sev | Flaw | Fix in v3 |
|---|---|---|---|
| 40 | **HIGH** | **"You made Naive mode artificially bad."** A judge can claim the toggle is rigged. | Naive mode **is literally our own old code path**: the `orchestrator.py:111` behaviour, kept behind a flag. Line for stage: *"This isn't a strawman. It's our own code from last month. We had this bug."* That's honest, memorable and verifiable in git history. |
| 41 | **HIGH** | **Mismatch with the owner's stated goal.** The owner wants "real world plug n play that helps instantly", but v2 put onboarding in STRETCH. | Promote a **minimal onboarding** to SUPPORTING: the family scans a QR on the watch, enters Amma's name, language and 2–3 contacts, and records her fall pre-consent (#30). The target is **under 3 minutes from box to armed**, timed on stage as a proof number. |
| 42 | MED | **India's DPDP Act** (the data-protection law). A judge will ask about sensor streams in the cloud. | Consent at onboarding, a **TTL on raw sensor traces** (e.g. 7 days), her readable audit log, and no audio stored after transcription. The exact legal duties are UNVERIFIED, so don't claim "compliant". |
| 43 | LOW | **Several judges scan the QR**, so there are several Priyas racing to tap "On my way". | First tap wins. The others see *"Another Priya is already going 🙂"*. That's fun on stage. |

## Mock judge (P5) — v2 vs. v3

| Criterion | v1 | v2 (est.) | v3 (est.) | What moved it |
|---|---|---|---|---|
| Impact / real-world use | 9.0 | 9.0 | **9.5** | Neighbour-first (#30), night coverage (#32), daily value (#34) |
| Novelty | 8.5 | 9.0 | 9.0 | Do-Check |
| Technical depth | 8.0 | 8.5 | 8.5 | Latency table (#38) |
| Working product | 6.5 | 8.0 | **8.5** | Trace plan feasible (#36), board transport (#37), onboarding (#41) |
| Demo | 8.0 | 8.5 | 9.0 | Naive = our own old code (#40) |
| Honesty / proof | 7.5 | 8.5 | **9.0** | Wear test (#33), battery number (#32) |

**Biggest single save:** #27. Without it, one doctor on the panel sinks the project.

**New weakest point:** real-life false triggers. That's unknown until the wear test (#33) runs, so **run it first**, before the demo is choreographed.

## Still open for v4
- The barometer noise floor (#5).
- Off-body sensor availability.
- Sourced killer facts, including the night-fall fact.
- Watch battery with our sensor load.
- The wear-test trigger rate.
- The real rubric.

---

# Research corrections (tracks 1–8 → bible v4)

These aren't red-team flaws. They're claims the research **proved wrong or sharpened**. Each was fixed in v4.

| # | What v3 said | What the research showed | Source | v4 fix |
|---|---|---|---|---|
| R1 | "She lies" (theek hoon) is the trap | Devices offer **only two exits**, "I'm OK" or ambulance; people avoid the second *"for fear of being taken into hospital"* | Fleming & Brayne BMJ 2008; vendor docs; AgingCare | Trap redefined; PEELA = "the third option" |
| R2 | "80% reluctant to press" (UAlberta paraphrase) | 80% of alone, can't-get-up falls had an **unused** alarm; 97% of long lies | BMJ 2008 (primary) | Re-attributed |
| R3 | Barometer on Watch4 UNVERIFIED | **Confirmed** in Samsung's spec | Samsung Newsroom | L1 updated |
| R4 | Kannada support "likely limited" | Transcribe **streams** Kannada and 8 more Indian languages; Polly **speaks** only Hindi/English | AWS docs | Language claim corrected |
| R5 | "Night bathroom trips are the peak" | Nocturia is *a* risk; filmed falls peak at **7–10 am / 7–10 pm** | Vlaeyen 2013; nocturia studies | Night claim softened; 06:40 justified |
| R6 | "Code decides, AI only reads" as a differentiator | Already used by a 2026 first-place winner (Ally) and CarePilot | Devpost | Demoted to hygiene |
| R7 | Recovery check as broadly novel | Apple claims motion-based recovery (US12380789B2 cl. 12); SafeStep auto-cancels via camera | Google Patents; Devpost | Novelty narrowed to "checking her **answer**" |
| R8 | Barometer height detection as ours | 2005 patent (expired) already claims height + time on the floor | US8747336B2 | Cited as lineage |
| R9 | Package name `ally` harmless | Same name as a 2026 first-place elder-care winner | Devpost | Rename to `suraksha` |
| R10 | Apple = "cancel on response" | Apple also auto-calls only if **immobile**, which creates the Moving-Arm Trap | Apple support 108896; Vlaeyen 2013 | New trap + demo beat |
