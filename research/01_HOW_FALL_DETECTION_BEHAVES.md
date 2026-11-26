# Track 1 — How fall detection actually behaves

*25 Nov 2026. Status: **done, waiting for your review.***

*Method: 12 web searches, then 11 sources read in full. That covers the official support docs for Samsung (two pages), Apple and Google; an industry pendant provider; two Indian elder-care services (Emoha, Samarth); India's DrRing; a 2026 GeekWire startup profile; a University of Alberta review summary; and two Reddit threads read through a Reddit data provider (r/AppleWatch, 415+ upvotes on the top reply; r/india). Reddit's own pages blocked direct scraping.*

## The one-line finding

**Every product, from Samsung to Apple to Google to the pendant call centres, ends the emergency the moment the person says or taps "I'm OK". Not one of them checks whether she actually got up.** The trap is real, it's documented by the vendors themselves, and the people who build in this space say the same thing out loud: *"Number one, they say, 'I'm OK.'"*

---

## The mechanism table

| Who | What happens after a fall | The real core mechanism | What "I'm OK" does | Source |
|---|---|---|---|---|
| **Samsung Galaxy Watch** (Watch4 and later) | Alert for **60 s** with a popup, sound and vibration. With no response, an **SOS message** goes to emergency contacts | Pure **response timeout**. Nothing in the docs checks movement or posture after the fall | **Cancel ends it.** Also: fall detection is **off by default** and has to be turned on in the Galaxy Wearable app. On Watch4 you choose "Always / During physical activity / Only during workouts" | Samsung AU and US support |
| **Apple Watch** (SE, Series 4 and later) | Taps the wrist, sounds an alarm, shows an alert. **If it detects you're moving, it waits for you to respond and won't call automatically.** If you're immobile for about a minute, a 30 s countdown starts, then it calls emergency services and contacts | Response + **an immobility check**. Movement of *any* kind counts as "fine" | **"I'm OK" or Close dismisses it.** It's on automatically for users aged 55+. It needs Wrist Detection on | Apple support 108896 |
| **Google Pixel Watch** | Waits about **30 s**, then vibrates and rings and asks if you want to call. With no response, it calls emergency services after **60 s** with an automated voice message | Response timeout | **"I'm OK" dismisses it.** The supported languages are Danish, Dutch, English, French, German, Italian, Japanese, Mandarin, Norwegian, Spanish and Swedish: **no Hindi or any Indian language**, even though India is a supported country | Google support 12663810 |
| **US medical alert pendants** (MedicalAlert.com, typical of the industry) | A fall alert or button press connects to a call centre specialist | A **human on a speaker** | *"The specialist comes on, you say you are fine, and that is the end of it."* Silence is treated as an emergency; words end it | medicalalert.com |
| **DrRing** (India, about ₹6–9k) | A **one-touch BLE button** paired to an Android phone. It sends WhatsApp alerts and **calls the family list in order** (busy means the next number) | **She must press the button.** The companion app claims phone-accelerometer fall detection | Not documented, but it's a press-to-alert product | drring.health |
| **Emoha** (India) | 24/7 helpline, app button, pendant, fall-detection watch. *"The response team calls back, assesses the situation…"* | A human call centre callback | The callback assesses her; nothing in the public docs verifies what she says | emoha.com |
| **Samarth** (India) | A trained care manager doing daily in-person visits, plus devices where appropriate | **Humans, not devices.** *"An alert sent to a phone in another time zone… is largely symbolic"* | — | samarth.community |
| **Thessai** (US, 2026 startup) | Ambient motion sensors learn her routine and alert the family on deviation (no wearables, cameras or mics) | Routine baseline + deviation | — (it doesn't ask her) | GeekWire, Nov 2026 |

---

## The evidence that the trap is human, not just technical

| Evidence | What it says | Source |
|---|---|---|
| **Thessai founder** (built it after his mother-in-law hid a fall) | She had a phone and an emergency button within reach, didn't use them, and **told no one until the next day, when she needed an ambulance**. Why older adults stay quiet: *"Number one, they say, 'I'm OK.' Number two, 'I don't want to bother you.' And number three, and most important, is embarrassment."* | GeekWire, 2 Nov 2026 |
| **University of Alberta review** of 118 fall-detection studies | **None tested with seniors or in real life**; most used students, some used mannequins. One cited study: **80% of older adults were reluctant to push the button after a fall**, because activating it was hard or *they didn't want to disturb a caregiver*. And: *"Not everyone who falls wants an immediate emergency dispatch. They might want to contact a neighbour instead or get up themselves."* | UAlberta Folio, 2018 (the primary study behind the 80% figure is to be traced in track 2) |
| **r/AppleWatch**, elderly father | Dad fell; the watch asked; he **said "yes" out loud**, but the watch has no voice input, so it didn't call. Top replies: *"Maybe he thought 'I'm okay' was 'okay' as in 'yes please call'?"* (183 upvotes). *"When you are on your back, in pain, last thing that comes to mind is that you need to tap buttons."* Another user: *"I fell… I pressed the 'I'm ok' button so it wouldn't call 911."* Another: *"fallen out of bed, fractured my elbow and gotten nothing."* | Reddit r/AppleWatch |
| **r/india**, 63-year-old mother | She fainted, hit her head, needed 7 stitches, and was on the floor about 10 minutes before getting up and **calling an aunt who lives nearby**. Her son: *"I didn't even find out until after she was back from the hospital."* Comments: *"Life alert does not operate in India"*; *"how do you convince them to wear it?"*; and worries about keeping it charged | Reddit r/india |
| **DrRing review** (a Whitefield, Bengaluru senior apartment) | Residents *"fall down losing balance and they can't wake up to reach to their phone… In the morning, we open the door with the spare key and find them on the floor."* | drring.health |

---

## What we can pick

1. **Apple's immobility check exists, so credit it, then go past it.** Apple already uses *one* body signal: immobility. But in Apple's own words, if it detects you're moving, it **won't** call automatically. An injured person waving an arm, trying to get up, or rocking on the floor counts as "moving". That's a second, sharper trap. **Moving isn't standing.** Our barometer "back to her pre-fall height" voter is exactly the evidence that separates them.
2. **Silence counts as an emergency everywhere.** Every product treats no response as an emergency. Keep that ✅; it's already our LAAL rule.
3. **Sequential calling** (DrRing: busy means the next number) is a proven, locally accepted pattern. Our Step Functions chain already does this. Cite DrRing as proof that Indian families want it.
4. **Voice, not buttons, in the emergency moment.** The Reddit father said "yes" to a screen. Our conversation is spoken (Polly/Transcribe), and the buttons are only a fallback.
5. **The neighbour, not an ambulance.** The UAlberta line (*"They might want to contact a neighbour instead"*) plus the r/india mother calling her nearby aunt both back our neighbour-in-parallel design (#30). This is now evidence, not a guess.
6. **Samarth's honesty line for the pitch:** *"An alert sent to a phone in another time zone… is largely symbolic."* That's exactly why we get **one person who can arrive** to commit.

## What nobody built

| Gap | Who comes closest | Why it's still a gap |
|---|---|---|
| **Verify "I'm OK" against the body** | Apple (an immobility check only) | Movement ≠ standing. Nobody checks height, steps or a requested action |
| **Ask her to *do* something** (our Do-Check) | Nobody | Every product asks a yes/no question or shows a button |
| **A spoken conversation in Hindi after a fall** | Nobody | Pixel has no Indian languages; Samsung and Apple are button UIs; pendants are English call centres |
| **A soft middle tier** ("I believe you, but I'm asking your daughter to call") | Nobody | Every product is binary: cancel or full SOS. That's *why* people press "I'm OK": the only alternative is a siren and an ambulance |
| **Getting one specific person to commit, then telling her who is coming** | DrRing (sequential calls) | Calls ring in order, but nothing tells her *who accepted* or *when they'll arrive*, and nothing stays with her |
| **Respecting what she wants shared** | Thessai (room-level sensor switches) | Nobody lets her set *who* hears *what* by voice |

**The biggest new insight is the binary problem.** Products offer only "cancel" or "full SOS to emergency services". A person who's embarrassed and doesn't want an ambulance has exactly one escape hatch: "I'm OK". **Our PEELA tier is the missing middle option, and it's the reason she wouldn't need to lie.** That's a stronger pitch than "we catch the lie".

---

## What this changes for Suraksha (proposals; nothing edited until you agree)

1. **Reframe the trap with the new evidence.** The trap isn't only "she lies". It's **"the only alternative to 'I'm OK' is an ambulance siren"**. Proposed pitch line: *"Every watch gives her two buttons: 'I'm OK' or 'call an ambulance'. An Indian mother will press 'I'm OK' every time. We give her a third option."*
2. **Add a second named trap, the Moving-Arm Trap.** Apple's own docs say movement means no automatic call. Our Do-Check plus the height vote is the answer. A demo beat: the teammate on the mat waves an arm, and Naive mode stays green.
3. **Correct the competitor table in bible §3.** Use verified behaviour: Samsung's 60 s and off by default; Apple's movement check and auto-on at 55+; Pixel's 30 + 60 s and no Indian language; DrRing (₹5,999/yr, press-only, sequential calls); Emoha and Samarth (human call-backs and visits); Thessai (ambient sensors). All of them dismiss on "I'm OK".
4. **Killer facts now sourced:**
   - *"Older adults reluctant to press the button after a fall: 80%."* (cited via UAlberta; primary source to trace in track 2)
   - *"None of 118 fall-detection studies tested with seniors in real life."*
   - Pixel fall detection: **no Indian language**.
   - *"Life Alert doesn't operate in India"* (forum claim; label it as such).
5. **Make the "Not everyone wants an ambulance" line a design principle** in bible §4: *"Ask her first, offer a middle option, call the nearest person, not the siren."*
6. **Pitch-only:** credit Apple's immobility check as prior art. It shows we know the field, and it sets up the Moving-Arm Trap.

## Sources

- [Samsung US: Detect fall feature](https://www.samsung.com/us/support/answer/ANS10003423/): off by default, Watch4 options
- [Samsung AU: Activate Hard Fall Detection](https://www.samsung.com/au/support/mobile-devices/activate-hard-fall-detection/): the 60 s alert, cancel, SOS to contacts
- [Samsung US: Emergency situations](https://www.samsung.com/us/support/answer/ANS10002904/): SOS repeats location every 30 min for 24 h
- [Apple: Use Fall Detection](https://support.apple.com/en-us/108896): the moving/immobile logic, "I'm OK", auto-on at 55+
- [Google: Pixel Watch safety features](https://support.google.com/googlepixelwatch/answer/12663810?hl=en): the 30 + 60 s flow, the language list
- [MedicalAlert.com: what happens with false alarms](https://www.medicalalert.com/blog/pressed-by-accident-what-really-happens-with-medical-alert-false-alarms/): "you say you are fine, and that is the end of it"
- [Emoha: Emergency support](https://emoha.com/care/emergency-support): call-back protocol
- [Samarth: Home safety monitoring](https://care.samarth.community/blog/safety/elderly-home-safety-monitoring-india/): "largely symbolic" alerts, human layer
- [DrRing: Alert button](https://drring.health/buy/drringalert/): press-only, sequential calling, pricing; [DrRing home](https://drring.health/): the Bengaluru apartment review
- [GeekWire: Thessai (2 Nov 2026)](https://www.geekwire.com/2026/startup-uses-motion-sensors-and-ai-to-tell-families-when-an-aging-parents-routine-changes/): "they say 'I'm OK'"
- [UAlberta Folio: why fall detection devices fall short (2018)](https://www.ualberta.ca/en/folio/2018/02/why-fall-detection-devices-for-seniors-are-falling-short.html): the 118-study review, the 80% reluctance, neighbour preference
- [r/AppleWatch: "Detected a fall… dropped the ball"](https://www.reddit.com/r/AppleWatch/comments/1dyfrow/detected_a_fall_offered_to_call_dropped_the_ball/): an elderly user's interaction failure
- [r/india: "Mom (63) had a serious fall while home alone"](https://www.reddit.com/r/india/comments/1nxtxfr/mom_63_had_a_serious_fall_while_home_alone_i_live/): the Indian family reality

## Couldn't confirm

- Whether Samsung's fall flow has *any* post-fall movement check. Its docs mention only the response timeout.
- The primary study behind "80% reluctant to press". It's cited in the review summary; trace it in track 2.
- DrRing's fall-detection accuracy. Their app claim is unverified.
