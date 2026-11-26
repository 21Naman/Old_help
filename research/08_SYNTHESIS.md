# Track 8 — Synthesis: what the research says, and what changes

*26 Nov 2026. Status: **done, waiting for your review.** This file combines tracks 1–7. Track 9 (real conversations) is yours.*

*Inputs: [01 How fall detection behaves](01_HOW_FALL_DETECTION_BEHAVES.md) · [02 Research papers](02_RESEARCH_PAPERS.md) · [03 Patents](03_PATENTS.md) · [04 User complaints](04_USER_COMPLAINTS.md) · [05 India landscape](05_INDIA_LANDSCAPE.md) · [06 Hackathon projects](06_HACKATHON_PROJECTS.md) · [07 Hardware and stack](07_HARDWARE_AND_STACK.md). That's about 46 proposals across the seven tracks, merged and de-duplicated below.*

---

## 1. The verdict in one paragraph

**The trap is real, and it's real at every level we looked:** in the vendors' support docs (Samsung, Apple, Google and pendant call centres all end on "I'm OK"), in Apple's granted patent claim (*"not transmit the alert if a response to the prompt is received"*), in a BMJ cohort (alarms unused in 80% of can't-get-up falls; *"for fear of being taken into hospital"*), in caregiver forums (*"refuses to wear her necklace"* after an ambulance came for a false alarm), and in 53 hackathon projects (every fall flow still ends on her answer or a timeout). **The research also changed what the trap *is*.** It isn't mainly that mothers lie. **Every product gives her two choices, "I'm OK" or "ambulance", and an embarrassed, independent person will choose "I'm OK" every time.** Suraksha's job is to be the **third option**, and then to check whether her body agrees.

## 2. The trap, restated with evidence

> **The Theek Hoon Trap (v4):** after a fall, every device offers two exits, **"I'm OK" (nothing happens)** or **"emergency" (siren, call centre, ambulance)**. People who are hurt but proud, scared of hospital, or unwilling to bother their children take the first exit, and the device believes them.

| Layer of evidence | The single best piece | Source |
|---|---|---|
| Products | *"The specialist comes on, you say you are fine, and that is the end of it."* | MedicalAlert.com (track 1) |
| Patent | Apple US12100282B2 claim 11: no alert *"if a response to the prompt is received"*, the response being *"a touch input"* | Track 3 |
| Science | 80% (113/141) of alone, can't-get-up falls: **alarm not used**; 97% of long lies had an unused alarm; *"for fear of being taken into hospital"* | Fleming & Brayne, BMJ 2008 (track 2) |
| Consequence | 11 of 20 people who lay on the floor over an hour died within a year | Wild et al., BMJ 1981 (track 2) |
| Real families | *"pushing the button DOES NOT MEAN… 'take me to the hospital'. It just means 'I NEED A LITTLE HELP'"* | AgingCare caregiver (track 4) |
| What false alarms do | *"Samsung has made me infinitely LESS SAFE!… my contacts will ignore it"* | Samsung Community (track 4) |
| Culture | Concealing minor falls *"to avoid causing family worry"* (filial-piety culture) | Zhu et al. 2026, China (track 2; India-specific evidence: **gap → track 9**) |

**Companion trap, the Moving-Arm Trap:** Apple calls automatically only if you're *immobile*; real filmed falls show people *moving* on the floor (Vlaeyen 2013). Movement isn't standing.

**Companion trap, the Charger/Cry-Wolf Trap:** a false alarm that becomes a public event teaches everyone to ignore the next one (Samsung, AgingCare).

## 3. What's crowded vs. what's empty

