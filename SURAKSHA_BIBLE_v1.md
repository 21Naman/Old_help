# SURAKSHA — Bible v1

*The watch that doesn't take "theek hoon" for an answer.*

Written against `Hackathon-Blueprint-Bhavya-Pattern.md` (Part 12.3 skeleton). Built on the existing repo. Prior work is allowed at this event, so we **keep the spine and rebuild the story around one trap**.

**Status legend** used throughout: ✅ built in repo · 🔧 built, needs change · 🆕 invent and build · 🎤 pitch-only (said on stage, not built).

**Every outside fact below is tagged UNVERIFIED.** Check each one before it goes on a slide (Blueprint 6.11).

---

## 0. One-line pitch

Smartwatches ask an elderly parent "Are you OK?" after a fall and **believe the answer**. Suraksha treats her words as **one vote**, checks them against her body, then gets **one person who can actually show up** to commit, and stays with her until they arrive.

---

## 1. The person, the moment, the cost

- **Person:** Kamala Sharma ("Amma"), 72, widowed. She lives alone in Bengaluru. Her son Rahul is in Pune (840 km away). Her daughter Priya is in Bengaluru (40 minutes away). Sunita aunty is next door. *(This is the seeded family in `ally/seed/amma.json`.)*
- **Moment:** 06:40, in the bathroom. She slips and lands on the floor. Her hip hurts and she can't get up. Her watch asks "Are you OK?". She says **"haan, theek hoon"** ("yes, I'm fine"), because she doesn't want to worry Rahul before his office day. The watch cancels. She stays on the floor.
- **Cost:** the "long lie", meaning the time spent on the floor after a fall. Each hour there adds dehydration, pressure injury and pneumonia risk. It also turns a sprain into a hospital stay. *(UNVERIFIED: get a sourced number for long-lie outcomes, e.g. mortality or admission after more than 1 hour on the floor.)*

**Killer facts to collect** (Blueprint 4.5). All are UNVERIFIED, so find a source or cut each one:
1. The number of Indians aged 60+, and the share living alone or with only a spouse.
2. The share of elderly people who fall each year, and how many can't get up unaided.
3. Long-lie outcomes (above).
4. That commercial watch fall detection cancels the emergency call if the wearer responds. **Check this in the actual Samsung and Apple docs** before claiming it.
5. How often older parents under-report symptoms to their children. Find any survey; "theek hoon" is the cultural core of the pitch.

**30-second hook:** *"06:40. Amma's on the bathroom floor. Her watch asks if she's okay. She says 'theek hoon', because every Indian mother says 'theek hoon'. The watch believes her. Rahul finds out at 1 pm."*

---

## 2. The traps

### 2.1 The "Theek Hoon" Trap (the hero)

**The obvious approach:** detect a fall, ask "Are you OK?", and treat any "I'm OK" or button press as a cancel.

**Why it's confidently wrong:** the person most likely to under-report is exactly the person on the floor. Embarrassment, not wanting to bother the kids, and shock all produce "theek hoon".

**Our repo has this bug today.** In `ally/agents/orchestrator.py:111`, if `reply.parent_says_okay`, the system calls `on_im_okay()` and resolves both the investigation and the escalation. 🔧

**How we beat it:** independent body evidence must agree with her words before a fall can be resolved. This is the Get-Up Vote (§6, L4).

### 2.2 The Charger Trap (the false-alarm side)

**The obvious approach:** no movement means "not up yet" or "lying still after a fall", so alert the family.

**Why it's confidently wrong:** the watch is on the charger, or on the sink while she bathes. Absence of signal is not absence of movement. Each false alarm teaches the family to mute the app, and then the real fall is missed (alarm fatigue).

**How we beat it:** off-wrist detection (heart-rate sensor contact, Samsung off-body sensor), charging state and a drop signature produce a **GREY / UNKNOWN** state. UNKNOWN is **never** shown as OK and **never** blasted as an emergency (Blueprint 5.5, the Drishti "UNKNOWN ≠ FREE" pattern).

---

## 3. Positioning

**Category shift:** *Everyone does **detect → alert**. We do **verify → commit → stay**.*

