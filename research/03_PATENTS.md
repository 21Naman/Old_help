# Track 3 — Patents

*25 Nov 2026. Status: **done, waiting for your review.***

*Method: Firecrawl credits ran out at the start of this track, so I used the built-in browser on Google Patents and its own results endpoint. That was 9 searches (by company: Apple, Samsung, Google, Philips, Amazon; by mechanism: barometer + get-up, voice check after a fall, asking the user to act, escalation that waits for acceptance, sensors overriding "I'm OK", and language). **Claims read for 10 patents.** Status (active or expired) is taken from Google Patents and is **not legal advice**. Indian patents (InPASS) were not searched; that's a gap.*

## The one-line finding

**The patent record confirms the trap, and shows which parts of our design are old and which are new.** Apple's own claim says the alert is *not* sent *"if a response to the prompt is received"*. Height-change detection, "is the watch actually worn" checks, and even listening for groans after a fall are **all already patented** (some expired, some active). **What nobody claims is the combination: treating the person's "I'm OK" as something to verify, asking her to *do* something, and using her body's answer to choose a middle tier.**

---

## The mechanism table (claims read)

| Patent | Owner, status | What claim 1 actually protects | What it means for us |
|---|---|---|---|
| **US12100282B2** "Care event detection and alerts" | **Apple, active** (priority 2014) | Detect a fall, show a prompt, and send an alert *if no response* is received. **Claim 11:** detect *motion after the fall*; alert if the user is immobile for a period; **"not transmit the alert if a response to the prompt is received"**, where the response is **"a touch input on the touch-screen display"** | ⭐⭐ **The Theek Hoon Trap, written into a granted claim.** Any response cancels. The response is a *touch*, which the Reddit father couldn't do. Our design differs on both: **the response is spoken, and it doesn't cancel anything by itself** |
| **US12380789B2** "Detecting falls using a mobile device" | **Apple, active** (priority 2017) | Detect a fall from an impact plus **behavioural features *before* the impact** (bracing, flailing, balancing). **Claim 12:** *"determining… that the user has **recovered after the fall**"* using a behaviour model | ⭐ **The closest prior art to our get-up check.** But it's a dependent claim tied to claim 1's pre-impact motion model. Ours uses barometric height relative to her own pre-fall reading, steps, and a requested action. **Different mechanism; cite it as prior art and never claim "first to detect recovery"** |
| **US11282361B2** "Detecting falls using a mobile device" | Apple, active | Fall detection that uses a **fall risk** from the user's age, gender and vascular health | Apple adjusts by *who* the user is. We adjust by *her own* baseline (pre-fall pressure, wake window, voice speed) |
| **US8747336B2** "Personal emergency response (PER) system" | **Bao Tran, expired (fees not paid)** (priority 2005) | Detect a fall by **"analyzing changes in height"** plus acceleration, then **"determining if the patient is on a floor for a predetermined period"**; then **"confirming the fall when a person or a call center contacts the patient to verify the patient status."** | ⭐⭐ **Height plus time on the floor is old and free to use.** And this patent's confirmation step *is* the trap: a call centre asks the patient. **We use the same physics to check the *answer*, not the fall.** Pitch nuance: *never* say "we invented barometer fall detection" |
| **JP2012506084A** "Fall detection system" | **Philips, expired (fees not paid)** (priority 2008) | A **dropped** device spins **≥ 360°** (magnetometer), while a body fall doesn't; alarm only if it didn't spin | ⭐ **A free drop signature for our Charger Trap.** Add a "≥ 1 full rotation = watch dropped, not a person" rule to L2 verify. Proven, free, cheap |
| **JP5539857B2** "Fall detection system" | **Philips, active in Japan** (priority 2007) | A second check: was the sensor **actually worn at the moment of impact** (free-fall signature of the device itself, and/or a body-proximity sensor)? | The idea behind our on-wrist/GREY check is 2007 prior art. Fine for a prototype. Cite it as lineage |
| **US12198525B2** "Fall detection and reporting technology" | **Alarm.com, active** (priority 2011) | First decide the device **is likely being worn**, then check an event threshold, then alert thresholds; **skip the alert** if they aren't met | Overlaps our verify layer in *structure*. A prototype is fine; a venture would need a freedom-to-operate check (labelled caution) |
| **US11800996B2** "Detecting falls… using a wearable sensor" | **Philips, active** (priority 2019) | After an apparent fall, record audio, isolate *the subject's* voice with a **model tuned to their acoustic profile**, extract **"audible trauma-related cues"** with a **bi-directional LSTM**, and confirm the fall. Claim 2: cues include *"moaning, groaning… verbal expression of having fallen or being injured."* Claim 3: **estimate the extent of pain** | ⭐ **The closest prior art to our voice voter.** Philips listens for groans to confirm a *fall*. We measure speech rate against her baseline plus Hindi/English pain words, to check whether her *"I'm OK"* holds. The techniques differ (no per-subject acoustic model, no BiLSTM). **Don't pitch V4 as novel; cite it** |
| **US10687193B2** "Assist device and system" | **UnaliWear, active** (maker of the **Kanega** voice-first medical-alert watch for seniors) | A wearable that learns the wearer's **activity profile** (times and places) and talks to the wearer when behaviour deviates | ⭐ **A direct competitor we missed in track 1:** a *voice-first* senior watch, already shipping (US). Add it to the competitor table; check its fall flow in track 5 |
| **US11298049B2** "Detecting dangerous situation" | Samsung, active | Camera (dynamic vision sensor) fall detection with danger levels from post-fall motion | Camera-based. Not our path; a privacy contrast |

## What the searches *didn't* find (gaps)