| Crowded (don't lead with it) | Evidence | Empty (lead with it) | Evidence |
|---|---|---|---|
| Fall *detection* itself | Apple, Samsung, Google, every pendant, about 20 hackathon projects | **Verifying "I'm OK"** | No product, patent or hackathon project found (tracks 1, 3, 6) |
| Checking the watch is worn / drop vs. fall | Philips 2007 (active JP), Alarm.com (active US), Philips 2008 spin rule (expired) | **Do-Check: asking her to *do* something** | No patent hit; no project (tracks 3, 6) |
| Recovery detection from motion | Apple claim 12 (behaviour model); SafeStep (camera auto-cancel) | **A middle tier chosen by her body** | All products and projects are binary (tracks 1, 4, 5, 6) |
| Listening to the voice after a fall | Philips US11800996B2 (groans, pain estimate) | **Neighbour pre-consented for falls, asked in parallel** | DrRing calls in order; SafeStep has a backup caregiver; nobody does neighbour-first (tracks 1, 5, 6) |
| "Code decides, AI only reads"; severity tiers | Ally (first-place winner), CarePilot | **Staying with her on her wrist until someone arrives** | Projects and products alert and stop (tracks 1, 6) |
| Native-language check-ins (WhatsApp/SMS) | CareBridge, CarePilot | **A mainstream watch's barometer used to check "is she up?"** | Barometer research targets fall *detection*; nobody points it at the *answer* (tracks 2, 3, 6) |
| Cameras / Wi-Fi / radar ambient sensing | About 9 projects; Thessai; Ring-based | | |
| Human response networks | Anvayaa (1.5 lakh seniors), Emoha, Samarth | | |
| Medication reminders, scam shields | About 15 hackathon projects | | |

## 4. Directions considered (with why and why not)

| # | Direction | For | Against | Verdict |
|---|---|---|---|---|
| **A** | **Suraksha as designed: verify → commit → stay, on a Galaxy Watch** | Lives in the empty column; the hardware already exists and the barometer is confirmed; we have the code spine; a strong trap with primary evidence | The wear-test false-trigger rate is unknown; the wrist barometer is thinly studied; Apple and Philips have nearby claims | ✅ **Go.** Every track supports it |
| B | Camera / Wi-Fi ambient fall detection | No wearable to forget | Crowded (about 9 projects, startups); privacy objection (track 4); bathrooms; no conversation | ❌ Reject |
| C | Phone-only app (no watch) | Cheapest; everyone has a phone | *"A phone on a charging stand in the bedroom is no use in the bathroom"* (Emoha); the DrRing review on phone dependency | ❌ Reject |
| D | A daily WhatsApp/SMS check-in companion (CarePilot/CareBridge style) | Easy to build; habit-forming | Crowded; no answer for the 06:40 moment | ➖ Keep only as **supporting daily value** (morning check-in ✅ already built) |
| E | B2B decision layer for response networks (sell to Anvayaa/Emoha) | Turns the biggest competitor into a channel; real business | Not demoable on stage on its own | ➖ Keep as **one Q&A line**, not the demo |
| F | Pivot to scam protection for elders | A hot topic | Very crowded (about 9 projects); off our hardware and trap | ❌ Reject |

**Recommendation: A, with D as supporting daily value and E as the business answer.**

## 5. The pitch, rebuilt from evidence

**Hook (06:40):**
> *"06:40. Amma's on the bathroom floor. Her watch asks if she's okay. It gives her two buttons: 'I'm OK', or 'call an ambulance'. She presses 'I'm OK', because every Indian mother does. India's elder helpline doesn't open till 8. In a classic study, more than half the people left on the floor over an hour were dead within a year."*
*(Sources: Samsung/Apple/Google docs; Elderline 8 am–8 pm; Wild 1981, 11 of 20.)*

**Category shift:** *Everyone does detect → alert. We do verify → commit → stay.*

**The novelty sentence (narrow and defensible):**
> *"Others detect falls, check the watch is worn, listen for groans, even cancel the alert when a camera sees you stand. We're the first we've found to check her **answer**: we ask her to do something, and let her body vote."*

**The third-option line:**
> *"Families already tell their mothers, 'pressing it doesn't mean hospital, it means a little help.' We built that sentence into the watch."*

**Positioning against the biggest Indian player:**
> *"India built the response teams. Nobody built the judgement. Suraksha decides when to call them, and who."*

**Proof slide candidates (all sourced):** Apple's claim 11 quote · Fleming's 80% / 97% · *"for fear of being taken into hospital"* · our own held-out numbers (to be measured).

**Hygiene, not headline:** code decides / AI reads; tiers; Cedar consent; AWS services. Say them in the architecture strip and in Q&A.

## 6. Consolidated changes for bible v4 (merged from 46 proposals)

### MUST (change the story or fix a factual error)

| # | Change | From track |
|---|---|---|
| M1 | **Redefine the Theek Hoon Trap** as the two-exit problem ("I'm OK" vs. ambulance); PEELA is "the third option" | 1, 2, 4 |
| M2 | **Replace every UNVERIFIED killer fact** with sourced ones: Fleming 80% / 97% + quote; Tinetti 47%; Wild 11/20; LASI women living alone 27.6%; Bagalà 3–85 false alarms a day; Elderline 8–8 | 1, 2, 5 |
| M3 | **Fix the 80% attribution** (Fleming BMJ 2008, not the UAlberta paraphrase) | 2 |
| M4 | **Narrow the novelty claim** to the sentence in §5; never claim barometer fall detection, wear checks or recovery detection as new | 3, 6 |
| M5 | **Demote "code decides" and tiers** from USP to hygiene | 6 |
| M6 | **Rename the `ally` package to `suraksha`** (a 2026 first-place winner is called "Ally") | 6 |
| M7 | **Hard rule, stated on stage: Suraksha never auto-dials emergency services.** It gets a person to commit; 112 is shown on the family's screen | 4 |
| M8 | **Correct the language claim:** understands Hindi, English, Kannada, Tamil, Telugu, Marathi, Bengali…; speaks Hindi and English | 7 |
| M9 | **Correct the night claim:** nocturia is *a* risk; video evidence puts the peak at 7–10 am and 7–10 pm (06:40 is well chosen) | 2 |
| M10 | **The barometer is confirmed** in the Watch4 spec; off-body is still "test on device" | 7 |

### SHOULD (strengthen the design or the demo)

| # | Change | From track |
|---|---|---|
| S1 | **Add the Moving-Arm Trap** (Apple's immobility rule; Vlaeyen 2013) with a demo beat: wave an arm on the mat while Naive mode stays green | 1, 2 |
| S2 | **Add Philips' expired 360° drop rule** (gyro/magnetometer) to L2 verify | 3, 7 |
| S3 | **Borrow from SafeStep:** the "still on the floor" status update, a device heartbeat (*silence never looks like safety*), a backup-caregiver reminder | 6 |
| S4 | **Do-Check wording "follows NHS fall guidance"** in L4 and Q&A | 2 |
| S5 | **Wear-test pass bar:** ≤ 1 false trigger per 40 waking hours (Kangas); **report nights separately** | 2, 4 |
| S6 | **Foreground service spec:** type `health`; heart rate only after a fall | 7 |
| S7 | **Recommend the 44 mm Watch4 (361 mAh)** in the demo kit and onboarding | 7 |
| S8 | **Competitor table v4:** Samsung, Apple, Pixel (verified flows); pendants; **Anvayaa, Emoha, Samarth, AGEasy Protec (2.1★), DrRing (500+ installs), Elderline, Kanega ($85/mo), Thessai; hackathon: SafeStep, Ally, CarePilot** | 1, 4, 5, 6 |
| S9 | **The "patent that proves the trap" slide** (Apple claim 11) | 3 |
| S10 | **A first-hour on-watch checklist** (off-body, barometer noise, battery, step latency, bathroom audibility) before any Kotlin | 7 |

### NICE (Q&A and lineage lines)

| # | Line | From track |
|---|---|---|
| N1 | *"Why a Galaxy Watch?"* → Indian senior watches are 2.1–3.5★ with 5-hour batteries; we put the intelligence in software on mainstream hardware | 4, 5 |
| N2 | *"Who pays?"* → children (often abroad), employers as an employee benefit, response networks as partners | 5 |
| N3 | *"Privacy?"* → Pip records her whole day, SafeStep puts a camera in her room; our mic opens only after a fall | 6 |
| N4 | Lineage: *"Height-plus-time-on-floor is a 2005 patent, now expired; barometers separate sitting from standing at 99.5% (Massé 2014). We point them at her answer."* | 2, 3 |
| N5 | Region: us-east-1 because Polly's generative voices aren't in Mumbai | 7 |
| N6 | Freedom-to-operate note (Apple claim 12; Philips audio; Alarm.com wear check) in the limits section | 3 |
| N7 | Avoid the "ambient OS" look: one architecture strip, not a wall of AWS logos | 6 |

## 7. Risks the research surfaced (honest list)

| Risk | Why it matters | Mitigation |
|---|---|---|
| **False-trigger rate in real life is unknown** | Every product that failed, failed here (track 4) | Wear test first; the pass bar is set; a false trigger costs one spoken question |
| **The wrist barometer is thinly studied** (1 paper) | V2 could be noisy | Measure the noise floor first; V2 is one vote of three; abstain = not up |
| **SafeStep is close** | Judges may have seen body-based "she stood up" | Our claim is about her *answer*, not detection; cite SafeStep openly |
| **Nearby active patents** (Apple claim 12, Philips audio, Alarm.com) | A venture risk, not a hackathon risk | Different mechanisms; FTO note; never claim those parts are novel |
| **No India-specific evidence of concealment** | The cultural core of the pitch rests on China + forums | **Track 9: two real conversations** |
| **Polly can't speak Kannada** | A Bengaluru judge may ask | Say it first (M8) |
| **Anvayaa's watch features are unknown** | It might already do some of this | Retry their site with Firecrawl before the event |

## 8. Still open

1. **Track 9, two real conversations (you):** one parent living alone (*"If you fell and your watch asked 'are you OK?', what would you press, and why?"*) and one child living away (*"Would a 'please call Amma' message be useful, or annoying?"*). That's the only way to close the India-concealment gap.
2. **Firecrawl redo when credits reset:** Reddit (r/india, r/AgingParents, r/GalaxyWatch), Anvayaa's site, Indian hackathon showcases (SIH/Unstop), Indian patents.
3. **On-watch measurements** (S10).
4. **The real rubric** for the target event (`00_RULES.md`). Every judge-facing choice above should be re-weighted once it's known.

## 9. Next step

On your approval of this synthesis, write **`SURAKSHA_BIBLE_v4.md`** applying the MUST + SHOULD changes (keeping v1–v3 as history), and update the red-team log with the research-driven corrections. The NICE items go into the challenge table and pitch notes.