| Everyone | Suraksha |
|---|---|
| "Are you OK?" and believe the answer | Her words are one vote. Her body casts the rest. |
| Alert everyone at once | Ask the **one person who can arrive**, get a commitment, tell her who |
| Go silent after alerting | Stay on the watch with her, in Hindi, until a human confirms arrival |
| No signal is treated as "fine" or "emergency" | No signal is **GREY**, shown as "can't tell" |
| A camera or dashboard watches her all day | Most days it says nothing. She decides what's shared (Cedar). |

**Competitor table** (every row's behaviour is UNVERIFIED until checked):

| Product | What it does | What it lacks | Our one-liner |
|---|---|---|---|
| Samsung Galaxy Watch fall detection | Detects a fall and calls or SMSes an SOS contact | Cancelled by a response; alerts a fixed contact; no conversation; no verification | "We run on the same watch, but we don't stop at her first answer." |
| Apple Watch fall detection | Same shape | Same | Same |
| Panic pendants (e.g. Indian elder-care alarm services) | A button calls a call centre | She has to press it, and has to want to | "She doesn't have to ask for help." |
| CCTV / home cameras | Family watches a feed | Kills her dignity and independence | "Nobody watches her." |
| Elder-care apps (medicine reminders, check-in calls) | Reminders, scheduled calls | Nothing in the emergency moment | "We do reminders too. The difference is 06:40." |

---

## 4. The one principle

> **"Her words are one vote."**

The AI listens, speaks and explains. **Code decides.** No single signal (words, a sensor or the LLM) can close a fall on its own.

---

## 5. Seven ordered questions = the pipeline = the folder tree

```
Q1  Did something happen?            sense/      watch: impact, free-fall, wake, off-wrist     ✅🔧
Q2  Is it real, or the Charger Trap? verify/     off-wrist, charging, drop signature → GREY    🆕
Q3  What does she say?               voice/ + agents/companion   Transcribe → Nova → Polly    ✅
Q4  Does her body agree?             getup/      the Get-Up Vote (5 voters)                    🆕
Q5  How sure are we?                 policy/tiers.py   → HARA / PEELA / LAAL / GREY             🔧
Q6  Who can show up, and may they?   escalation/ + policy/consent   Step Functions + Cedar     ✅🔧
Q7  Stay with her until they arrive. stay/       watch loop: relay ETA, check in every 60 s    🆕
```

Restructure `ally/` so the architecture slide **is** this tree (Blueprint 5.1). Move existing code; don't rewrite it.

---

## 6. Layer by layer

### L1 — sense/ (watch, Kotlin) ✅🔧
- **Mechanism:** `FallDetector.kt` (free-fall then an impact spike, or a hard impact after stillness), `WakeDetector.kt`, `StepsReader.kt`, `WatchVitals.kt` (HR, SpO₂).
- **🆕 Add the barometer** (`Sensor.TYPE_PRESSURE`; the Galaxy Watch 4 has one, UNVERIFIED for your exact model). Sample at 1–5 Hz into a 60 s ring buffer.
- **🆕 Fall payload:** send `{impact_g, freefall_ms, pressure_before_hpa, pressure_after_hpa, hr_before, on_wrist, charging, t}` to `/ally/watch` instead of a bare `kind: "fall"`.
- **Test:** replay recorded traces through the detector; the expected fire/no-fire for each trace is in `eval/traces/*.json`.

### L2 — verify/ (beats the Charger Trap) 🆕
- **Mechanism:** if `on_wrist == false` or `charging == true` at impact time, the result is `GREY` ("watch not on her"). The family view shows *"Can't tell — watch off wrist since 07:10"*, with no push.
- **Drop signature:** impact with zero rotation afterwards and no HR contact means the watch was dropped, not a fall.
- **Edge case:** off-wrist for more than her usual window (e.g. 3 h in daytime) triggers one gentle nudge to *her* ("Amma, ghadi pehen lijiye", i.e. "please put your watch on"), never to the family.
- **Test:** `test_charger_trap.py`: 10 drop and charger traces → 0 RED, 0 pushes.

### L3 — voice/ + companion ✅
- Transcribe (en-IN / hi-IN identification) → Nova companion → Polly Kajal. Already built.
- **🆕 Fall-mode prompt:** short questions only. *"Aap uth paa rahi hain?"* ("Can you get up?"), *"Kahin dard hai?"* ("Does it hurt anywhere?").
- `vocal_gate` (speech rate vs. her baseline) ✅ already exists. **Reuse it as voter V4.**

### L4 — getup/ : the Get-Up Vote (the heart of the project) 🆕

This runs on the server (`ally/getup/vote.py`) **and** is mirrored in Kotlin on the watch for offline mode (§8).

| Voter | Says "she's up" when | Data | Window after fall |
|---|---|---|---|
| V1 Words | Companion says `parent_says_okay` and not `parent_reports_unwell` | Transcribe + Nova | Any reply |
| V2 Steps | ≥ 8 steps since the fall | Step counter | 3 min |
| V3 Height | Pressure falls ≥ 0.05 hPa from the floor reading and holds 20 s (about +0.4 m, i.e. wrist rises from floor to standing) | Barometer | 3 min |
| V4 Voice | Speech rate ≥ 60% of her baseline wpm, no pain words | `vocal_gate` + deviation regex | Her reply |
| V5 Heart | HR within baseline + 15 bpm | PPG | 3 min |

**Decision, in code:**
- **HARA (green, resolved):** V1 **and** at least 2 of V2–V5.
- **PEELA (yellow, "soft check"):** V1 but fewer than 2 body votes. Suraksha says: *"Theek hai Amma, aapki baat maan li. Bas Priya ko bol rahi hoon ek baar call kar le."* ("Okay Amma, I believe you. I'm just asking Priya to call you once.") The nearest child gets a **low-urgency** "please call her" message, not a siren.
- **LAAL (red):** not V1 (unwell, can't get up, or silent for 90 s). Run the full chain (L6).
- **GREY:** from L2.

**Worked example (the demo case):** impact 3.1 g. She says "theek hoon" (V1 ✓). 0 steps (V2 ✗). Pressure unchanged (V3 ✗). Speech 58 wpm vs. 105 baseline (V4 ✗). HR 104 vs. 72 baseline (V5 ✗). That's 1 of 4 body votes, so **PEELA**. The naive system said resolved.

**Barometer caveat to state ourselves:** a door opening or AC draught shifts pressure by a few pascals. That's why V3 needs a 20 s hold and is only one vote of four. *(UNVERIFIED: measure the watch's real noise floor in the venue before trusting 0.05 hPa. Tune it on dev traces only.)*

**Test:** `test_getup_vote.py` uses table-driven cases with the expected tier written down.

### L5 — policy/tiers.py 🔧
- Today: two tiers decided by the judge's severity. **Change:** fall-path tiers come **only** from the Get-Up Vote. The LLM judge is still used for non-fall cases (late wake, words that sound unwell). It's one input there, never the decider.
- Colours appear everywhere: watch face, family app, spectator board.

### L6 — Who can show up (escalation + Cedar) ✅🔧
- ✅ The Step Functions chain: child → timeout → next child → ask her about the neighbour → neighbour if Cedar allows → failsafe notify-all.
- 🆕 **Who-Shows-Up ordering:** sort contacts by *can physically arrive*. Same city first, then past acceptance rate at this hour. Rahul (Pune) declining with "I'm far" demotes him for RED cases. This is the visible-learning beat (§10).
- 🆕 **Real phone call fallback:** Amazon Connect `StartOutboundVoiceContact`, ported from `backend/src/services/notifications.ts`, fires if a push isn't accepted within 45 s. Polly reads: *"Your mother may have fallen. Press 1 if you're going."*
- 🆕 **Location in the alert:** her home address from the profile. No live GPS.
- ✅ Cedar: "Priya ko meri tabiyat mat batana" ("don't tell Priya about my health") blocks health updates. **Safety cannot be forbidden** (`templates.py` FORBIDDABLE).

### L7 — stay/ : stay with her 🆕
- While an escalation is open, the watch keeps the conversation going. Every 60 s: *"Main yahin hoon. Priya 25 minute mein pahunch rahi hai."* ("I'm right here. Priya will be there in 25 minutes.")
- The family's "I'm on my way (ETA 25 min)" is relayed **verbatim from the escalation record**.
- Ends when the family taps **"Arrived"**. Only a human ends RED.

---

## 7. Uncertainty and safety: what the AI is never allowed to decide

1. **The AI never resolves a fall.** Only the Get-Up Vote (code) or a human "Arrived" tap can. 🆕
2. **The AI never cancels or downgrades an escalation.** 🔧
3. **No False Comfort gate** 🆕: the AI may not tell her "Rahul is coming" unless the escalation record says someone accepted. Every companion reply in fall mode is scanned for coming/arriving/told phrases (Hindi + English). If a phrase doesn't match the record, it's replaced with a template. This extends the existing `_compose_say` rule that "what Ally says matches what was saved". Mirrors Blueprint 5.4, layer 5.
4. **The AI never writes Cedar.** ✅ Fixed templates only.
5. **Family Q&A answers only from tool-returned records.** ✅

**Named invariant — the Floor Invariant** 🆕
> Once a fall is detected, no sequence of events (silence, LLM errors, timeouts, retries, duplicate webhooks) can lower the tier or reach RESOLVED without (V1 ∧ ≥2 body votes) or a human "Arrived".

Test it with **Hypothesis**: generate 10,000 random event sequences and assert **0 violations**. Put this number on the slide; it comes from the test run.

---

## 8. Degradation ladder

| What breaks | What still happens | Status |
|---|---|---|
| Bedrock down | Hindi templates ask the fall questions; the Get-Up Vote is unchanged (it never needed the LLM); `llm_unavailable` is shown | ✅ outage path exists; 🔧 add the fall templates |
| Transcribe down | The watch shows two big buttons: "Theek hoon" / "Madad chahiye" ("I'm fine" / "I need help"). V1 comes from the button, V4 abstains | 🆕 |
| Push not accepted | Amazon Connect phone call after 45 s | 🆕 |
| Watch has no network | **On-watch Get-Up Vote** runs in Kotlin, cached Polly audio speaks, the event queues and fires on reconnect, the alarm stays loud on the watch | 🆕 (stretch) |
| Watch off wrist | GREY, gentle nudge to her, never a false RED | 🆕 |
| Step Functions error | Failsafe notifies every child | ✅ |

**Chaos toggle** 🆕: a `POST /ally/dev/chaos {bedrock: "down"}` breaker flip, shown as a red switch on the spectator board.

---

## 9. Proof: metrics and evaluation

**Dataset we record ourselves** (`eval/traces/`) 🆕. Watch on wrist, falls onto a mattress, done safely.

| Class | Dev set | Held-out set |
|---|---|---|
| Real fall → gets up | 20 | 10 |
| Real fall → stays down, says "theek hoon" (the trap) | 20 | 10 |
| Real fall → stays down, silent | 10 | 5 |
| Hard sit on sofa | 15 | 8 |
| Watch dropped on table / put on charger | 15 | 8 |
| Daily noise (clapping, arm swing, bed) | 15 | 8 |

**One named teammate owns the held-out set.** Nobody tunes on it (Blueprint 6.2).

**Metrics** (`eval/metrics.py` → `metrics.json` → every pitch number):

| Metric | Baseline | Ours |
|---|---|---|
| **Trap catch rate**: stayed-down + "theek hoon" cases *not* resolved | Cancel-on-response (what commercial watches are reported to do; UNVERIFIED) | target ≥ 90% |
| False RED per drop/charger trace | Naive no-movement rule | target 0 |
| Got-up cases correctly resolved HARA (don't nag her) | — | target ≥ 85% |
| Time to committed responder (sim) | Broadcast-to-all, first to open | report seconds |
| Floor Invariant violations | — | 0 / 10,000 |

**Ablation** (proves each voter earns its place): rerun the held-out set with each voter removed (words-only, no barometer, no steps, …) and show the trap catch rate drop.

**Honest negative result to keep:** whatever fails (probably the barometer in a draughty venue, or the hard-sit vs. fall confusion). Publish it.

---

## 10. Demo design (3:00)

| Time | Beat | On screen |
|---|---|---|
| 0:00–0:10 | **Cold open:** black screen. A recorded mother's voice on a phone call: *"Haan beta, main theek hoon. Tum kaam karo."* ("Yes dear, I'm fine. You go to work.") Title: *"Every Indian mother says this. Even from the floor."* | Title card |
| 0:10–0:35 | **The trap, live.** Spectator board in **Naive mode**. A teammate falls on the mat, says "theek hoon", stays down. The board goes **HARA**: "Resolved". *"That's how watches work today. Confidently wrong."* | Board green ❌ |
| 0:35–1:15 | **Suraksha mode, same fall.** Voters light up live: Words ✓, Steps ✗, Height ✗, Voice ✗, Heart ✗ → **PEELA**. The watch says, in Hindi, it believes her but is asking Priya to call. | 5 voter lamps, tier |
| 1:15–1:40 | **Judge participates.** Before the demo, judges scanned a QR code and *became Priya*. Second fall, silent → **LAAL**. The judge's phone buzzes. The judge taps **"I'm on my way, 20 min"**. The watch says: *"Priya aa rahi hai, 20 minute. Main yahin hoon."* | Judge's phone |
| 1:40–2:05 | **Chaos toggle.** Flip "AI off". Run a third fall: the same tier, the same Hindi (templates). *"The decision never needed the AI."* | Red switch |
| 2:05–2:25 | **It learns.** Earlier, Rahul tapped "Can't — I'm in Pune". The board now shows the chain reordered: Priya first for RED. Also show "Priya ko tabiyat mat batana" blocking a *health* note while *safety* still goes. | Chain reorder + Cedar deny in audit |
| 2:25–2:45 | **Proof card** from `metrics.json`: trap catch rate vs. baseline (held-out, n = 10), false REDs 0/8, Floor Invariant 0/10,000. **Caveat first:** *"acted falls on a mattress by us, not elderly users."* | One card |
| 2:45–3:00 | **Close:** *"Her words are one vote. Not a medical device. 112 is always on the family screen."* | Logo |

**Backup:** a full recorded clean run. **Cut** anything high-variance (no real-floor falls).

---

## 11. Spectator layer 🆕

Who sees what:
- **Amma:** voice and haptics on the watch only.
- **Family:** the PWA (`/home`, `/family/respond/[id]`).
- **Judges:** the **Suraksha Live** board.

Board layout:
- Live sensor strips (accel g, pressure hPa, HR, steps) from the watch.
- 5 voter lamps, the tier colour and the escalation chain with who accepted and their ETA.
- The Naive/Suraksha toggle and the chaos switch.
- A **QR code** that opens `/join?role=family` on judges' phones.

Use the existing `three` / `framer-motion` stack, and skip the 3D world. Reuse `web/src/app/command` and `components/command/*`.

---

## 12. Rubric mapping

The rubric is unknown, so fill in `00_RULES.md` (Blueprint 12.1) when it's released. Generic mapping:

| Typical criterion | What answers it |
|---|---|
| Impact / usefulness | Long-lie cost, the 06:40 story, "would she keep wearing it": morning check-ins, reminders, quiet most days ✅ |
| Novelty | The Theek Hoon Trap + Get-Up Vote + verify → commit → stay |
| Technical depth | 5-sensor vote on real hardware, Cedar consent, Step Functions callbacks, the Floor Invariant property test, the degradation ladder |
| Working product | The live watch fall end to end, a real push and a real phone call |
| Demo / presentation | Cold open, trap live, judge-as-Priya, chaos toggle, proof card |
| Sponsor tech (if AWS) | Bedrock, Transcribe, Polly, Step Functions, Connect, DynamoDB, Cognito: remove them and the chain and voice stop working |

---

## 13. Challenge → answer

| Challenge | Answer |
|---|---|
| "Isn't this just Samsung fall detection?" | "Same watch. Samsung stops at her first answer; we check her body against it, and we stay with her." |
| "Isn't overriding 'I'm fine' disrespectful?" | "We never override her. PEELA only asks her nearest child to *call*, and she hears that we're doing it. Only RED runs the chain." |
| "Is the barometer real at wrist level?" | "It's one vote of four, with a 20 s hold. Here's our noise measurement and the ablation without it." |
| "Your falls are acted by 20-year-olds." | "Yes, we said it first. The held-out set is ours too. Next step: an elder-care home pilot." |
| "What if there's no internet?" | Degradation ladder: buttons, templates, the on-watch vote, a loud local alarm, the queue. |
| "What if the AI hallucinates 'help is coming'?" | The No False Comfort gate: claims are checked against the escalation record. |
| "Privacy?" | Nothing is streamed. Conversations are never shared (a Cedar base rule). She sets rules by voice. She can read her audit log. |
| "What's simulated?" | Pre-today history (labelled), the eval falls (acted), and the Connect call to a demo number. |
| "What failed?" | Our best negative result from §9. |
| "Business?" | The family pays a monthly subscription; elder-care homes and insurers are pilots. 🎤 One sentence only. |

---

## 14. Considered and rejected

- **Camera-based fall detection:** a dignity killer, and it fails in bathrooms.
- **LLM decides "is she okay":** this is the exact trap we're fighting.
- **Broadcast to all contacts:** creates the bystander effect and nobody commits.
- **The 3D explore world (`experience/`, `web/explore`):** ported third-party assets with no story value. Cut.
- **Hospital load-balancing sim (`sim-service/`):** off-story. Cut.
- **Post-discharge doctor flow:** a second product. Cut (one line in "what's next" at most).

## 15. What this is NOT

- Not a medical device and not an emergency service. **112** is always on the family screen.
- Not surveillance. No camera, no live location, no shared conversations.
- Not validated on elderly users yet.
- Not a replacement for Samsung SOS. It can run alongside it.

---

## 16. Keep / cut / build (repo actions)

| Keep ✅ | Change 🔧 | Build 🆕 | Cut ✂️ |
|---|---|---|---|
| `ally/` agents, store, policy, escalation, proactive, tests | `orchestrator.py:111` okay-resolves-fall → route through the vote | `getup/` vote (Python + Kotlin) | `experience/` (and the copyrighted mp3s) |
| `infra/` CDK + Step Functions | `tiers.py` → 4 colour tiers | `verify/` off-wrist/charger → GREY | `sim-service/` |
| `wear-os/` detectors, AudioBridge | Watch fall payload + barometer | `stay/` loop on the watch | `dashboard/` (Vite dupe) |
| `web/` parent, home, respond, command | Escalation order: Who-Shows-Up | No False Comfort gate | `backend/` after porting Connect |
| Cedar consent + audit | `/command` → Suraksha Live board | Connect call fallback | `web/explore`, `classic`, `doctor`, `checkin`, `patient`, `guard` |
| | | QR join-as-family | Hardcoded live URLs in `ally/README.md` |
| | | `eval/` traces + `metrics.py` + ablation | |
| | | Floor Invariant Hypothesis test | |
| | | Chaos toggle + Naive mode toggle | |
| | | 2-min onboarding + watch pairing code | |

---

## 17. Build map (dependency order)

| # | Ticket | Priority | Blocked by | Done when |
|---|---|---|---|---|
| 1 | Watch → `ally` fall payload (impact, pressure, HR, on-wrist, charging); confirm the watch uses `AllyHttp`, not the old `/ws` | CORE | — | A real watch drop creates an alert in DynamoDB with all fields |
| 2 | Barometer ring buffer + post-fall stream (steps, pressure, HR every 5 s for 3 min) | CORE | 1 | Trace JSON saved per fall |
| 3 | `getup/vote.py` + table tests | CORE | — | The worked example (§6 L4) returns PEELA |
| 4 | Replace `orchestrator.py:111` resolve-on-words with the vote | CORE | 3 | The trap case no longer resolves; existing 55 tests pass |
| 5 | `verify/` GREY state | CORE | 1 | `test_charger_trap` gives 0 RED |
| 6 | 4-colour tiers end to end (API → web) | CORE | 3 | The family view shows the colour + plain-language line |
| 7 | Watch speaks fall questions and replies via AudioBridge (no tablet) | CORE | 1 | The whole conversation happens on the watch |
| 8 | Stay loop + family ETA relay | CORE | 7 | The watch speaks the ETA from the record every 60 s |
| 9 | No False Comfort gate | CORE | 8 | An injected "Rahul aa raha hai" with no acceptance is replaced |
| 10 | Floor Invariant Hypothesis test | CORE | 4 | 10,000 cases, 0 violations |
| 11 | Suraksha Live board + Naive toggle + QR join | CORE | 6 | A judge's phone joins as Priya and receives the push |
| 12 | Chaos toggle | SUPPORTING | 11 | Bedrock is "down" and the tier is unchanged |
| 13 | Connect call fallback | SUPPORTING | — | A real call to a demo number with Polly audio |
| 14 | Who-Shows-Up ordering | SUPPORTING | — | Decline "far" → reordered next time |
| 15 | Record dev + held-out traces | CORE | 2 | Counts in §9 met; held-out sealed by its owner |
| 16 | `eval/metrics.py` + ablation → `metrics.json` | CORE | 3, 15 | The proof card renders from JSON |
| 17 | 2-min onboarding + watch pairing code | SUPPORTING | — | A new family is set up without `seed.py` |
| 18 | Transcribe-down buttons on the watch | SUPPORTING | 7 | Buttons feed V1 |
| 19 | On-watch Kotlin vote + offline queue | STRETCH | 3 | Works in airplane mode |
| 20 | Repo cleanup (cuts, rename to Suraksha everywhere, README in Blueprint 12.9 order) | SUPPORTING | — | One name, one backend |

**Demo-ready spine = tickets 1, 3, 4, 6, 7, 11.** Build that first.

---

## 18. Honesty inventory (fill in as tickets land)

| Component | What it really is | What we say on camera |
|---|---|---|
| Fall detection | Deterministic accelerometer rule on the watch | "Classic free-fall + impact rule" |
| Get-Up Vote | Deterministic, 5 voters | "Code decides, not the AI" |
| Words voter | Nova structured output | "The AI understands her Hinglish; it's one vote" |
| Eval falls | Acted by the team on a mattress | Said **before** the number |
| History before today | Simulated, labelled | "Today is live" |
| Phone call | Real Connect call to our demo number | "Real call, demo number" |

---

## 19. Team roles (fill in names)

- **Spine / watch owner:** tickets 1, 2, 7, 19.
- **Brain owner:** tickets 3, 4, 5, 9, 10, 14.
- **Show owner:** tickets 6, 11, 12, 17, plus the pitch and backup video.
- **Held-out owner:** records and seals the held-out set; nobody else sees it until the final run.

---

## 20. Key numbers by heart

These are filled in **from `metrics.json` only**: trap catch rate (ours vs. baseline), false REDs, Floor Invariant cases, the n of the held-out set, and median time to a committed responder.

## 21. One-paragraph pitch

Every year, elderly Indians fall at home and lie on the floor for hours. That isn't because nobody detected the fall. It's because they said "theek hoon". Today's watches ask "Are you OK?" and believe the answer. Suraksha, on a Galaxy Watch, treats her words as one vote. Her steps, the barometer, her voice and her heart cast the rest. If they disagree, it gently asks her nearest child to call. If she's down, it gets the one person who can actually arrive to commit, rings them if they miss the push, and stays talking to her in Hindi until they walk in. Most days it says nothing at all.

## 22. Glossary

- **Theek Hoon Trap:** an "I'm fine" given while unable to get up.
- **Charger Trap:** no signal mistaken for no movement.
- **Get-Up Vote:** words + 4 body voters → tier.
- **HARA / PEELA / LAAL / GREY:** green (resolved), yellow (soft check), red (chain running), grey (can't tell).
- **Floor Invariant:** nothing but evidence or a human lowers a fall's tier.
- **No False Comfort gate:** the AI can't promise help the record doesn't show.
- **Who-Shows-Up:** contacts ordered by who can physically arrive.

---

## Changelog

- **v1:** first bible. Recentred the repo from "family-care companion" onto the Theek Hoon Trap. Next: run red-team rounds P4 ×3 and a mock judge (P5) once the rubric is known (Blueprint Part 11).