| Search | Result | Meaning |
|---|---|---|
| Fall + **"instruct / request / prompt the user to stand up or walk"** + verify | **Nothing relevant** (athletic watches, pill dispensers) | ⭐ **No patent we found asks the person to *do* something and then checks the sensors.** That supports the Do-Check as our clearest novel element |
| Fall + **user says "fine" / cancels** + sensors **override** or keep monitoring | Nothing on point (only generic health-monitoring patents) | ⭐ **No claim treats "I'm OK" as unverified.** Apple claims the opposite |
| Fall + caregiver **accepts / acknowledges** + **next contact** | Nothing fall-specific (Dexcom glucose alerts, bed-exit sensors) | Sequential escalation with acceptance exists in products (DrRing, track 1) but isn't a fall-specific claim we found. **A low-novelty area; don't pitch it as new** |
| Fall + **language / dialect / multilingual** voice | Nothing fall-specific (one 2025 Chinese elder help-call audio patent) | Hindi/Hinglish post-fall conversation looks unclaimed. *Weakly searched; labelled* |
| Amazon / Alexa + fall + voice prompt | Nothing fall-specific surfaced | Not confirmed either way. *Labelled* |

---

## What we can pick (free or low-risk)

1. **Philips' 360° rotation drop signature** (expired) → add it to L2 verify as a third GREY rule. It costs one magnetometer or gyroscope check and makes the Charger Trap demo stronger.
2. **Bao Tran's "height change + time on the floor"** (expired) → our V2 physics is free to use. Cite it to show we know the history.
3. **Apple's claim 11 as a pitch slide:** quote the patent text, *"not transmit the alert if a response to the prompt is received"*, next to our rule *"a response is one vote."* That's a powerful, verifiable contrast.

## What to be careful about (active claims near ours)

| Our part | Nearby active claim | Why we're probably fine for a hackathon | For a venture |
|---|---|---|---|
| V4 voice voter | Philips US11800996B2 | Different technique (speech rate + keywords, no per-subject acoustic model, no BiLSTM); different purpose (verify "I'm OK", not confirm a fall) | Freedom-to-operate review |
| Recovery check (V2/V3) | Apple US12380789B2 claim 12 | It depends on claim 1's pre-impact behaviour model, which we don't use | Same |
| Worn check (L2) | Alarm.com US12198525B2; Philips JP5539857B2 (Japan) | A prototype, and a common-sense step with old prior art | Same |

*(Not legal advice. Hackathon prototypes generally aren't the concern; a product launch would be.)*

## What nobody built (from patents)

1. **Verifying the "I'm OK".** Every claim treats a response as the end, or as a confirmation of the fall. **None treats it as a hypothesis to test.**
2. **Asking for an action** (the Do-Check). No hits.
3. **A middle tier** chosen by whether the body agrees. All claims are binary: alert or no alert.
4. **Hindi/Hinglish post-fall dialogue.** No fall-specific hits.

## What this changes for Suraksha (proposals; nothing edited until you agree)

1. **Sharpen the novelty claim in the pitch** to exactly: *"Others detect falls, check whether the watch is worn, and even listen for groans. We're the first we've found to treat 'I'm OK' as a claim to verify, by asking her to do something and letting her body vote."* Drop any hint that barometer fall detection or wear checks are new.
2. **Add Philips' 360° drop rule** to L2 verify (from an expired patent, so free).
3. **Add UnaliWear/Kanega to the competitor table** (a voice-first senior watch, US). Dig into its fall flow in track 5.
4. **New pitch slide, "The patent that proves the trap":** Apple US12100282B2 claim 11 quoted, versus our rule.
5. **Design lineage line for Q&A:** *"Height-plus-time-on-floor goes back to a 2005 patent (now expired); wear-checking to Philips in 2007. We built on that and pointed it at a new question."*
6. **Keep a freedom-to-operate note** in the bible's "what this is NOT" or limits section, for V4 and the recovery check, if anyone asks about commercialising.

## Sources (Google Patents)

- [US12100282B2 — Apple, Care event detection and alerts](https://patents.google.com/patent/US12100282B2/en)
- [US12380789B2 — Apple, Detecting falls using a mobile device](https://patents.google.com/patent/US12380789B2/en)
- [US11282361B2 — Apple, Detecting falls using a mobile device](https://patents.google.com/patent/US11282361B2/en)
- [US8747336B2 — Bao Tran, Personal emergency response system (expired)](https://patents.google.com/patent/US8747336B2/en)
- [JP2012506084A — Philips, Fall detection system (360° drop rule, expired)](https://patents.google.com/patent/JP2012506084A/en)
- [JP5539857B2 — Philips, Fall detection system (worn-at-impact check)](https://patents.google.com/patent/JP5539857B2/en)
- [US12198525B2 — Alarm.com, Fall detection and reporting technology](https://patents.google.com/patent/US12198525B2/en)
- [US11800996B2 — Philips, Fall detection with audio trauma cues](https://patents.google.com/patent/US11800996B2/en)
- [US10687193B2 — UnaliWear, Assist device and system](https://patents.google.com/patent/US10687193B2/en)
- [US11298049B2 — Samsung, Detecting dangerous situation](https://patents.google.com/patent/US11298049B2/en)

## Couldn't confirm

- **Indian patents** (InPASS / IP India) weren't searched.
- **The Amazon/Alexa fall flow.** Searches didn't surface a fall-specific claim; not ruled out.
- **The Apple/Samsung product flows vs. claims.** Products may differ from claims; track 1's support docs are the source for *behaviour*.
- The "nothing found" rows are absence of evidence from ~10 searches, **not** proof that no such patent exists.
