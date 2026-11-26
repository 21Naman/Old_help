# SURAKSHA — Bible v4

*Every watch gives her two buttons: "I'm OK" or "ambulance". Suraksha is the third.*

**v4 = v3 + the research** (tracks 1–8 in [`research/`](research/)). It applies all 10 MUST and 10 SHOULD changes from [`research/08_SYNTHESIS.md`](research/08_SYNTHESIS.md); the 7 NICE items are folded into §13. Flaw numbers (#N) refer to [`RED_TEAM_LOG.md`](RED_TEAM_LOG.md); research references are `[T1]`–`[T7]` (the track files). v1–v3 are kept as history.

**Status legend:** ✅ built · 🔧 built, needs change · 🆕 build · 🎤 pitch-only · 🔬 measure on the watch first.

---

## 0. One-line pitch

After a fall, every watch and alarm offers two exits: **"I'm OK"** (nothing happens) or **"emergency"** (siren, call centre, ambulance). Hurt, proud people choose "I'm OK". **Suraksha adds the third option** ("I believe you; I'm just asking your daughter to call"), **asks her body to confirm**, gets **the one person who can arrive** to commit, and **stays with her** until they do.

## 1. The person, the moment, the cost

- **Person:** Kamala Sharma ("Amma"), 72, widowed, alone in Bengaluru. Son Rahul is in Pune; daughter Priya is 40 minutes away; Sunita aunty is next door. *(Seeded in `suraksha/seed/amma.json`.)*
  - In India, **women living alone have the highest fall rate: 27.6%** (LASI wave 1, adults 45+) [T2].
- **Moment:** 06:40, bathroom floor. Her watch asks "Are you OK?" and offers two buttons. She presses "I'm OK".
  - 06:40 is inside the real peak: filmed real-world falls clustered at **7–10 am and 7–10 pm** [T2, Vlaeyen 2013].
  - **India's elder helpline, Elderline 14567, runs 8 am–8 pm** [T5].
- **Cost:** the long lie.
  - **11 of 20** older people who lay on the floor for over an hour **died within a year** [T2, Wild et al., BMJ 1981].
  - **47%** of *uninjured* fallers couldn't get up after at least one fall [T2, Tinetti et al., JAMA 1993].

**Why she presses "I'm OK" (sourced):**
- In **80% (113/141)** of falls where an older person was alone and couldn't get up, **they didn't use the alarm they had**. **97%** of long lies happened to people who had an alarm and didn't press it [T2, Fleming & Brayne, BMJ 2008].
- One participant: *"I didn't want to use the call alarm, although I was wearing it, **for fear of being taken into hospital**."* [same]
- In a filial-piety culture, older adults conceal minor falls *"to avoid causing family worry"* [T2, Zhu et al. 2026, China]. India-specific evidence is the **open gap** (see §8 of the synthesis; track 9).

**Hook:**
> *"06:40. Amma's on the bathroom floor. Her watch gives her two buttons: 'I'm OK', or 'call an ambulance'. She presses 'I'm OK', because every Indian mother does. India's elder helpline doesn't open till 8."*

## 2. The traps

### 2.1 The Theek Hoon Trap (the hero), redefined by the research
- **Naive:** fall → prompt → "I'm OK" ends it; anything else becomes a siren, call centre or ambulance.
- **Why it's confidently wrong:** the device offers **only two exits**, and the one that keeps her dignity is "I'm OK". Evidence:
  - **Vendor docs:** Samsung (60 s alert; cancel ends it; fall detection off by default), Apple ("I'm OK" or Close dismisses it), Google Pixel ("I'm OK" dismisses it; **no Indian language**), and pendants (*"you say you are fine, and that is the end of it"*) [T1].
  - **Apple's own patent:** *"not transmit the alert if a response to the prompt is received"*, where the response is *"a touch input"* (US12100282B2, claim 11) [T3].
  - **Real families:** after an ambulance came for a false alarm, a mother *"is very angry over the intrusion and now refuses to wear her necklace"* [T4].
- **📂 It's in our repo:** `orchestrator.py:111` resolves on `parent_says_okay`. That's Naive mode, kept behind a flag for the demo.
- **Beaten by:** the **third option** (PEELA) plus the **Do-Check** plus the **Get-Up Vote** (L4).

### 2.2 The Moving-Arm Trap 🆕
- **Naive (Apple):** *"If your Apple Watch detects that you're moving, it waits for you to respond and won't automatically call."* [T1]
- **Why it's wrong:** in filmed real falls, *"the postfall phase was not characterized by inactive participants"* [T2, Vlaeyen 2013]. Waving, rocking and trying to rise all count as "moving". **Moving isn't standing.**
- **Beaten by:** V2 (back to her own pre-fall height) and V3 (walking cadence), not "any movement".

### 2.3 The Charger / Cry-Wolf Trap
- **Naive:** no signal means danger; every trigger goes public.
- **Why it's wrong:** watches get dropped, charged or banged in sleep, and each false alarm burns credibility: *"Samsung has made me infinitely LESS SAFE!… my contacts will ignore it due to too many false alerts."* [T4]
- **Beaten by:** fall/drop split + on-wrist + charging + the 360° spin rule → **GREY**. No push on GREY or HARA, and **never an auto-dial to emergency services** (§4).

## 3. Positioning

**Category shift:** *Everyone does detect → alert. We do verify → commit → stay.*

**The novelty sentence (narrow and defensible; say exactly this):**
> *"Others detect falls, check the watch is worn, listen for groans, even cancel the alert when a camera sees you stand. We're the first we've found to check her **answer**: we ask her to do something, and let her body vote."* [T3, T6]

**Positioning vs. India's biggest player:**
> *"India built the response teams. Nobody built the judgement. Suraksha decides when to call them, and who."* [T5]

### Competitor table v4 (behaviour verified in research)

| Who | After a fall | Gap Suraksha fills | Source |
|---|---|---|---|
| **Samsung Galaxy Watch** | 60 s alert; cancel ends it; SOS text to contacts; **off by default** | No verification; binary | [T1] |
| **Apple Watch** | "I'm OK" / Close dismisses; auto-calls only if **immobile ~1 min** | Moving-Arm Trap; binary | [T1, T3] |
| **Google Pixel Watch** | ~30 s, then 60 s countdown; "I'm OK" dismisses; **no Indian language** | No Hindi; binary | [T1] |
| **US pendants** (MedicalAlert, Lifeline…) | A call-centre human; "say you're fine" ends it | The words decide | [T1] |
| **UnaliWear Kanega** (US) | Monitored watch, **$84.95/mo**; countdown-cancel; swappable batteries | Cancel-on-response | [T3, T5] |
| **Anvayaa** (India; 1.5 lakh seniors, 38 cities, as reported) | Its own senior watch + SOS → a human command centre; *"3-minute response"* | No public verification or conversation; its patent claim is unverified | [T5] |
| **Emoha / Samarth** (India) | A call-centre callback / daily human visits | Human-only judgement | [T1, T5] |
| **AGEasy Protec** (Antara/Max, ₹7,559) | Fall detection → notify caregivers | **2.1★**; 5–8 h battery; setup needs tech support | [T5] |
| **DrRing** (India, ₹5,999/yr) | Press the button → sequential family calls + WhatsApp | Press-only; phone-dependent; **500+ installs** | [T1, T4] |
| **Elderline 14567** (Govt) | Helpline **8 am–8 pm**; not an emergency service | Closed at 06:40 | [T5] |
| **Thessai** (US startup) | Ambient motion sensors; routine-deviation alerts | Doesn't ask her | [T1] |
| *Hackathon:* **SafeStep** | Camera; **auto-cancels if it sees her stand**; "still on the floor" update | The person can still cancel; the body never questions her answer; camera in her room | [T6] |
| *Hackathon:* **Ally** (first place), **Pip**, **CarePilot** | "Are you OK?" → alert if no answer; code-decides tiers | The trap; tiers are hygiene, not novelty | [T6] |

## 4. Principles

> **"Her words are one vote."** The AI listens, speaks and explains. Code decides. No single signal closes a fall.

**Design principles (from the research):**
1. **Ask her first.** In her language, on her wrist.
2. **Offer a middle option.** *"Families already tell their mothers 'pressing it doesn't mean hospital, it means a little help.' We built that sentence into the watch."* [T4]
3. **Call the nearest person, not the siren.** *"They might want to contact a neighbour instead."* [T1, UAlberta]
4. **Suraksha never auto-dials emergency services.** It gets a person to commit; **112 is always on the family's screen**. [T4]
5. **A false trigger costs one private question, never a public event.** [T4]

**Hygiene (true, built, but not the headline):** code decides / the AI reads; colour tiers; Cedar consent; AWS services. These are now common in hackathon projects [T6].

## 5. Seven questions = pipeline = folder tree

```
Q1 Did something happen?           sense/     watch: fall vs drop, wake, on-wrist, charging       🔧
Q2 Real, or the Charger Trap?      verify/    drop · spin ≥360° · off-wrist · charging → GREY      🆕
Q3 What does she say?              voice/ + agents/companion (fall mode = short, templated)     ✅🔧
Q4 Can she show it?                getup/     Do-Check + Get-Up Vote + concern flags              🆕
Q5 How sure are we?                policy/tiers.py → HARA / PEELA / LAAL / GREY                    🔧
Q6 Who can arrive, and may they?   escalation/ + policy/consent   neighbour ∥ nearest child      ✅🔧
Q7 Stay with her.                  stay/      watch loop, ETA from the record, "still on floor"   🆕
```

**🔧 Rename the Python package `ally/` → `suraksha/`** (M6): a 2026 first-place hackathon winner in the same space is called "Ally" [T6].

---

## 6. Layer by layer

### L1 — sense/ (Galaxy Watch4) 🔧
- **Hardware (confirmed, Samsung spec):** accelerometer, **barometer**, gyro, geomagnetic, light, BioActive (PPG). **5ATM + IP68.** Battery **361 mAh (44 mm)** / 247 mAh (40 mm); LTE variant available [T7]. **Use the 44 mm model.**
- **One brain (#1):** fall → `suraksha` only; remove the `EmergencyClient` `/ws` fall path.
- **Fall vs. drop (#2):** free-fall ≥ 80 ms below 3 m/s² → impact above 18 m/s², **with PPG contact** → `fall`. Otherwise `drop`.
- **Sensors:** `TYPE_PRESSURE` (1 Hz idle, 5 Hz after a fall), `TYPE_STEP_DETECTOR`, gyro and magnetometer (spin rule), `BatteryManager` charging. `TYPE_LOW_LATENCY_OFFBODY_DETECT` (API 26+) only **if Watch4 exposes it** 🔬; otherwise PPG contact.
- **Foreground service (#10, S6):** `android:foregroundServiceType="health"`, permission `FOREGROUND_SERVICE_HEALTH`, prerequisite **`HIGH_SAMPLING_RATE_SENSORS`** (📂 already declared). **Heart rate is read only after a fall** (app foregrounded by the alert), so the core path never depends on `BODY_SENSORS_BACKGROUND` [T7].
- **Fall payload:** `{kind, impact_ms2, freefall_ms, spin_deg, p_ref_hpa (median of 10 s before), on_wrist, charging, t}`. Then stream `{p_hpa, step_events, accel_var, hr}` every 2 s for `GETUP_WINDOW_S`.
- **Charge window (#32, M9):** charge during her **morning bath or breakfast**, never overnight. Nocturia is a recognised night risk [T2], and 06:40 sits inside the observed 7–10 am peak.

### L2 — verify/ 🆕
- **GREY** if any of: `drop`; **spin ≥ 360° during the impact window** (Philips' expired rule; gyro/magnetometer) [T3]; `on_wrist=false`; `charging=true`. Message: *"Can't tell: watch off wrist since 07:10."* **No push.**
- **Device heartbeat (S3, from SafeStep):** the watch posts every 5 min; a missing heartbeat during wear hours → GREY on the family view. *"Silence never looks like safety."* [T6]
- **Off-wrist at an unusual hour (#22):** longer than her usual bath → a gentle ask **to her first**.

### L3 — voice / companion, fall mode 🔧
- **Understands** Hindi, English, Kannada, Tamil, Telugu, Marathi, Bengali and more (Transcribe streaming in us-east-1). **Speaks** Hindi and English only (Polly **Kajal**, generative → neural fallback ✅; Arjun and Kiara available) [T7].
- Status sentences are **templates from the record** (#9); the LLM writes only the comfort sentence.
- The first question is **cached audio** (no TTS wait) (#38).

### L4 — getup/: Do-Check + Get-Up Vote 🆕

**Step 1 — ask.** *"Amma, aap theek hain?"* ("Amma, are you okay?")

**Step 2 — the Do-Check, when she says she's fine (follows NHS fall guidance, S4).**
> *"Achha. Agar dard nahi hai, toh aaram se uthiye aur darwaze tak chaliye. Agar dard hai, toh bilkul mat uthiye, wahin rahiye, main madad bula rahi hoon."*
> ("Okay. If there's no pain, get up slowly and walk to the door. If it hurts, don't get up at all. Stay there, I'm calling for help.")

That matches NHS: *"check for any pain or injuries and see if you think you can get up"*; call for help if someone *"cannot get up"*. And AARP: *"If something hurts as you move, it is best to remain on the floor."* [T2]. **Never tell an injured person to stand.** Staying down only picks the tier.

**Mobility aids (#28):** walker → a lower stride band; wheelchair → `p_ref` = seated height, V3 abstains.

**Step 3 — vote**, within `GETUP_WINDOW_S` (180 s real; 40 s stage, disclosed on camera).

| Voter | Votes "up" when | Abstains when | Evidence |
|---|---|---|---|
| **V1 Words** | `parent_says_okay` ∧ ¬`parent_reports_unwell` | — | — |
| **V2 Height** | Pressure within **0.03 hPa of `p_ref`**, held 15 s, low arm variance 🔬 | No barometer | Massé 2014: a barometer separates sit from stand at 99.5%; Bianchi 2010; wrist: Jatesiktat 2017 [T2] |
| **V3 Movement** | ≥ 6 step-detector events **or** ≥ 6 strides at 0.5–2 Hz | Sensors missing | Moving-Arm Trap: *walking*, not "motion" |
| **V4 Voice** | A ≥ 4-word reply; rate ≥ 60% of her baseline; no pain words | Reply < 4 words | Prior art: Philips US11800996B2 (different method) [T3] |

**Concern flags** (raise only): HR > 130 or < 45 for 20 s; SpO₂ < 90%; PPG lost after the fall; pain words.

**Decision (code):**
- **Abstain = "not up".**
- **HARA:** V1 ∧ ≥ 2 of {V2, V3, V4} ∧ no flag → **nobody is messaged**.
- **PEELA (the third option):** V1 but the body doesn't agree → she hears *"Theek hai Amma, aapki baat maan li. Bas Priya ko bol rahi hoon ek baar call kar le."* ("Okay Amma, I believe you. I'm just asking Priya to call you once.") Priya gets *"Please give Amma a call when you can"*, with no health detail (#20). **The loop closes (#29):** "Spoke to her ✓" / "No answer"; no answer or no tap in 10 min (30 s on stage) → LAAL.
- **LAAL:** ¬V1, silence 30/90 s, any flag, or Do-Check silence.
- **GREY:** from L2.

**Worked example (hero case):** free-fall 140 ms, impact 31 m/s², no spin, on-wrist. "Theek hoon" (V1 ✓). Do-Check: pressure stays 0.09 hPa above `p_ref` (V2 ✗); 0 steps (V3 ✗); no ≥ 4-word reply (V4 abstains = ✗); she waves an arm (Apple would wait). HR 104, below the flag. → **PEELA.** Naive → resolved.

**Cost asymmetry (#21):** a false HARA means a long lie (never acceptable); a false PEELA means one phone call; a false LAAL means panic (kept low via GREY).

### L5 — tiers 🔧
The fall path's tier comes **only** from L4. The LLM judge stays for non-fall cases (late wake, words that sound unwell) as one input.

### L6 — who can arrive ✅🔧
- ✅ Step Functions chain with callbacks and failsafe.
- 🆕 **Fall pre-consent → neighbour in parallel (#30):** *"gir jaaun toh Sunita ko pehle bulana"* ("if I fall, call Sunita first") → a fixed-template Cedar `permit` with `context.reason == "fall"`. A LAAL fall asks **Sunita ∥ nearest child**; first to accept is "the one coming". 📂 Today `steps.py:158` asks the neighbour last.
- 🆕 **Nearest-First** ordering (same city, then past acceptances); called "adapts", not "learns".
- 🆕 **Amazon Connect call** if a LAAL push isn't accepted in 45 s (ported from `backend/`).
- 🆕 **Backup reminder (S3):** if nobody accepts in 2 cycles, re-ping everyone with *"still on the floor"*.
- **🔒 Never auto-dials emergency services (M7).** 112 is shown prominently on every family screen.
- ✅ Cedar: safety isn't forbiddable; PEELA carries no health detail.

### L7 — stay/ 🆕
Every 60 s, a haptic and then max volume: a templated status from the record (*"Main yahin hoon. Priya 20 minute mein pahunch rahi hai."* = "I'm right here. Priya will be there in 20 minutes."). The family view shows **"still on the floor"** while V2/V3 say down (S3). It ends only on **Arrived**; no Arrived by ETA + 15 min → *"Still coming?"* and the chain re-opens (#31).

---

## 7. What the AI is never allowed to decide
1. Resolve a fall. Only the L4 vote or a human "Arrived" can.
2. Cancel or downgrade an escalation.
3. **No False Comfort:** status lines are templates from the record.
4. Write Cedar ✅.
5. Answer family Q&A beyond tool records ✅.
6. **Dial emergency services.** Suraksha never does this on its own.

**Floor Invariant:** after a fall, no event sequence lowers the tier or reaches RESOLVED without (V1 ∧ ≥ 2 body votes ∧ no flag) or a human "Arrived". Hypothesis through the real orchestrator with injected faults; 1,000 seeded cases in CI (#39).

## 8. Degradation ladder

| Breaks | Still happens |
|---|---|
| Bedrock | Hindi templates; L4 unchanged; `llm_unavailable` shown |
| Transcribe | Watch buttons feed V1; V4 abstains |
| Push ignored | Connect call at 45 s → next contact → backup reminder |
| No network | On-watch vote + cached audio → tier on the watch + loud alarm; events queued |
| Off wrist / dropped / no heartbeat | GREY; ask her first |
| Step Functions error | Failsafe notifies all ✅ |

**Venue:** personal hotspot plus a backup video. Never claim "offline".

## 9. Proof

### 9.0 First hour on the watch (S10) 🔬 — before any Kotlin
| Check | How | Time |
|---|---|---|
| Off-body sensor present? | `getDefaultSensor(TYPE_LOW_LATENCY_OFFBODY_DETECT)` | 5 min |
| **Barometer noise at the wrist** | 10 min still + sit/stand cycles at 5 Hz → std dev, stand-vs-floor delta | 30 min |
| Battery %/h, armed | Log every 30 min for 8 h | passive |
| Step-detector latency | 10 steps, timestamps | 10 min |
| Bathroom audibility | Cached Kajal audio at max volume, door shut | 5 min |

### 9.1 Wear test (#33) — run first
Two teammates, ≥ 16 h each. **Pass bar: ≤ 1 false `fall` trigger per 40 waking hours** (the Kangas 2014 real-world benchmark [T2]). **Report nights separately** (S5): the Samsung night false-trigger reports [T4].

### 9.2 Traces (#36)
60 traces (36 dev / 24 held-out); controlled falls onto a firm mat; 60 s streams. The held-out set is sealed by its owner.

| Class | Dev | Held-out |
|---|---|---|
| Fall → gets up + walks | 8 | 5 |
| Fall → stays down, "theek hoon" (+ arm waving) | 8 | 5 |
| Fall → silent | 4 | 3 |
| Hard sit on the sofa | 5 | 4 |
| Watch dropped / charger / spun | 6 | 4 |
| Daily noise | 5 | 3 |

### 9.3 Baselines and metrics (`eval/metrics.py` → `metrics.json`)
- **Baselines:**
  - **B0** cancel-on-response (documented vendor behaviour [T1]).
  - **B0′** Apple-style immobility rule (alert only if no motion for 60 s).
  - **B1** a sceptical Nova judge on her words.
  - **B2** steps-only.
- **Metrics:** trap catch rate; got-up correctly HARA (no nag); false LAAL per drop/noise trace; Floor Invariant violations / N; false triggers per wear-day and per wear-night; box → armed onboarding time.
- **Ablation:** drop V2, V3 and V4 one at a time.

### 9.4 Latency budget (#38)
Fall → first question < 1.5 s · reply → Do-Check < 4 s · LAAL → judge's phone < 3 s. All measured.

**Known context to cite (not our numbers):**
- Real-world fall detectors: **57% average sensitivity, 3–85 false alarms a day** (Bagalà 2012).
- **1 false alarm per 40 h** at best (Kangas 2014) [T2].

## 10. Demo (3:00)

| Time | Beat |
|---|---|
| 0:00–0:10 | **Cold open:** *"Haan beta, main theek hoon. Tum kaam karo."* ("Yes dear, I'm fine. You go to work.") Title: *"Every Indian mother says this. Even from the floor."* |
| 0:10–0:30 | **Trap, live, in Naive mode (our own old code).** A teammate falls on the mat, says "theek hoon", **waves an arm**, stays down. Board: **HARA "Resolved"**. *"That's how watches work today. Apple's own patent says so."* Flash **US12100282B2 claim 11** for 3 s (S9) |
| 0:30–1:05 | **Suraksha, same fall:** "theek hoon" → conditional Do-Check (*"if it hurts, stay there"*) → stays down → lamps: Words ✓, Height ✗, Movement ✗ (arm waving doesn't count), Voice — → **PEELA**. Judge-as-Priya gets *"Please give Amma a call."* |
| 1:05–1:20 | **It stays quiet:** she gets up and walks → **HARA**, nobody messaged |
| 1:20–1:55 | **Red:** silent fall → **LAAL** → Sunita and Priya asked **in parallel** → the judge taps *"On my way, 20 min"* → the watch: *"Priya aa rahi hai. Main yahin hoon."* ("Priya is coming. I'm right here.") Board: *"still on the floor"*. Reveal: *"I switched the AI off before that one."* And: *"Notice what it didn't do: it never called an ambulance on its own."* |
| 1:55–2:15 | **Two-tier lines:** drop the watch on the table → **GREY**, no push (the spin rule); *"she can speak Kannada to it"*; *"every other day it's a quiet companion"* |
| 2:15–2:40 | **Proof card** from `metrics.json`. **Caveat first:** *"acted falls by us; stage windows shortened."* Plus Fleming: *"4 in 5 who couldn't get up didn't press their alarm."* |
| 2:40–3:00 | **Close:** *"Her words are one vote. Not a medical device. 112 is always on the family screen."* |

**Fallbacks:** a REPLAY button (labelled), a backup video, a hotspot.

## 11. Spectator layer 🆕
- **The Live board:** sensor strips (accel, pressure vs. `p_ref`, HR, steps, heartbeat), V1–V4 lamps + flags, the tier, the chain with ETA, the "still on the floor" badge, the Naive toggle, AI-off, REPLAY, the QR code.
- **Transport:** 1 s polling of `GET /suraksha/live/<session>`, plus a warm-up pinger (#37).
- **`/join/<demo-session>`:** no login; first tap wins (#43).
- **One architecture strip; no wall of AWS logos (N7).**

## 12. Rubric mapping
Generic until `00_RULES.md` exists:
- **Impact** → §1 (sourced).
- **Novelty** → §2–3 + the novelty sentence.
- **Depth** → L4, the Floor Invariant, wear test + held-out set, Cedar, Step Functions.
- **Working product** → spine + wear-test pass + 10/10 mat fire rate.
- **Demo** → §10.
- **Sponsor tech (AWS)** → Bedrock, Transcribe, Polly, Step Functions, Connect and DynamoDB are load-bearing.

## 13. Challenge → answer

| Challenge | Answer |
|---|---|
| "Isn't this Samsung or Apple fall detection?" | "Same watch class. Their own docs and Apple's patent say 'I'm OK' ends it. We check her answer." |
| "Isn't it just a confirmation step?" | "A confirmation step asks her. Ours asks her body." |
| "Hasn't someone detected recovery already?" | "Yes: Apple claims it from motion, SafeStep with a camera. Neither uses it to question her *answer*, and neither gives her a third option." |
| "You told an injured woman to stand?" | "Never. The Do-Check follows NHS guidance: if it hurts, stay where you are." |
| "Is the barometer real at the wrist?" | "It's on Watch4's spec sheet. It separates sit from stand at 99.5% in the literature; at the wrist we measured our own noise floor: [number]. One vote of three." |
| "What if it's wrong?" | "False PEELA = one phone call. False LAAL is kept low by GREY. We never dial an ambulance on our own." |
| "Real-life false alarms?" | "Our wear test: [N] triggers in [H] hours, nights reported separately. The published best is 1 per 40 hours." |
| "Night falls?" | "Charging moves to her morning bath. Video studies put the peak at 7–10 am and 7–10 pm, which is why our story is 06:40." |
| "Why a Galaxy Watch?" (N1) | "Indian senior watches are 2.1–3.5★ with 5-hour batteries. We put the intelligence in software on mainstream hardware." |
| "Kannada?" | "She can speak Kannada to it; it answers in Hindi or English for now. Polly has no Kannada voice." |
| "Who pays?" (N2) | "Children (often abroad), employers as a benefit, response networks like Anvayaa as partners." |
| "Privacy?" (N3) | "Pip records her whole day; SafeStep puts a camera in her room. Our mic opens only after a fall, and conversations are never shared." |
| "Is any of this patented by others?" (N6) | "Nearby: Apple (motion-based recovery), Philips (audio after a fall), Alarm.com (wear check). Different mechanisms. We'd need an FTO review before a launch." |
| Lineage (N4) | "Height-plus-time-on-floor is a 2005 patent, now expired; Philips' spin rule is expired too. We built on that and pointed it at her answer." |
| "Why us-east-1?" (N5) | "Polly's generative voices aren't in Mumbai; Singapore is the nearest alternative." |
| "What's simulated?" | Pre-today history (labelled), acted falls, the demo phone number, shortened stage windows. |
| "Dementia?" | "Not designed for it. No answer to the Do-Check fails safe to red." |

## 14. Considered and rejected
- Cameras / Wi-Fi / radar (crowded, privacy) [T6].
- A phone-only app (not on her body in the bathroom) [T5].
- An LLM deciding "is she okay".
- Broadcasting to everyone.
- HR as an "up" voter.
- An absolute barometer threshold.
- Web Push for judges.
- **Auto-dialling 112.**
- Scam-shield pivot (crowded) [T6].
- 3D world, sim-service, post-discharge flow.

## 15. What this is NOT
- Not a medical device; not an emergency service; **never auto-dials 112** (shown on screen).
- Not surveillance: the mic opens only after a fall, a tap or a check-in.
- Not validated with elderly users (none of 118 fall-detection studies were either [T1]; we say it first).
- Not for dementia. Not offline-first.
- Speaks Hindi and English only (understands more).
- **Not cleared for commercial launch:** nearby active patents (Apple claim 12, Philips US11800996B2, Alarm.com US12198525B2) need a freedom-to-operate review [T3].

## 16. Keep / change / build / cut

| Keep ✅ | Change 🔧 | Build 🆕 | Cut ✂️ |
|---|---|---|---|
| Agents, store, policy, escalation, tests | **Rename `ally/` → `suraksha/`** | `getup/` (Python → Kotlin) | `experience/` + copyrighted mp3s |
| `infra/` CDK (IAM already covers the Nova inference profile [T7]) | `orchestrator.py:111` → L4 (Naive behind a flag) | `verify/` incl. the **spin rule** + **heartbeat** | `sim-service/`, `dashboard/` |
| `AudioBridge`, step/vitals readers | `FallDetector` → fall/drop split | Do-Check (NHS wording) | `backend/` after the Connect port |
| Cedar + audit | `RakshakViewModel` → one brain | Barometer, step detector, charging | Unused web routes |
| Polly generative → neural fallback ✅ | Tiers → 4 colours | **Health foreground service** | Live URLs in READMEs |
| | `/command` → Live board | `stay/` + "still on the floor" | |
| | | Neighbour ∥ child, Connect call, backup reminder | |
| | | `/join`, REPLAY, AI-off, Naive toggle | |
| | | `eval/` traces, wear test, `metrics.py`, B0/B0′/B1/B2, ablation | |
| | | Minimal onboarding (44 mm watch, charge window, fall pre-consent) | |

## 17. Build map

| # | Ticket | Pri | Blocked by | Done when |
|---|---|---|---|---|
| 0 | **First-hour watch checklist (§9.0)** | CORE | — | 5 measurements logged |
| 1 | One brain + rename to `suraksha` | CORE | — | One conversation on the watch |
| 2 | Fall/drop split + spin rule + on-wrist/charging | CORE | 0, 1 | Desk drop or spin → `drop`; mat fall → `fall` |
| 2a | **Wear test** starts | CORE | 2 | ≥ 32 h logged, nights separate |
| 3 | Barometer `p_ref` + post-fall stream | CORE | 0, 1 | A trace JSON per fall |
| 4 | `getup/vote.py` + flags + table tests | CORE | — | The §6 example → PEELA |
| 5 | Do-Check (NHS wording) + replace `:111` (Naive flag) | CORE | 4 | Trap case not resolved; 55 tests pass |
| 6 | `verify/` GREY + heartbeat | CORE | 2 | 0 LAAL on drop/spin/charger traces |
| 7 | 4-colour tiers + templated status | CORE | 4 | Colours on the watch and the family view |
| 8 | Live board + `/join` + Naive toggle + REPLAY + `/live` polling | CORE | 7 | A stranger's iPhone joins as Priya |
| 9 | PEELA loop close | CORE | 7 | No answer → LAAL |
| 10 | Traces + held-out sealed | CORE | 3 | §9.2 counts; mat fire 10/10 |
| 11 | `metrics.py` + baselines + ablation | SUPPORTING | 4, 10 | Proof card from JSON |
| 12 | Floor Invariant (Hypothesis) | SUPPORTING | 5 | N cases, 0 violations |
| 13 | Stay loop + ETA + "still on the floor" | SUPPORTING | 7 | Spoken every 60 s |
| 14 | Neighbour ∥ child (fall pre-consent) | SUPPORTING | 7 | Both asked at once |
| 15 | Health foreground service | SUPPORTING | 1 | Sensors survive backgrounding |
| 16 | AI-off switch | SUPPORTING | 8 | Same tier with Bedrock "down" |
| 17 | Connect call + backup reminder | SUPPORTING | — | A real call to the demo number |
| 18 | On-watch vote + cached audio | SUPPORTING | 4 | Tier in airplane mode |
| 19 | Minimal onboarding | SUPPORTING | 14 | Box → armed in < 3 min |
| 20 | Latency + battery tables | SUPPORTING | 1 | §9.4 filled |
| 21 | Transcribe-down buttons; Nearest-First | STRETCH | — | — |

**Spine:** 0 → 1 → 2 (→ 2a starts) → 3 → 4 → 5 → 7 → 8 → 9.

## 18. Honesty inventory

| Component | Really is | Say on camera |
|---|---|---|
| Fall detection | A deterministic accelerometer rule (+ spin rule from an expired Philips patent) | "Classic free-fall + impact" |
| Do-Check + vote | Deterministic; wording follows NHS guidance | "Code decides; NHS-style wording" |
| V1 words | Nova structured output | "One vote" |
| Eval falls | Acted by us | Said **before** the number |
| Windows | 40 s stage / 180 s real | Said |
| Phone call | A real Connect call to our number | Said |
| Competitor behaviour | From their own support docs and patents | "Their docs say…" |
| Anvayaa figures | Company claims, unaudited | "Anvayaa reports…" |

## 19. Roles
- **Watch owner:** tickets 0, 1, 2, 3, 15, 18.
- **Brain owner:** tickets 4, 5, 6, 9, 12, 13, 14.
- **Show owner:** tickets 7, 8, 16, 19, the pitch, the backup video.
- **Held-out owner:** ticket 10 + the wear-test log (2a).

## 20. Key numbers by heart

**Sourced (say them with the source):**
- **80%** of alone, can't-get-up falls → alarm unused (BMJ 2008).
- **97%** of long lies had an unused alarm (same).
- **11 of 20** who lay over an hour died within a year (BMJ 1981).
- **47%** of uninjured fallers couldn't get up (JAMA 1993).
- **27.6%** fall rate for Indian women living alone (LASI).
- Elderline **8 am–8 pm**.
- Real-world detectors: **3–85 false alarms a day**; best **1 per 40 h**.

**Ours (from `metrics.json` only):** trap catch rate vs. B0/B0′/B1, no-nag rate, false LAAL, Floor Invariant N, held-out n, mat fire rate, wear-test triggers per day and per night, the barometer noise floor.

## 21. One-paragraph pitch
After a fall, every watch gives an older parent two buttons: "I'm OK", or "call an ambulance". In a landmark study, four out of five people who couldn't get up never pressed for help, one *"for fear of being taken into hospital."* Suraksha, on a Galaxy Watch, gives her a third option. It believes her out loud, asks her to show it ("if there's no pain, walk to the door"), and lets her barometer, steps and voice vote. If her body disagrees, it quietly asks her daughter to call. If she's down, it asks her neighbour and her nearest child at once, rings them if they miss it, and keeps talking to her in Hindi until someone walks in. It never calls an ambulance on its own. Most days it says nothing at all.

## 22. Glossary
- **Theek Hoon Trap:** the two-exit design that makes "I'm OK" the only dignified choice.
- **Moving-Arm Trap:** "moving" read as "fine".
- **Charger / Cry-Wolf Trap:** no signal or false alarms that burn trust.
- **Third option / PEELA:** "I believe you; I'm asking Priya to call."
- **Do-Check:** the conditional, NHS-style ask to get up.
- **Get-Up Vote:** V1 words, V2 height, V3 movement, V4 voice.
- **Spin rule:** a watch spinning ≥ 360° means it was dropped, not a person.
- **HARA / PEELA / LAAL / GREY:** green / yellow / red / grey.
- **Floor Invariant.** **No False Comfort.** **Neighbour ∥ child.**

## Changelog
- **v1:** recentred on the Theek Hoon Trap.
- **v2:** 26 red-team fixes.
- **v3:** 17 round-4 fixes (NHS-safe Do-Check, PEELA loop, neighbour, wear test, onboarding…).
- **v4:** research tracks 1–8.
  - **MUST:** two-exit trap definition; all killer facts sourced; 80% re-attributed to Fleming 2008; a narrow novelty sentence; "code decides" demoted to hygiene; `ally` → `suraksha`; never auto-dial 112; language corrected (understands many, speaks Hindi/English); night claim corrected; barometer confirmed.
  - **SHOULD:** Moving-Arm Trap + demo beat; Philips spin rule; SafeStep borrowings (heartbeat, "still on the floor", backup reminder); NHS wording; wear-test bar (≤ 1/40 h, nights separate); health foreground service; 44 mm watch; competitor table v4; the Apple-patent beat; the first-hour watch checklist.
- **Open for v5:** track 9 conversations (India concealment evidence); on-watch measurements; the Firecrawl redo (Reddit, Anvayaa, Indian hackathons, Indian patents); the real rubric.
