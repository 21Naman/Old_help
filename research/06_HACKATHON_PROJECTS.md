# Track 6 — Hackathon projects (what everyone builds)

*26 Nov 2026. Status: **done, waiting for your review.***

*Method: Devpost's own search endpoint, through the built-in browser, across 6 queries × 3 pages ("fall detection", "elderly fall", "fall detection watch", "senior fall alert", "elderly safety wearable", "aging parents alone"). That gave **53 elder-care or fall projects**. Every project page was checked for a "Winner" badge (**5 winners**). Full write-ups read for 7 projects (Ally, Pip, Blissey Beacon, CarePilot, CareBridge, SafeStep, Threshold) plus Aama and elder-care-incident-guardian. GitHub repo search via `gh` (top fall-detection repos have 0–1 stars, so nothing to learn there).*

## The one-line finding

**Elder-care is a crowded hackathon theme, and several ideas we thought were ours are already common: "code decides, the AI only reads", severity tiers, "only page the family when it matters", camera auto-cancel when the person stands, native-language WhatsApp check-ins, routine-absence alerts.** What **no project** does is treat the person's *"I'm OK"* as unverified, ask her to *do* something, or offer a *middle tier* chosen by her body. Every fall flow we read still ends on her answer or a timeout.

---

## The 5 winners

| Winner | Event / prize | What it does | Fall flow | Lesson for us |
|---|---|---|---|---|
| **Ally** | Immerse the Bay 2026, **ManageXR first place** | Mentra camera glasses: whispers warnings in the senior's ear (scam calls, food allergens, schedule); the caregiver gets events, never footage | *"Fall check-in asks 'Are you okay?' after 'I've fallen', and **alerts family if there's no answer**."* | ⭐ **Same philosophy line as ours:** *"Claude only reads the words. Plain code makes every safety call."* That's not a differentiator any more. **Its fall flow is the trap.** **Name clash:** our backend package is also called `ally` (rename to `suraksha`) |
| **Pip** | VexoHacks AI Wearables, **Stripe third place** | A wristband with an always-on mic: transcribes her day, answers "did I take my pills?", freezes her card on scam talk, nightly family summary | *"A fall brings up a 'did you fall?' check that Margaret can answer by voice or by tapping the band, and Lisa is alerted."* | Voice-answerable fall check exists. **An always-on mic recording her whole day** is the opposite of our privacy stance (mic opens only after a fall, tap or check-in; conversations never shared) |
| **Blissey Beacon** | LA Hacks 2026, **Espressif "Best use of"** | ESP32 Wi-Fi sensing for camera-free fall monitoring; **a caregiver reviews the incident before family is contacted**; AI-written explanations | A human reviewer before escalation | A human in the loop as the middle layer. Ours puts *her own voice and body* as the first check, with no paid reviewer |
| **Y.P.I.A** | TigerHacks 2026, MLH ElevenLabs | Medication management for seniors living alone | — | Medication is the most common elder-care hackathon problem |
| **Kinding Quest** | Girls Who Code HHS | An empathy game | — | Not relevant |

## The non-winners worth knowing (closest to us)

| Project | What it does | How close | The difference |
|---|---|---|---|
| **SafeStep** (camera) | YOLO pose detects a fall; **"If SafeStep sees them stand back up, it cancels the alert automatically."** *"Still on the floor"* after 60 s; *"I'm on my way"* button; backup caregiver; camera heartbeat (*"silence never looks like safety"*) | ⭐⭐ **The closest project.** Body-based get-up detection plus an escalation chain, already built | **The person can still cancel within 30 s; the body only *cancels*, it never *questions* her answer.** It's camera-based (a bedroom camera). No conversation, no middle tier, no language. Our pitch must not say "first to check if she got up". It must say **"first to check her *answer*"** |
| **CarePilot** (AWS Strands + Bedrock) | Morning SMS check-in → structured signals → **ok / watch / alert / urgent**; *"a deterministic keyword floor… **The LLM gets a floor, not a veto**."* *"only page the family when it matters."* | ⭐⭐ The same stack and the same philosophy as our existing `ally/` code | Text check-ins, not falls; no sensors, no verification, no stay-with-her |
| **CareBridge** (AWS, WhatsApp) | *"WhatsApp AI checking on aging parents **in their native tongue**"*; cites 140M+ Indian seniors and *">90% app abandonment"* | ⭐ India + native language + AWS is taken as a *pitch* | WhatsApp text/voice notes; no wearable, no fall moment |
| **Threshold** (Ring cameras) | *"Ring tells you when something happens. **Threshold tells you when something doesn't**"*: routine-absence detection (no kitchen movement 7–9 am) | ⭐ Our late-wake investigation is a known idea | Cameras; no conversation |
| **elder-care-incident-guardian** (local NAS) | Local camera AI for falls and inactivity, *"multi-signal posture verification"*, SHA-256 evidence | Verification of *posture*, not of her words | Cameras, an evidence focus |
| **Aama** (Nepal) | Long-distance care for parents whose children work abroad: meds, SOS, caregiver coordination | The "children abroad" story is shared | No fall verification |
| A cluster of **Alexa+ / Ring / Bedrock "ambient OS"** projects (GuardianEcho, CareSentinel+, CareBridge Ambient OS, Nexus, OmniCare, CareLoop, Hearth, RoutineWatch) | Multi-agent home orchestration across Echo, Ring and wearables | — | **Buzzword stacking** (the Event-Horizon pattern in the blueprint). Avoid looking like these |

