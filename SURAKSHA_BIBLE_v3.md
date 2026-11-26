# SURAKSHA — Bible v3

*The watch that doesn't take "theek hoon" for an answer.*

**v3 = v2 + 17 round-4 fixes (#27–#43).** The flaw numbers (#N) refer to [`RED_TEAM_LOG.md`](RED_TEAM_LOG.md). v1 and v2 are kept as history.

**Status legend:** ✅ built · 🔧 built, needs change · 🆕 build · 🎤 pitch-only. **Every outside fact is UNVERIFIED** until it's sourced.

---

## 0. One-line pitch

Smartwatches ask an elderly parent "Are you OK?" after a fall and **believe the answer**. Suraksha treats her words as **one vote**. It asks her body to *show* it, then gets **one person who can actually arrive** to commit, and stays with her until they do.

## 1. The person, the moment, the cost

- **Person:** Kamala Sharma ("Amma"), 72, alone in Bengaluru. Son Rahul is in Pune (840 km away), daughter Priya is in Bengaluru (40 minutes away), and Sunita aunty is next door. *(Seeded in `ally/seed/amma.json`.)*
- **Moment:** 06:40, bathroom floor. Her hip hurts. The watch asks "Are you OK?". She says **"haan, theek hoon"** ("yes, I'm fine") so Rahul isn't worried before work. The watch cancels.
- **Cost:** the long lie (hours on the floor) means dehydration, pressure injury, pneumonia and admission. *(UNVERIFIED: source it.)*

**Killer facts to source or cut:** the 60+ population living alone; the annual fall rate and how many can't get up; long-lie outcomes; **the exact cancel behaviour of Samsung and Apple fall detection (read their docs)**; parents under-reporting to their children.

**Hook:** *"06:40. Amma's on the bathroom floor. Her watch asks if she's okay. She says 'theek hoon', because every Indian mother says 'theek hoon'. The watch believes her. Rahul finds out at 1 pm."*

## 2. The traps

### 2.1 The "Theek Hoon" Trap (the hero)
- **Naive:** fall → "Are you OK?" → any "I'm OK" cancels.
- **Confidently wrong:** the person most likely to under-report is the one on the floor.
- **📂 It's in our repo:** in `ally/agents/orchestrator.py:111`, `parent_says_okay` leads to `on_im_okay()`, which resolves both the investigation and the escalation.
- **Beaten by:** the **Do-Check** plus the **Get-Up Vote** (L4). Her words open the question; her body has to answer it.

### 2.2 The Charger Trap (the false-alarm side)
- **Naive:** no movement means she's down or not up.
- **Confidently wrong:** the watch is on the charger or the sink, or was just dropped on a table. False alarms make the family mute the app, and then the real fall is missed.
- **📂 Our detector creates this trap.** `FallDetector.kt` fires on "a deliberate drop from ~20–40 cm" (#2).
- **Beaten by:** splitting `fall` from `drop`, plus on-wrist/charging checks → **GREY**. GREY is never OK and never an emergency.

## 3. Positioning

**Category shift:** *Everyone does **detect → alert**. We do **verify → commit → stay**.*

| Everyone | Suraksha |
|---|---|
| Asks "Are you OK?" and believes the answer | Asks her to *show* it: "walk to the door for me" |
| Alerts everyone at once | Gets the one person who can arrive to commit, and tells her who |
| Goes silent after alerting | Stays talking to her in Hindi until a human taps "Arrived" |
| No signal = fine, or = emergency | No signal = GREY, "can't tell" |
| A camera or feed watches her | Says nothing most days; she sets the privacy rules by voice |

**Competitors** (behaviour UNVERIFIED until checked): Samsung and Apple Watch fall detection; panic pendants; CCTV; elder-care reminder apps.

**"Isn't this just a confirmation step?"** → *"A confirmation step asks her. Ours asks her body to show it."*

## 4. The one principle

> **"Her words are one vote."** The AI listens, speaks and explains. Code decides. No single signal closes a fall.

## 5. Seven questions = pipeline = folder tree

```
Q1 Did something happen?           sense/     watch: fall vs drop, wake, on-wrist, charging   🔧
Q2 Real, or the Charger Trap?      verify/    drop / off-wrist / charging → GREY              🆕
Q3 What does she say?              voice/ + agents/companion  (fall mode = short + templated) ✅🔧
Q4 Can she show it?                getup/     Do-Check + Get-Up Vote + concern flags          🆕
Q5 How sure are we?                policy/tiers.py → HARA / PEELA / LAAL / GREY               🔧
Q6 Who can arrive, and may they?   escalation/ + policy/consent   Nearest-First, Cedar        ✅🔧
Q7 Stay with her.                  stay/      watch loop, ETA from the record                 🆕
```

---

## 6. Layer by layer

### L1 — sense/ (watch) 🔧
- **One brain (#1):** the fall goes to `ally` only. Remove the `EmergencyClient` `/ws` fall path from `RakshakViewModel.onFallDetected()`. Voice in and out uses `ally` (`/ally/parent/audio`, `/ally/tts`) through `AudioBridge` (`playBase64Wav` ✅).
- **Split the detector (#2):** a free-fall (≥ 80 ms below 3 m/s²) followed by an impact above 18 m/s², **with PPG contact**, sends `fall`. An impact after stillness, or anything off-wrist, sends `drop`.
- **🆕 Barometer** `TYPE_PRESSURE` ring buffer (**1 Hz idle, 5 Hz after a fall**, 60 s; battery, #32). **🆕 `TYPE_STEP_DETECTOR`** events (#6). **🆕 `BatteryManager`** charging state. 🆕 off-body detection via `TYPE_LOW_LATENCY_OFFBODY_DETECT` if present (UNVERIFIED on Watch 4), otherwise PPG contact.
- **Fall payload:** `{kind, impact_ms2, freefall_ms, p_ref_hpa (median of the 10 s before the fall), on_wrist, charging, hr_before, t}`. After the fall, the watch streams `{p_hpa, steps, hr, accel_var}` every 2 s for `GETUP_WINDOW_S`.
- 🆕 **Foreground health service** with a persistent notification (#10).
- **Charging window (#32):** onboarding sets charging for the **morning bath or breakfast**, never overnight. Night-time bathroom trips are a reported peak fall time (UNVERIFIED; source it). A GREY at night triggers a gentle nudge to wear it. **Battery % per hour with our sensor load is measured** and becomes a proof number.

### L2 — verify/ 🆕
- A `drop`, `on_wrist=false` or `charging=true` produces **GREY**: *"Can't tell, watch off wrist since 07:10."* No push is sent.
- **Off-wrist at an unusual hour (#22):** longer than her usual bath duration (learned from history, default 25 min) triggers a gentle ask **to her first** (on the watch when it's back on, or the phone). It never goes to family first.

### L3 — voice / companion, fall mode 🔧
- Short questions only. **Status sentences are templates** filled from the escalation record (#9). The LLM writes only the comfort sentence.

### L4 — getup/: Do-Check + Get-Up Vote 🆕

**Step 1 — ask.** *"Amma, aap theek hain?"* ("Amma, are you okay?")

**Step 2 — if she says she's fine, run the Do-Check (#3, made safe by #27).**
> *"Achha. Agar dard nahi hai, toh aaram se uthiye aur darwaze tak chaliye. Agar dard hai, toh bilkul mat uthiye, wahin rahiye, main madad bula rahi hoon."*
> ("Okay. If there's no pain, get up slowly and walk to the door. If it hurts, don't get up at all. Stay there, I'm calling for help.")

**Never tell an injured person to stand.** The Do-Check is *conditional* and gives her **permission to stay down**. Staying down is never penalised for her; it only picks the right tier. Offering a dignified "it's okay if it hurts" is also what makes her more likely to say so.

**Mobility aids (#28):** a profile field `mobility`. Walker: a lower stride band. Wheelchair: `p_ref` = seated height, V3 abstains, and the Do-Check becomes "move back to your chair".

**Step 3 — vote**, within `GETUP_WINDOW_S` (180 real, 40 stage; said on camera, #8).

| Voter | Votes "up" when | Abstains when |
|---|---|---|
| **V1 Words** | `parent_says_okay` ∧ ¬`parent_reports_unwell` | — |
| **V2 Height** | Pressure returns to within **0.03 hPa of `p_ref`** (her own pre-fall wrist height), held 15 s, with accel variance below the arm-waving threshold (#5) | No barometer |
| **V3 Movement** | ≥ 6 step-detector events **or** ≥ 6 strides of 0.5–2 Hz accelerometer cadence | Sensors missing |
| **V4 Voice** | A reply of ≥ 4 words, speech rate ≥ 60% of her baseline wpm, no pain words | Reply < 4 words |

**Concern flags** can only *raise* the tier, never lower it (#4): HR > 130 or < 45 sustained for 20 s; SpO₂ < 90%; PPG contact lost after the fall; pain words ("dard", "uth nahi pa rahi" = "I can't get up").

**Decision, in code:**
- **Abstain = "not up"** (#7).
- **HARA (green):** V1 ∧ ≥ 2 of {V2, V3, V4} ∧ no concern flag. **Nobody is messaged.**
- **PEELA (yellow):** V1 but the body doesn't confirm. She hears: *"Theek hai Amma, aapki baat maan li. Bas Priya ko bol rahi hoon ek baar call kar le."* ("Okay Amma, I believe you. I'm just asking Priya to call you once.") Priya gets: *"Please give Amma a call when you can"*, with **no health detail** (#20).
  **The loop must close (#29):** Priya's page shows "Spoke to her ✓" and "No answer". "No answer", or no tap within **10 min (stage: 30 s)**, **auto-upgrades to LAAL**.
- **LAAL (red):** ¬V1 (unwell, "can't get up", silence for 30 s stage / 90 s real), or any concern flag, or Do-Check silence after the window (#23).
- **GREY:** from L2.

**Worked example (the hero case):** free-fall 140 ms, impact 31 m/s², on-wrist. She says "theek hoon" (V1 ✓). Do-Check: pressure stays 0.09 hPa above `p_ref`, meaning her wrist is about 0.8 m lower (V2 ✗). 0 steps (V3 ✗). No ≥ 4-word reply (V4 abstains = ✗). HR 104, below the flag threshold. **Result: PEELA.** Naive = resolved. B1 (sceptical LLM on her words) = report whatever it actually says.

**Cost asymmetry (#21):**

| Error | Cost | Design bias |
|---|---|---|
| False HARA (she's down, we say fine) | A long lie, possibly fatal | **Never acceptable**, hence abstain = not up |
| False PEELA (she's fine, we ask Priya to call) | One phone call | Cheap, accepted |
| False LAAL (family rushes for nothing) | Panic and lost trust | Kept low, via GREY and the fall/drop split |

### L5 — tiers 🔧
For the fall path, tiers come **only** from L4. The LLM judge stays for non-fall cases (late wake, words that sound unwell), as one input there.

### L6 — who can arrive ✅🔧
- ✅ Step Functions: contact → timeout → next → ask her about the neighbour → neighbour if Cedar allows → failsafe.
- 🆕 **Fall pre-consent → neighbour in parallel (#30):** 📂 today `steps.py:158` asks about Sunita only after both children fail. That's backwards for a fall. At onboarding Amma says *"gir jaaun toh Sunita ko pehle bulana"* ("if I fall, call Sunita first"). That becomes a fixed-template Cedar `permit` with `context.reason == "fall"`. For a LAAL fall, **the neighbour and the nearest child are asked in parallel**, and the first to accept is "the one coming". Without pre-consent, the old order applies.
- 🆕 **Nearest-First ordering** (#16): same city first, then past acceptances at this hour. It's deterministic and called "adapts", not "learns".
- 🆕 **Amazon Connect call** if a LAAL push isn't accepted within 45 s. Port it from `backend/src/services/notifications.ts`.
- 🆕 The home address from her profile goes in the LAAL alert. No live GPS.
- ✅ Cedar: safety is not forbiddable. PEELA text carries no health detail (#20).

### L7 — stay/ 🆕
Every 60 s, the watch speaks a templated status from the record: *"Main yahin hoon. Priya 20 minute mein pahunch rahi hai."* ("I'm right here. Priya will be there in 20 minutes.") Each prompt is preceded by a haptic, at max volume (#25). It ends only when a human taps **Arrived**. If there's no "Arrived" by **ETA + 15 min**, the responder is asked "Still coming?" and the chain re-opens to the next contact (#31).

---

## 7. What the AI is never allowed to decide

1. It never resolves a fall. Only the L4 vote or a human "Arrived" tap can.
2. It never cancels or downgrades an escalation.
3. **No False Comfort:** status sentences are templates from the record. The AI's comfort sentence is dropped if it contains any status claim.
4. It never writes Cedar ✅.
5. Family Q&A comes from tool records only ✅.

**Floor Invariant:** after a fall, no event sequence lowers the tier or reaches RESOLVED without (V1 ∧ ≥ 2 body votes ∧ no flag) or a human "Arrived". Tested **through the real orchestrator** (moto + fake clock) with Hypothesis (#11). Injected faults include LLM errors, duplicate watch posts and push replies, out-of-order events and abstaining sensors. Pitch number: the case count and 0 violations, from the test output.

## 8. Degradation ladder

| Breaks | Still happens |
|---|---|
| Bedrock | Hindi templates; L4 is unchanged (it never used the LLM); `llm_unavailable` is shown |
| Transcribe | Watch buttons "Theek hoon" / "Madad chahiye" ("I'm fine" / "I need help") feed V1; V4 abstains |
| Push ignored | Connect call after 45 s, then the next contact |
| No network on the watch | 🆕 **On-watch Kotlin vote + cached Polly audio** gives the tier on the watch and a loud local alarm; events queue until reconnect (SUPPORTING, #12) |
| Off wrist | GREY, ask her first |
| Step Functions error | Failsafe notifies all ✅ |

**Venue rule (#12):** personal hotspot only, and a backup video. We never claim "offline".

## 9. Proof

**Traces** (`eval/traces/`): watch on wrist, firm gym mat, done safely. Each trace stores the raw sensor stream plus the label.

**Feasible plan (#36):** 60 traces, 60 s post-fall stream each, about 2 hours. Use **controlled falls**: kneel first, then go down sideways onto a firm mat.

| Class | Dev | Held-out |
|---|---|---|
| Fall → gets up + walks (Do-Check passes) | 8 | 5 |
| Fall → stays down, says "theek hoon" (trap) | 8 | 5 |
| Fall → silent | 4 | 3 |
| Hard sit on the sofa | 5 | 4 |
| Watch dropped / put on the charger | 6 | 4 |
| Daily noise (clap, arm swing, raising an arm while lying) | 5 | 3 |
| **Total** | **36** | **24** |

**🆕 Wear test (#33), run FIRST:** two teammates wear the watch through normal days (≥ 16 h each). Report `fall` triggers per wear-day. That's the honest **nag budget**, and the riskiest unknown in the project.

**🆕 Latency budget (#38),** measured on the real stack:

| Hop | Target | Measured |
|---|---|---|
| Fall → first spoken question | < 1.5 s (cached Polly audio) | |
| Her reply ends → Do-Check prompt starts | < 4 s | |
| LAAL decided → judge's phone rings | < 3 s | |
| Battery % per hour, armed | — | |

**The held-out set is sealed** by its named owner.

**Baselines (#15):**
- **B0:** cancel-on-response.
- **B1:** our own Nova judge reading her words with a *sceptical* prompt. This is the honest one.
- **B2:** steps-only.

**Metrics** (`eval/metrics.py` → `metrics.json`):

| Metric | B0 | B1 | B2 | Ours (held-out) |
|---|---|---|---|---|
| Trap catch rate (not resolved when down) | | | | |
| Got-up correctly HARA (no nag) | | | | |
| False LAAL per drop/charger/noise trace | | | | |
| Floor Invariant violations / cases (#39: 1,000 seeded) | — | — | — | 0 / N |
| False `fall` triggers per wear-day (#33) | — | — | — | |
| Box → armed onboarding time (#41) | — | — | — | |

**Ablation:** remove V2, V3 and V4 one at a time and report the catch and no-nag rates.

**Rehearsal metric (#13):** fall fire rate on the stage mat must be 10/10 before demo day.

**Keep the best negative result** for Q&A (likely the barometer in a draughty room, or hard-sit vs. fall).

---

## 10. Demo (3:00)

| Time | Beat |
|---|---|
| 0:00–0:10 | **Cold open:** a mother's voice, *"Haan beta, main theek hoon. Tum kaam karo."* ("Yes dear, I'm fine. You go to work.") Title: *"Every Indian mother says this. Even from the floor."* |
| 0:10–0:30 | **Trap, live:** the board in **Naive mode**, which is *our own old code* (#40). A teammate falls on the mat, says "theek hoon", stays down. The board goes HARA "Resolved". *"That's how watches work today, and it's how ours worked last month. Confidently wrong."* |
| 0:30–1:05 | **Suraksha, same fall:** "theek hoon" → watch: *"agar dard nahi hai, darwaze tak chaliye; dard hai toh wahin rahiye"* ("if there's no pain, walk to the door; if it hurts, stay there") → she stays down → lamps: Words ✓ Height ✗ Movement ✗ Voice — → **PEELA**. The judge (who scanned the QR as **Priya**) gets *"Please give Amma a call."* |
| 1:05–1:20 | **It stays quiet (#17):** fall → "theek hoon" → she **gets up and walks** → **HARA**, nobody messaged. *"When she's actually fine, nobody gets bothered."* |
| 1:20–1:55 | **Red:** silent fall → **LAAL** → the judge's phone rings on the page → the judge taps *"On my way, 20 min"* → the watch says *"Priya aa rahi hai, 20 minute. Main yahin hoon."* ("Priya is coming, 20 minutes. I'm right here.") Then the reveal (#18): *"I switched the AI off before that one."* |
| 1:55–2:15 | **Two-tier beat (one line each):** Sunita aunty was asked *in parallel* because Amma pre-consented for falls (#30); "every other day it's a quiet companion: morning check-in, voice reminders" (#34); Nearest-First (Rahul tapped "I'm in Pune" earlier, so Priya is first); Cedar ("tabiyat mat batana" = "don't tell about my health") means PEELA carried no health detail. |
| 2:15–2:40 | **Proof card** from `metrics.json`. **Caveat first:** *"acted falls on a mat, by us, not elderly users; windows shortened for stage."* Then the numbers vs. B1. |
| 2:40–3:00 | **Close:** *"Her words are one vote. Not a medical device. 112 is always on the family screen."* |

**Fallbacks:** a REPLAY button on the board (a recorded real trace, labelled REPLAY); a full backup video; the hotspot.

## 11. Spectator layer 🆕

- **Suraksha Live board:** live sensor strips (accel, pressure vs. `p_ref`, HR, steps), the V1–V4 lamps plus concern flags, the tier colour, the chain with ETA, the Naive/Suraksha toggle, the AI-off switch, REPLAY and the QR code.
- **Transport (#37):** 📂 the web already polls (`useSurakshaState.ts`). The board and `/join` poll `GET /ally/live/<session>` every 1 s, a single DynamoDB item. A warm-up pinger runs 10 min before the demo.
- **Naive mode = our own old code (#40):** the `orchestrator.py:111` resolve-on-words path, kept behind a flag. On stage: *"This isn't a strawman. It's our own code from last month."*
- **First-tap-wins** when several judges scan the QR (#43).
- **QR → `/join/<demo-session>`:** no login and no Web Push (#14). A live socket with on-page sound and vibration, plus "Call Amma", "On my way + ETA" and "Can't, I'm far". Tested on iPhone Safari and Android Chrome.

## 12. Rubric mapping

Generic until the rules are known (fill in `00_RULES.md`). Impact → §1; novelty → §2–3; depth → L4, the Floor Invariant, Cedar, Step Functions; working product → spine + 10/10 fire rate; demo → §10; sponsor tech (AWS) → Bedrock, Transcribe, Polly, Step Functions, Connect, DynamoDB, Cognito are load-bearing.

## 13. Challenge → answer

| Challenge | Answer |
|---|---|
| "Isn't this Samsung fall detection?" | "Same watch. It stops at her first answer. We ask her body to show it, and we stay." |
| "Isn't it just a confirmation step?" | "A confirmation step asks her. Ours asks her body." |
| "You override her 'I'm fine'?" | "Never in front of her. We believe her out loud, and only ask her daughter to *call*. One call vs. a long lie." |
| "Is the barometer real at the wrist?" | "Relative to *her own* height 10 s before the fall, held 15 s, one vote of three. Here's the ablation without it." |
| "Acted falls by 20-year-olds." | "Said first. The held-out set is sealed. Next is a care-home pilot." |
| "She takes the watch off to bathe." | "GREY, never false-red. Off too long at an odd hour → we ask her first. It's water-resistant; onboarding asks her to keep it on." |
| "No internet?" | "Tier on the watch, loud alarm, queue. We don't claim offline; it's hotspot-backed today." |
| "AI says 'help is coming' when it isn't?" | "It can't. Status lines are templates from the record." |
| "You told an injured woman to stand up?" | "Never. The Do-Check says: if it hurts, stay where you are. Staying down just picks the right tier." (#27) |
| "Night falls, when the watch is charging?" | "Charging is set for her morning bath, not night. Here's our battery-per-hour number." (#32) |
| "How often does it falsely trigger in real life?" | "Our wear test: N triggers across M hours, said with the caveat that it's young wearers." (#33) |
| "Why is the neighbour last?" | "She isn't, for falls. Amma pre-consents and Sunita is asked in parallel." (#30) |
| "Data protection?" | "Consent at onboarding, 7-day TTL on raw traces, no audio kept after transcription, an audit she can read. We don't claim legal compliance." (#42) |
| "Dementia?" | "Not designed for it. No answer to the Do-Check fails safe to red." |
| "What's simulated?" | Pre-today history (labelled), the acted eval falls, a demo phone number, shortened stage windows. |

## 14. Considered and rejected

- Cameras.
- An LLM deciding "is she okay".
- Broadcasting to everyone at once.
- HR as an "up" voter (#4).
- An absolute barometer threshold (#5).
- Web Push for judges (#14).
- 3D explore world, sim-service, post-discharge flow.

## 15. What this is NOT

- Not a medical device or emergency service; 112 is always shown.
- Not surveillance: the mic only opens after a fall, a tap or a check-in (#24).
- Not validated on elderly users.
- Not for dementia.
- Not offline-first.
- Hindi, Hinglish and English only today; Kannada and others are next (#35).
- Not a substitute for wearing it: GREY is honest, not magic.

## 16. Keep / change / build / cut

| Keep ✅ | Change 🔧 | Build 🆕 | Cut ✂️ |
|---|---|---|---|
| `ally/` agents, store, policy, escalation, tests | `orchestrator.py:111` → L4 | `getup/` (Python, and later Kotlin) | `experience/` + copyrighted mp3s |
| `infra/` CDK + Step Functions | `FallDetector` → fall/drop split | `verify/` GREY | `sim-service/`, `dashboard/` |
| `AudioBridge`, step/vitals readers | `RakshakViewModel` → one brain | Do-Check prompts | `backend/` (after the Connect port) |
| Cedar + audit | Tiers → 4 colours | Barometer + step detector + charging | `web/explore`, `classic`, `doctor`, `checkin`, `patient`, `guard` |
| `web/` parent, home, respond, command | `/command` → Live board | `stay/` loop, No False Comfort templates | Live URLs in `ally/README.md` |
| | | `/join` guest page, REPLAY, AI-off, Naive toggle | |
| | | `eval/` traces, `metrics.py`, baselines, ablation, Hypothesis | |
| | | Foreground service, Connect call, Nearest-First, onboarding | |

## 17. Build map

| # | Ticket | Pri | Blocked by | Done when |
|---|---|---|---|---|
| 1 | One brain: watch fall → `ally` only; voice via `ally` audio/TTS | CORE | — | A fall produces one conversation, on the watch |
| 2 | `fall` vs. `drop` split + on-wrist/charging in the payload | CORE | 1 | A desk drop gives `drop`; a mat fall gives `fall` |
| 3 | Barometer `p_ref` + post-fall stream (pressure, step detector, HR, accel var) | CORE | 1 | A trace JSON is saved per fall |
| 4 | `getup/vote.py` with abstain = not up, flags, table tests | CORE | — | The §6 worked example gives PEELA |
| 5 | Do-Check prompt + replace `orchestrator.py:111` | CORE | 4 | The trap case is not resolved; the existing 55 tests still pass |
| 6 | `verify/` GREY | CORE | 2 | 0 LAAL on drop/charger traces |
| 7 | 4-colour tiers end to end + templated status lines | CORE | 4 | The family view and watch show colour + plain language |
| 8 | Live board + `/join` guest page + Naive toggle + REPLAY | CORE | 7 | A stranger's iPhone joins as Priya and gets the PEELA |
| 9 | Record traces; seal the held-out set | CORE | 3 | §9 counts met; mat fire rate 10/10 |
| 10 | `metrics.py` + B0/B1/B2 + ablation → `metrics.json` | SUPPORTING | 4, 9 | The proof card renders from JSON |
| 11 | Floor Invariant via the orchestrator (Hypothesis) | SUPPORTING | 5 | N cases, 0 violations |
| 12 | Stay loop + ETA relay | SUPPORTING | 7 | ETA is spoken from the record every 60 s |
| 13 | AI-off switch | SUPPORTING | 8 | Same tier and templates with Bedrock "down" |
| 14 | Connect call fallback | SUPPORTING | — | A real call to the demo number |
| 15 | On-watch Kotlin vote + cached audio + queue | SUPPORTING | 4 | Tier shown on the watch in airplane mode |
| 15a | **Wear test** (#33), run first | CORE | 2 | Triggers per wear-day recorded for ≥ 32 h |
| 15b | PEELA loop close + auto-upgrade (#29) | CORE | 7 | "No answer" / timeout gives LAAL |
| 15c | Fall pre-consent + neighbour in parallel (#30) | SUPPORTING | 7 | Sunita and Priya are asked at the same time |
| 15d | `GET /ally/live` + 1 s polling + warm-up pinger (#37) | CORE | 7 | Board latency < 1.5 s |
| 15e | Latency + battery measurement (#38, #32) | SUPPORTING | 1 | Tables in §9 filled |
| 16 | Foreground health service | SUPPORTING | 1 | Sensors survive the app being backgrounded |
| 17 | Nearest-First ordering | STRETCH | — | "I'm far" → reordered |
| 18 | **Minimal onboarding** (#41): QR on the watch → name, language, 2–3 contacts, fall pre-consent, charge window | SUPPORTING | 15c | Box → armed in < 3 min, timed |
| 19 | Transcribe-down buttons | STRETCH | 1 | Buttons feed V1 |
| 20 | Repo cleanup + one name + README (Blueprint 12.9) | SUPPORTING | — | One name, one backend |

**Spine = 1 → 2 → 3 → 4 → 5 → 7 → 15d → 8 → 15b.** The wear test (15a) starts **the moment #2 lands**, because it's the riskiest unknown. Traces (9) run alongside as soon as #3 lands.

## 18. Honesty inventory

| Component | Really is | Say on camera |
|---|---|---|
| Fall detection | A deterministic accelerometer rule | "Classic free-fall + impact" |
| Do-Check + vote | Deterministic | "Code decides, not the AI" |
| V1 words | Nova structured output | "The AI understands her Hinglish. It's one vote" |
| Eval falls | Acted by us on a mat | Said **before** the number |
| Windows | 40 s stage / 180 s real | Said on camera |
| Phone call | A real Connect call to our number | "Real call, demo number" |
| History | Simulated, labelled | "Today is live" |

## 19. Roles

- **Watch owner:** tickets 1, 2, 3, 15, 16.
- **Brain owner:** tickets 4, 5, 6, 11, 12.
- **Show owner:** tickets 7, 8, 13, the pitch and the backup video.
- **Held-out owner:** ticket 9, sealing the held-out set.

## 20. Key numbers by heart

From `metrics.json` only: trap catch rate (ours vs. B1), no-nag rate, false LAAL, Floor Invariant N, held-out n, mat fire rate.

## 21. One-paragraph pitch

Elderly Indians fall at home and lie on the floor for hours. That isn't because nobody noticed. It's because they said "theek hoon". Watches ask "Are you OK?" and believe the answer. Suraksha, on a Galaxy Watch, treats her words as one vote and asks her to *show* it: "walk to the door for me". The barometer, her steps and her voice check. If her body disagrees, it gently asks her daughter to call. If she's down, it gets the one person who can arrive to commit, rings them if they miss it, and keeps talking to her in Hindi until they walk in. When she's fine, nobody is bothered. Most days it says nothing at all.

## 22. Glossary

- **Theek Hoon Trap:** "I'm fine" said while down.
- **Charger Trap:** no signal mistaken for no movement.
- **Do-Check:** asking her to stand and walk.
- **Get-Up Vote:** V1 words + V2 height + V3 movement + V4 voice.
- **Concern flags:** signals that can only raise the tier.
- **Abstain = not up.**
- **HARA / PEELA / LAAL / GREY:** green, yellow, red, grey.
- **Floor Invariant.**
- **No False Comfort.**
- **Nearest-First.**

## Changelog

- **v1:** recentred the repo on the Theek Hoon Trap.
- **v2:** 26 red-team fixes ([`RED_TEAM_LOG.md`](RED_TEAM_LOG.md)).
  - **CRIT:** one brain (#1), fall/drop split (#2), Do-Check (#3), venue internet (#12), stage fall reliability (#13).
  - **HIGH:** HR → concern flag (#4), relative barometer (#5), step detector (#6), abstain = not up (#7), stage windows disclosed (#8), guest page instead of Web Push (#14), honest baselines (#15), consent-safe PEELA (#20), dignity + cost asymmetry (#21), bathroom (#22).
  - **Spine cut from 20 CORE-ish tickets to 7.**
- **v3:** round 4, 17 fixes.
  - **CRIT:** the Do-Check never tells her to stand (#27); the trace plan cut from about 9 h to 2 h (#36).
  - **HIGH:** PEELA loop closes (#29), neighbour in parallel for falls (#30), charging window and night coverage (#32), wear test (#33), board transport (#37), Naive = our own old code (#40), onboarding promoted (#41).
- **Open for v4:** barometer noise, off-body sensor, sourced facts (including night falls), battery, wear-test trigger rate, the real rubric.
