# Track 2 — Research papers

*25 Nov 2026. Status: **done, waiting for your review.***

*Method: 10 searches of the Firecrawl research index (PubMed, PMC and others), plus 3 web searches. Full text read for 2 papers (Fleming & Brayne BMJ 2008; Vlaeyen et al. 2013). Full PubMed abstracts pulled for 5 more (Massé 2014, Jatesiktat 2017, Bianchi 2010, Kangas 2014, Tinetti 1993). Abstracts and passages used for about 12 others. NHS falls guidance read in full. Where only an abstract or a secondary citation was available, the table says so.*

## The one-line finding

**The research backs our design on every point that matters, and corrects one number we were about to misquote.** People who can't get up are common; most don't use the alarm they're wearing, and some say why: *"for fear of being taken into hospital."* Barometers *can* tell standing from sitting or lying. And real-world fall detectors raise false alarms every day, which makes our wear test the most important measurement we haven't taken yet.

---

## 1. The trap is human, and it's documented

| Paper | What it found | What it means for us |
|---|---|---|
| **Fleming & Brayne, BMJ 2008** (prospective cohort, n=110, aged 90+, Cambridge UK; **full text read**) | 82% of falls happened when the person was alone. **80% (53/66) of fallers couldn't get up** after at least one fall; 30% lay on the floor for an hour or more. In **80% (113/141)** of falls where the person was alone and couldn't get up, **they did not use their call alarm**, even though 99% had one. **97% (37/38) of long lies happened to people who had an alarm and didn't press it.** Virtually nobody who *did* press it lay an hour or more | ⭐ This is the **primary source** behind the "80%" in track 1. Correct wording: *"In 4 out of 5 falls where an older person was alone and couldn't get up, they didn't use the alarm they had."* That's stronger than the University of Alberta paraphrase ("reluctant to push the button"), so cite Fleming directly |
| **Fleming & Brayne: participants' own words** | *"I didn't want to use the call alarm, although I was wearing it, **for fear of being taken into hospital**."* · *"I wanted to be able to get up by myself… It makes me annoyed if I have to have help."* · *"My niece is only next door. I can bang on the wall."* · *"I'd already taken it off ready for bed… on the floor all night until next morning."* | ⭐⭐ **The binary-choice problem (track 1) in a primary source.** Fear of the ambulance and hospital outcome is *why* people don't call. Also the neighbour, the bedtime watch-off gap (our night coverage, #32), and the wish to get up by herself (our Do-Check respects this) |
| **Zhu et al., Front Public Health 2026** (qualitative, n=19, China) | *"I don't want to be a burden."* Filial-piety cultures show two faces: caution *and* **concealing minor falls "to avoid causing family worry"**. Falls are framed relationally: a fall *"could trouble children, interrupt their work."* | The closest published cultural match to "theek hoon". Our pitch can say: *"This is documented in filial cultures, not just a hunch."* India-specific qualitative evidence wasn't found (see gaps) |
| **Tinetti et al., JAMA 1993** (n=1,103, aged 72+, US community) | Among non-injured fallers, **47% couldn't get up** after at least one fall. Those who couldn't were more likely to have lasting decline in daily activities (35% vs 26%) | Even *uninjured* falls leave half of people on the floor. "She wasn't hurt" doesn't mean "she got up" |
| **Wild, Nayak & Isaacs, BMJ 1981** (n=125, aged 65+, Birmingham UK; abstract and JSTOR excerpt) | 20 lay on the floor more than an hour; **11 of those 20 died in the following year**. The commonly quoted line from the abstract is *"half died within six months"* (the full abstract was truncated in our index; seen via secondary sources) | ⭐ The long-lie mortality fact. Safe pitch wording: *"In the classic study, more than half the people who lay on the floor over an hour died within a year."* Use "11 of 20", which we read directly |
| **Vlaeyen et al., BMC Geriatrics 2013** (26 real falls on video, 3 frail residents; **full text read**) | None got up unaided. Mean time on the ground was **28 min without the alarm vs 11 min with it**. Pressing the alarm took **70 s on average** (up to 224 s). **62% of falls happened 7–10 am or 7–10 pm.** And: ***"the postfall phase was not characterized by inactive participants."*** | ⭐ **Direct evidence for the Moving-Arm Trap:** people *move* on the floor after real falls, so an immobility check like Apple's misses them. And 7–10 am is exactly our 06:40 story window |

## 2. The physics: can a wrist barometer tell standing from lying?

| Paper | What it found | What it means for us |
|---|---|---|
| **Massé et al., Med Eng Phys 2014** (trunk-worn, 7 people, 322 transitions, real world) | A commercial barometer (MS5611) told **sitting from standing with 99.5% accuracy**, and fully separated sit-to-stand from stand-to-sit | ⭐ The physics works. But this was trunk-worn, not wrist |
| **Bianchi et al., IEEE TNSRE 2010** (waist, 20 young volunteers, falls onto a mattress) | Adding the barometer raised **sensitivity from 75% to 97.5% and specificity from 91.5% to 96.5%**, with no false positives during extended daily activities | The barometer as an *independent vote* is proven, not exotic. Caveat: young volunteers and a waist placement |
| **Jatesiktat & Ang, IEEE EMBC 2017** (**wrist**-worn accelerometer + barometer) | High performance on simulated falls, **"except for a few false alarms occurring when sitting on the floor from a standing pose"** | ⭐ The only wrist study. The confusion is *sitting on the floor vs. falling*. For **our** use (has she got back up?), sitting on the floor correctly counts as "not up". Our V2 asks the opposite question from fall detection, and the known weak spot falls on the safe side |
| **Sabatini & Genovese, Sensors 2014** (barometer + IMU fusion) | Height error (RMSE) **5–68 cm**; a whitening filter removes short-term pressure noise | Raw barometer readings are noisy, so fusing with the accelerometer and filtering matters. Supports our "held 15 s + low arm variance" rule |
| **Manivannan et al., Sensors 2020** (review) | Weather, doors, HVAC, temperature and the sensor itself all shift readings | Our "relative to her own reading 10 s before the fall" design avoids weather drift (minutes) but not door or AC gusts (seconds), hence the 15 s hold |

**Verdict on V2:** physically sound and backed by published evidence, **as one vote, relative to her own baseline, with a hold time**. The wrist is the least-studied placement, so measuring the noise on our own watch (open flaw #5) is still required before we trust any threshold.

## 3. Real-world false alarms (the "will she take it off?" risk)

| Paper | What it found | What it means for us |
|---|---|---|
| **Bagalà et al., PLoS One 2012** (13 published algorithms vs **29 real-world falls**) | Average **sensitivity 57%** on real falls (vs. near-perfect on simulated ones). **False alarms in one day of monitoring: 3 to 85**, depending on the algorithm | ⭐ Lab numbers lie. This is why we report *held-out* numbers and run a *wear test* |
| **Kangas et al., Gerontology 2014** (15,500 h, 16 older people, real life) | **Sensitivity 80% (12/15 real falls)**. False alarms of **0.049/h**, reduced to **0.025/h = 1 per 40 hours** | A realistic target for our wear test: **about 1 false trigger per 40 waking hours**. Above that, the Do-Check becomes daily nagging |
| **Chaudhuri / Demiris et al.** (older adults wearing a fall-detection device, real world; via a review) | A **42% false-positive rate**; participants were *"unhappy with the volume of false alarms"* | False alarms are the #1 reason people stop wearing these |
| **Yasmin et al., Sensors 2025** (smartwatch + hip, real homes) | False positives spiked in uncontrolled homes; retraining on user feedback cut older adults' false alarms to **2–4 per day** | Even good systems sit at 2–4/day. **Our design advantage:** a false trigger costs her one spoken question, not a family siren. The *cost* of a false alarm matters as much as the *rate* |
| **González-Cañete & Casilari, Sensors 2021** | The wrist overestimates falls because of *"jerky activity of the arms and hands"* | Confirms that wrist-only accelerometer detection is noisy, which is exactly why we verify afterwards rather than trusting the trigger |
| **Brew et al., JMIR 2022** (smartwatch app, 226 induced falls, 22 adults) | **77% sensitivity**, 99% specificity. Falls on the *same side* as the watch were detected more often | A benchmark for our stage fall: fall toward the watch side |

## 4. Safe-to-stand guidance (validates round-4 fix #27)

| Source | Guidance |
|---|---|
| **NHS, Falls (reviewed March 2025)** | *"Take a couple of minutes to check for any pain or injuries and see if you think you can get up."* If you can't: use an alarm, shout or bang on a wall, keep warm, change position every 30 min. **Call 999 if someone may have injured the head, back, neck or hip, or cannot get up** |
| **AARP** (search excerpt) | *"If something hurts as you move, it is best to remain on the floor and seek assistance."* |

⭐ Our conditional Do-Check (*"If there's no pain, get up slowly; if it hurts, stay there, I'm calling for help"*) **matches NHS guidance almost word for word**. That's a strong pitch line: *"The Do-Check follows NHS fall guidance."* And "cannot get up" means **call for help**, which maps to our LAAL.

## 5. India

| Paper | What it found | What it means for us |
|---|---|---|
| **LASI wave 1, 2017–18** (Barik et al. 2022; n=28,567, aged 60+) | Self-reported fall prevalence **12.5%** (13.6% of women vs 11.4% of men). Other LASI analyses report about 10.8–20% depending on the definition | The Indian baseline. Note it's *self-reported*, so if concealment is real, it's an undercount (our inference, labelled) |
| **LASI** (Thakkar et al. 2022) | **5.1% of Indians aged 60+ live alone**, about 1.4 crore people (our arithmetic; UNVERIFIED population base). *"Lone living older adults had a significantly higher likelihood of… falls and multiple falls"* | Our person is a real, sizeable, higher-risk group |
| **LASI** (Singh & Maurya 2022; aged 45+) | Fall prevalence for **women living alone: 27.6%**, vs 19.9% for women living with a spouse and children | ⭐ **Amma's exact profile, a woman living alone, has the highest fall rate in the table.** Pitch-grade |
| **Mohan et al., IJERPH 2025** (Kerala, qualitative, aged 65+ living alone because children migrated) | Distance makes parents anxious and lonely and creates "care gaps"; care flows "through virtual and in-person means" | Confirms the Rahul-in-Pune setup is a studied Indian pattern |

## 6. Night falls (round-4 fix #32)

- **Nocturia** (getting up at night to urinate) is consistently associated with falls: Stewart 1992 (*"an important risk factor for falls in ambulatory elderly"*), Vaughan 2010 (3+ episodes a night, RR 1.27), and a 2020 meta-analysis (Pesonen et al., J Urol).
- **Contradicting nuance:** Vlaeyen's video study found **no falls at night**; 62% were 7–10 am or 7–10 pm. That's a tiny sample in care homes, but it suggests **morning and evening transitions** are the peak, not 3 am. *Revise #32's wording:* "night-time bathroom trips are **a** recognised fall risk (nocturia studies), and morning and evening transitions are the peak in video evidence." Keep the morning-charging advice, but **don't** claim "night is the peak".

---

## What we can pick

1. **The Fleming quote, as the emotional core of the pitch:** *"I didn't want to use the call alarm… for fear of being taken into hospital."* That's the binary problem in a real 90-year-old's words.
2. **"Follows NHS fall guidance"** as the credibility line for the Do-Check.
3. **Kangas's 1 false alarm per 40 h** as the *target* for our wear test: a real published bar, not an invented one.
4. **Bianchi's ablation shape** (accelerometer only vs. + barometer) as the template for our own ablation table.
5. **The LASI "women living alone: 27.6%"** figure in the hook.

## What nobody built (from the literature)

- **Recovery verification after a fall.** The literature has lots of fall *detection* and some lie-to-stand *kinematics* (Schwickert 2016), but **no paper we found uses a get-up check to decide whether a reported "I'm OK" is true**. All the evaluation papers measure detection; none measure the *response* after it.
- **A middle tier.** Fleming's conclusion calls for *"work… on access and activation issues for design of call alarms"*. Nobody tested an option between "nothing" and "emergency".
- **Testing with actual elderly users** is still rare (UAlberta: none of 118 studies; Bagalà: the first real-fall benchmark was in 2012). We can't fix that in a hackathon, but saying so first is honest.

## What this changes for Suraksha (proposals; nothing edited until you agree)

1. **Fix the 80% claim in bible §1.** Use Fleming's wording and source (BMJ 2008), not the UAlberta paraphrase.
2. **Replace the UNVERIFIED killer facts** with: Fleming 80% / 97%; Tinetti 47%; Wild 11 of 20 died within a year; LASI women living alone 27.6%; Bagalà's 3–85 false alarms a day in the real world.
3. **Add "follows NHS fall guidance"** to the Do-Check (L4) and the challenge table.
4. **Set the wear-test pass bar:** ≤ 1 false trigger per 40 waking hours (the Kangas benchmark).
5. **Correct #32:** night is *a* risk (nocturia), but video evidence puts the peak at 7–10 am and 7–10 pm. The demo's 06:40 moment is *well chosen*; say so.
6. **Name the evidence for the Moving-Arm Trap:** Vlaeyen 2013, *"postfall phase was not characterized by inactive participants."*
7. **Barometer V2 stays**, with the honest note that wrist evidence is thin (one study) and our own noise measurement decides the threshold.
8. **Pitch-only lineage line:** *"Barometers have been shown to separate sitting from standing at 99.5% (Massé 2014). We point that at a new question: has she got back up?"*

## Sources

- Fleming J, Brayne C. Inability to get up after falling… BMJ 2008;337:a2227. [PMC2590903](https://pmc.ncbi.nlm.nih.gov/articles/PMC2590903/) (full text read)
- Tinetti ME et al. Predictors and prognosis of inability to get up after falls. JAMA 1993;269:65–70. [PMID 8416408](https://pubmed.ncbi.nlm.nih.gov/8416408/)
- Wild D et al. How dangerous are falls in old people at home? BMJ 1981;282:266. [PMID 6779979](https://pubmed.ncbi.nlm.nih.gov/6779979/); [JSTOR prognosis excerpt](https://www.jstor.org/stable/25566261)
- Vlaeyen E et al. Fall incidents unraveled… BMC Geriatr 2013;13:103. [PMC3850536](https://pmc.ncbi.nlm.nih.gov/articles/PMC3850536/) (full text read)
- Zhu Y et al. "I don't want to be a burden"… Front Public Health 2026. [PMC13433289](https://pmc.ncbi.nlm.nih.gov/articles/PMC13433289/)
- Massé F et al. Suitability of commercial barometric pressure sensors… Med Eng Phys 2014. [PMID 24485500](https://pubmed.ncbi.nlm.nih.gov/24485500/)
- Bianchi F et al. Barometric pressure and triaxial accelerometry-based falls event detection. IEEE TNSRE 2010. [PMID 20805056](https://pubmed.ncbi.nlm.nih.gov/20805056/)
- Jatesiktat P, Ang WT. An elderly fall detection using a wrist-worn accelerometer and barometer. IEEE EMBC 2017. [PMID 29059826](https://pubmed.ncbi.nlm.nih.gov/29059826/)
- Sabatini AM, Genovese V. Sensor fusion for vertical velocity and height. Sensors 2014. [PMC4179067](https://pmc.ncbi.nlm.nih.gov/articles/PMC4179067/)
- Manivannan A et al. Challenges and potential of barometric sensors. Sensors 2020. [PMC7731380](https://pmc.ncbi.nlm.nih.gov/articles/PMC7731380/)
- Bagalà F et al. Evaluation of accelerometer-based fall detection algorithms on real-world falls. PLoS One 2012. [PMC3353905](https://pmc.ncbi.nlm.nih.gov/articles/PMC3353905/)
- Kangas M et al. Sensitivity and false alarm rate… Gerontology 2014. [PMID 25138139](https://pubmed.ncbi.nlm.nih.gov/25138139/)
- Gordon LAN. Smart watches for NCDs in the ageing population (cites Chaudhuri's 42% false positives). Geriatrics 2018. [PMC6319218](https://pmc.ncbi.nlm.nih.gov/articles/PMC6319218/)
- Yasmin A et al. Enhancing real-world fall detection using commodity devices. Sensors 2025. [PMC12431052](https://pmc.ncbi.nlm.nih.gov/articles/PMC12431052/)
- González-Cañete FJ, Casilari E. Feasibility of smartwatches in fall detection. Sensors 2021. [PMC8004721](https://pmc.ncbi.nlm.nih.gov/articles/PMC8004721/)
- Brew B et al. Effectiveness of a smartwatch app in detecting induced falls. JMIR 2022. [PMC8981002](https://pmc.ncbi.nlm.nih.gov/articles/PMC8981002/)
- Barik M et al. Multimorbidity and falls among older adults in India (LASI). BMC Geriatr 2022. [PMC9167508](https://pmc.ncbi.nlm.nih.gov/articles/PMC9167508/)
- Thakkar S et al. Physical frailty and falls among older Indian adults (LASI). PLoS One 2022. [PMC9374260](https://pmc.ncbi.nlm.nih.gov/articles/PMC9374260/)
- Singh RR, Maurya P. Visual impairment and falls (LASI). BMC Public Health 2022. [PMC9746100](https://pmc.ncbi.nlm.nih.gov/articles/PMC9746100/)
- Mohan A et al. "Care beyond co-residence", Kerala. IJERPH 2025. [PMC12652767](https://pmc.ncbi.nlm.nih.gov/articles/PMC12652767/)
- Stewart RB et al. Nocturia: a risk factor for falls. JAGS 1992. [PMID 1447437](https://pubmed.ncbi.nlm.nih.gov/1447437/); Vaughan CP et al. 2010 [PMC3222329](https://pmc.ncbi.nlm.nih.gov/articles/PMC3222329/); Pesonen JS et al. 2020 [PMID 31347956](https://pubmed.ncbi.nlm.nih.gov/31347956/)
- Schwickert L et al. Lie-to-stand transfers with inertial sensors. Sensors 2016. [PMC5017442](https://pmc.ncbi.nlm.nih.gov/articles/PMC5017442/)
- [NHS: Falls](https://www.nhs.uk/conditions/falls/) (read in full)

## Couldn't confirm

- Wild 1981's exact *"half died within six months"* sentence. Our index truncated the abstract; the JSTOR excerpt gives 11 of 20 within a year. **Use 11 of 20.**
- **India-specific qualitative evidence on concealing falls from children.** The closest is China (Zhu 2026). That's the one gap the real conversations (track 9) can fill.
- Chaudhuri's 42% false-positive figure was read via a review, not the primary paper.
- The wrist barometer noise floor on a Galaxy Watch 4. No paper; it has to be measured.
