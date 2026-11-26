# Track 4 — User complaints (what goes wrong in real homes)

*26 Nov 2026. Status: **done, waiting for your review.***

*Method: Firecrawl credits were exhausted and Reddit is blocked in the built-in browser, so this track used the browser on: AgingCare.com (the largest US caregiver forum; 2 threads read in full, about 8 more as snippets), the Samsung Community (UK thread read in full, 16 replies; US threads as snippets), Apple Community (snippets), the Google Play listing for DrRing, and Amazon.in (14 listings; critical reviews read for 3 products). Searches went through DuckDuckGo. **Reddit wasn't reachable this time** (track 1 already covered two Reddit threads via a data provider). An r/GalaxyWatch thread on false fall detection (137 votes, 61 comments) was seen only as a search snippet.*

## The one-line finding

**Real users don't abandon fall detection because it misses falls. They abandon it because of what a false alarm *costs them*: an ambulance at the door, police on the line at 4 am, every contact phoned.** Then they take the device off, and the next real fall happens with nothing on. In one user's words: *"Samsung has made me infinitely LESS SAFE!"*

---

## The complaint table

| # | Where | What happened (their words, trimmed) | The failure mode | What it means for us |
|---|---|---|---|---|
| 1 | **AgingCare**, daughter of an 89-year-old (Lifeline pendant) | Two false alarms. The second time *"I was out of reach so they sent EMS. **She is very angry over the intrusion and now refuses to wear her necklace.**"* | **A binary escalation → humiliation → abandonment** | ⭐⭐ The exact chain our middle tier (PEELA) breaks. A false trigger in Suraksha costs her **one spoken question**, never an ambulance |
| 2 | **AgingCare**, another caregiver in the same thread | *"I remind her that pushing the button **DOES NOT MEAN** she is saying 'take me to the hospital'. It just means **'I NEED A LITTLE HELP'**, which may mean calling the next door neighbor or Daughter or Grandson or in fact 911."* | Families **invent a middle tier by talking** because the product doesn't have one | ⭐⭐ The best line yet for the third-option pitch: a caregiver explaining by hand what the device should do itself. And she lists the **neighbour first** |
| 3 | **AgingCare**, the same daughter | The base unit *"is loud enough, but **she can't hear it from her bedroom with the tv blaring**."* | The call-centre voice comes from a box in another room | Our voice comes from **her wrist**. Supports watch-first, max volume plus haptic before speaking (#25) |
| 4 | **AgingCare**, home-care agency owner (Florida) | Pendants come off *"when they are sleeping or in the shower, but those are the two most important times."* A wristwatch *"**becomes a piece of jewelry, not a 'medical device'**. Compliance is usually much easier."* A client's pendant swung round to his back after a fall, so he *"**lay on the floor all night**."* | Form factor kills compliance; pendants can be unreachable | ⭐ Validates the **watch** over a pendant. "Jewellery, not a medical device" is a good line for why Amma will wear it |
| 5 | **AgingCare**, 87-year-old who still drives | *"keeps bumping the button… That, of course, triggers emergency response personnel."* Another user: pendants *"occasionally went off when they were not touched at all… I had to go to where the landline was."* A third: fall detection *"is often more of a p\*i\*t\*a than helpful."* | Accidental triggers, each costing a scramble | False alarms are the **#1 everyday irritant**. Our wear test (#33) decides whether we repeat this |
| 6 | **Samsung Community (UK)**, Galaxy Watch 6, 16 replies | *"Woke up at 4 this morning to the emergency service talking to me through my watch."* · *"woken up at 12:30 am… emergency services shouting at me through my watch… Then my emergency contacts phoned… I've had a terrible night!"* · *"I was in my bed asleep. **I swiped in the wrong direction** & emergency protocols began."* | **False triggers during sleep**, while wearing; a confusing UI when half awake | ⭐ Night false triggers hit the people who wear it to bed, which is exactly the night coverage we're asking for (#32). The wrong-swipe confusion repeats Reddit's "I'm OK" mix-up (track 1). **Our answer:** a voice question, not a swipe, and no siren on a false trigger |
| 7 | **Samsung Community (UK)**, the same thread | *"**I am absolutely mortified as the police called back and they are furious!** … should there be an emergency now… emergency services along with all my contacts **will ignore it due to too many false alerts. Samsung has made me infinitely LESS SAFE!**"* | **The cry-wolf effect:** false alarms burn the credibility of the real one | ⭐⭐ The **alarm-fatigue** argument in a user's own words. Our design keeps family and emergency services out of every non-verified trigger: GREY never pushes, HARA never pushes, PEELA asks for a call, not an ambulance |
| 8 | **Samsung Community (US)**, Galaxy Watch4 thread ("Hard fall detection triggered", 6+ pages) | *"Watch 4 sending false fall detection alerts and an 'I've moved' alert to my emergency contacts… extremely annoying!"* · *"The recent update now has my GW4 sending false fall alarms, **even with Fall Detection turned off**."* (snippets) | False alarms reach family; a software update made it worse | Watch4 is *our* hardware. Its native fall detection has a public reputation for false alerts, which is a reason to **verify** our own trigger, not trust it |
| 9 | **Amazon.in**, DrRing (3.9★, 41 ratings), 1★ review | *"The button does NOT work upon just clicking it. It needs you to press the power button on the phone too! **After an accident, it is too much to expect a person to ALSO have the phone, AS WELL AS operate the phone.** If they could, why use the button at all?"* Plus no onboarding call, WhatsApp ghosting, hard returns | **Phone-dependent** "one-touch"; no support | ⭐ India's best-known product fails at the one thing it sells. Our watch talks and listens **itself** (LTE watch or Bluetooth to the phone; the watch is the interface) |
| 10 | **Google Play**, DrRing Alert app | **500+ downloads, 10 reviews**, 4.1★ | Tiny scale | ⭐ **The Indian market is barely served.** The leading dedicated product has hundreds of users, not lakhs |
| 11 | **Amazon.in**, AGEasy × boAt Protec Neo senior SOS watch (₹3,599, 3.5★, 25 ratings) | *"sensor was not working… after 6 month of use it is not turning on"* · *"Basic features not available, that is connectivity."* | Cheap senior "SOS" watches are unreliable | The Indian "senior smartwatch" category exists, but it's SOS-button-only, low quality, and has no fall verification |
| 12 | **Amazon** (US review on an Amazon.in listing), Connected Caregiver 4G medical-alert watch (3.4★) | *"**False security**… The only time I have experienced a fall… **the fall detection did not work**, so I tried the alert button, which did not work either. The only time fall detection does anything is when I fill a grocery bag with air… or drop the device."* | Misses a real fall, fires on drops | Both failure directions in one review. Our **drop rule** (Philips' expired 360° spin, track 3) and the post-trigger **verification** address the drop half; the miss half is why we never claim to catch every fall |

---

## Patterns across all sources

| Pattern | How often we saw it | Our design answer | Status |
|---|---|---|---|
| **A false alarm escalates straight to an ambulance, police or every contact** | AgingCare #1 and #5, Samsung #6, #7, #8 | **PEELA middle tier.** No push on GREY or HARA. Emergency services are never auto-dialled by Suraksha; 112 is shown to the family | Designed (bible v3) |
| **Humiliation leads to taking it off** | AgingCare #1, Samsung #7 | Cost asymmetry: a false trigger costs **one question to her**, not a public event | Designed; **wear test pending** |
| **Confusing UI in a crisis** (wrong swipe; "I'm OK" mistaken for "yes") | Samsung #6, Reddit (track 1) | **Voice** conversation in her language; buttons only as a fallback (#19) | Designed |
| **Can't hear the device** | AgingCare #3 | The voice is on her wrist; haptic before speaking; max volume | Designed (#25) |
| **Comes off for sleep and bath** | AgingCare #4, Fleming (track 2) | Watch (jewellery), water-resistant, a charge window in the morning, GREY nudges | Designed (#22, #32) |
| **"One-touch" that needs the phone too** | Amazon.in #9 | The watch is the whole interface | Built (AudioBridge ✅) |
| **No support, no onboarding** | Amazon.in #9 | Our minimal onboarding (#41) is in scope; support is out of scope for a hackathon, so we say so | Partly |
| **Unreliable cheap hardware** | Amazon.in #11, #12 | Galaxy Watch (mainstream hardware) plus our software, not a custom device | By choice |

## What nobody built (from complaints)

1. **A false trigger that costs nothing socially.** Every product we saw turns "maybe a fall" into a public event: a siren, a call centre, an ambulance, police or texts to everyone. Nobody makes the first step **a private conversation with her**.
2. **A product a caregiver doesn't have to explain.** Complaint #2 shows families *verbally* re-labelling the button as "a little help". Nobody built that meaning into the device.
3. **A serious Indian option.** The leading dedicated product has about 500 app installs and support complaints; cheap "SOS watches" are 3.5★ with hardware failures.

## What this changes for Suraksha (proposals; nothing edited until you agree)

1. **Add the cry-wolf argument to bible §2.2 (Charger Trap):** *"Every false alarm spends credibility; users say their contacts and the police 'will ignore it'."* Quote Samsung #7.
2. **New pitch line for the middle tier, from caregiver #2:** *"Families already tell their mothers 'pressing it doesn't mean hospital, it means a little help.' We built that sentence into the watch."*
3. **Hard rule in L5/L6, said on stage:** **Suraksha never dials emergency services by itself.** It gets a family member or neighbour to commit, and shows 112 on their screen. (That's already the design; making it explicit answers complaints #1, #6 and #7.)
4. **Wear-test framing:** report **false triggers per wear-night separately** from daytime (Samsung #6 shows night is where users get burned).
5. **Competitor table additions (India):** AGEasy × boAt Protec Neo (an SOS-button smartwatch, about ₹3.6k, 3.5★); DrRing's scale (500+ installs). **US:** Connected Caregiver-type 4G watches (false-security reviews).
6. **Q&A answer for "why a Galaxy Watch, not a cheap senior watch?":** *"Indian senior SOS watches are 3.5-star with dead sensors in six months. We use mainstream hardware and put the intelligence in software."*

## Sources

- [AgingCare: "Mom refuses to wear her alert necklace"](https://www.agingcare.com/questions/mom-refuses-to-wear-her-alert-necklace-179531.htm) (read in full)
- [AgingCare: "My mom keeps bumping the button on her lifeline apparatus…"](https://www.agingcare.com/questions/my-mom-keeps-bumping-the-button-on-her-lifelife-apparatus-that-hangs-around-her-neck-on-a-lanyard-an-486161.htm) (read in full)
- AgingCare search snippets: "Mom won't wear safety pendant", "Mom keeps taking off her personal fall alert necklace", "Best wearable device for fall alerts?"
- [Samsung Community UK: "Watch 6 fall detect"](https://community.samsung.com/uk/conversations/wearables/watch-6-fall-detect/eu_8142064) (read in full)
- [Samsung Community US: "Hard fall detection triggered" (Watch4)](https://us.community.samsung.com/t5/Galaxy-Watch/Hard-fall-detection-triggered/m-p/2690644) (snippets, pages 1 and 6)
- [Samsung Community: "My Galaxy 4 watch is sending out erroneous 911 calls"](https://r1.community.samsung.com/t5/wearables/my-galaxy-4-watch-is-sending-out-erroneous-911-calls/td-p/30142406) (snippet)
- [Apple Community: "How do I set fall detection"](https://discussions.apple.com/thread/254957661) (snippet: the "I fell, but I'm OK" option)
- [Google Play: Drring Alert](https://play.google.com/store/apps/details?id=com.drring.alert.health.care) (500+ downloads, 10 reviews)
- [Amazon.in search: "sos watch for elderly fall detection"](https://www.amazon.in/s?k=sos+watch+for+elderly+fall+detection); reviews read on DrRing (B0CTG6NNK8), AGEasy × boAt Protec Neo (B0F66Z2918) and Connected Caregiver (B0DYK4DKLM)
- r/GalaxyWatch "Anyone experienced false fall detection?" (snippet only; Reddit blocked)

## Couldn't confirm

- **Reddit, broadly.** It's blocked in the browser and Firecrawl is out of credits. Once credits reset, a pass on r/GalaxyWatch, r/AgingParents and r/india would add Indian-family voices.
- **Indian-language complaints** (Hindi reviews, WhatsApp-forward culture). Not searched.
- Whether the Watch4 "false alarms even with fall detection off" claim was a firmware bug that's since been fixed. It's a forum snippet only.
- The Amazon review on #12 is from a US buyer shown on Amazon.in; it's labelled as such.