## What everyone builds (crowded)

| Pattern | Count (of 53) | Status for us |
|---|---|---|
| Scam / fraud shields for seniors | ~9 | Not our lane |
| Camera or Wi-Fi / mmWave fall detection (no wearable) | ~9 | Our watch choice is distinct; the privacy argument favours wearables over cameras |
| Alexa+ / Ring / Bedrock "ambient care OS" | ~9 | Avoid the look |
| Medication / pill management | ~6 | We have reminders ✅, but never headline them |
| "Are you OK?" fall check → alert on no answer | Ally, Pip, ElderPal, Salem, NIRA, Fall Guardian… | **This is the trap.** Every fall flow we read ends on her answer or a timeout |
| "AI reads, code decides" / severity tiers | Ally, CarePilot | **No longer a differentiator.** Keep it, but don't lead with it |
| Native-language check-ins (WhatsApp/SMS) | CareBridge, CarePilot | Language alone isn't the USP |

## What nobody built (across 53 projects)

1. **Verifying the "I'm OK".** Every fall flow accepts it (or uses the body only to *cancel*, as SafeStep does).
2. **The Do-Check:** asking her to *do* something, safely, and reading the sensors.
3. **The middle tier chosen by her body** ("I believe you, I'm just asking Priya to call").
4. **Neighbour pre-consented for falls, asked in parallel.** SafeStep has a "backup caregiver"; nobody has a neighbour-first rule.
5. **Staying with her on the wrist until someone arrives,** with an ETA relayed from the record. Projects alert and stop.
6. **A mainstream smartwatch with a barometer** as the sensor. Projects use cameras, Wi-Fi, ESP32s, Mentra glasses or custom bands; none uses the barometer for a get-up check.

## What this changes for Suraksha (proposals; nothing edited until you agree)

1. **Demote "code decides / AI only reads / tiers" from USP to hygiene.** Two recent projects say the same words (Ally won first place with it). Lead with the **Do-Check + verifying her answer + middle tier**.
2. **Sharpen the novelty sentence again**, adding SafeStep: *"Others detect falls and even cancel the alert when the camera sees you stand. We're the first we've found to check her **answer**, by asking her to do something and letting her body vote."*
3. **Rename the backend package from `ally` to `suraksha`** before any demo. A 2026 first-place winner is called "Ally" in the same space, and judges may have seen it.
4. **Borrow from SafeStep (cite it as hackathon prior art):** the *"still on the floor"* status update, a backup-caregiver reminder, and a device heartbeat (*"silence never looks like safety"*). These match our GREY rule and the stay loop; the heartbeat is a cheap addition to L2.
5. **Avoid the "ambient OS" look:** no slide with 8 AWS logos in a row. One architecture strip, with the trap as the headline.
6. **The privacy contrast for Q&A:** *"Pip records her whole day; SafeStep puts a camera in her room. Suraksha opens the mic only after a fall, and never shares what she says."*

## Sources (Devpost)

- [Ally (Immerse the Bay 2026, ManageXR first place)](https://devpost.com/software/ally-5nkvhi)
- [Pip (VexoHacks, Stripe third place)](https://devpost.com/software/pip-wufocr)
- [Blissey Beacon (LA Hacks 2026, Espressif)](https://devpost.com/software/blissey-beacon)
- [Y.P.I.A (TigerHacks 2026)](https://devpost.com/software/ypia)
- [SafeStep](https://devpost.com/software/safestep-g1o8qj)
- [CarePilot](https://devpost.com/software/carepilot-lhctxd)
- [CareBridge](https://devpost.com/software/carebridge-56zhrl)
- [Threshold](https://devpost.com/software/threshold-pattern-absence-detection-for-elderly-care)
- [elder-care-incident-guardian](https://devpost.com/software/elder-care-incident-guardian)
- [Aama](https://devpost.com/software/aama)
- Plus 43 other project pages scanned for winner status and tagline (list reproducible from the Devpost search queries above)
- GitHub: `gh search repos "fall detection elderly" --sort stars` (top results have 0–1 stars)

## Couldn't confirm

- **Devpost search coverage.** 6 queries × 3 pages isn't every project; "winner" detection relies on the badge text on each page.
- **SIH, Unstop and Reskilll showcases** (Indian hackathons) weren't searched, because they aren't reachable through the same kind of endpoint. Worth a pass if the target event is Indian.
- **Whether the judges at *your* event have seen SafeStep/Ally/CarePilot.** Unknown; the safest assumption is yes.
