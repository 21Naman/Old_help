# Track 7 — Hardware and stack feasibility

*26 Nov 2026. Status: **done, waiting for your review.***

*Method: built-in browser on primary docs, namely Samsung's spec sheet (Newsroom India plus Samsung SG/CA product pages); Android Developers (foreground service types, the `Sensor` reference); AWS docs (Transcribe supported languages, Polly available voices, Polly generative voices and regions); the AWS ML blog plus a Braintrust KB note on the Nova 2 model IDs. Cross-checked against our own repo (`wear-os/app/build.gradle.kts`, `AndroidManifest.xml`, `infra/ally_stack.py`, `ally/voice/speech.py`). The Bedrock models-by-region page renders by script and came back empty, so the Nova check relies on the model ID and on our repo's existing smoke test, not on a region table.*

## The one-line finding

**Everything the v3 bible needs exists on a Galaxy Watch4 and in us-east-1. The barometer is confirmed in Samsung's own spec.** Two corrections: **Kannada speech-to-text *is* available** (we said it was limited), but **Polly can't speak Kannada**. And two unknowns only your watch can answer: whether Watch4 exposes the off-body sensor, and the real barometer noise and battery drain.

---

## 1. Galaxy Watch4: what the hardware gives us

From Samsung's official spec table (Newsroom India; the same sensor list on the SG/CA product pages):

| Spec | Watch4 | What it means for Suraksha |
|---|---|---|
| **Sensors** | BioActive (optical HR + electrical heart + BIA), **Accelerometer, Barometer, Gyro, Geomagnetic**, Light | ✅ **V2 barometer is real hardware.** ✅ The **gyro + geomagnetic** sensors enable Philips' expired **360° drop rule** (track 3). ✅ PPG for contact and HR flags |
| **Battery** | 44 mm: **361 mAh**; 40 mm: **247 mAh** (typical); wireless charging | The 40 mm model has about a third less battery. **Recommend the 44 mm for Amma**, and measure drain under our sensor load (#32) |
| **Durability** | **5ATM + IP68**, MIL-STD-810G | ✅ Shower-safe, which answers the bathroom objection (#22) with Samsung's own rating |
| **Connectivity** | **LTE variant**, BT 5.0, Wi-Fi 2.4/5 GHz, GPS | The LTE model works without the phone nearby, so the watch is the whole interface (answers the DrRing review in track 4). The BT model needs the paired phone in range |
| **Processor / memory** | Exynos W920 dual-core, 1.5 GB RAM, 16 GB | Enough for an on-watch Kotlin vote and cached Hindi audio (ticket 15) |
| **OS** | Wear OS Powered by Samsung | Standard Android sensor APIs apply |

## 2. Android / Wear OS APIs

| Need | API | Status | Notes |
|---|---|---|---|
| Barometer stream | `Sensor.TYPE_PRESSURE` (API 20+) | ✅ Exists | Not yet used in our code |
| Step events (not batched counts) | `Sensor.TYPE_STEP_DETECTOR` (API 20+) | ✅ Exists | Fixes #6 (counter latency). Needs `ACTIVITY_RECOGNITION` (already declared) |
| Off-body | `Sensor.TYPE_LOW_LATENCY_OFFBODY_DETECT` (**API 26+**) | ⚠️ The API exists; **whether Watch4 exposes it is device-specific** | **One-line test on your watch:** `sensorManager.getDefaultSensor(TYPE_LOW_LATENCY_OFFBODY_DETECT) != null`. Fallback: PPG contact via Health Services |
| Run sensors when the app isn't open (#10) | Foreground service type **`health`**; manifest permission **`FOREGROUND_SERVICE_HEALTH`**; pass `FOREGROUND_SERVICE_TYPE_HEALTH` | ✅ Feasible | Runtime prerequisite: declare **`HIGH_SAMPLING_RATE_SENSORS`** (📂 **already in our manifest**) *or* hold BODY_SENSORS/ACTIVITY_RECOGNITION. **Caveat from the docs:** to *start* a health service that uses body sensors **from the background** you need **`BODY_SENSORS_BACKGROUND`** (API 33–35). Accelerometer and barometer don't need body-sensor permission; heart rate does |
| Our targets | 📂 `compileSdk 35`, `targetSdk 35`, `minSdk 30`, Health Services client 1.0.0 | — | Targeting SDK 35 means the foreground-service *type* rules above **are enforced**. The service must declare `health` or it will crash on start |

**Design implication:** run the always-on fall trigger (accelerometer + barometer) in the health foreground service; read heart rate **only after a fall** (concern flags), while the app is foregrounded by the alert. That avoids depending on `BODY_SENSORS_BACKGROUND` for the core path.

## 3. AWS voice stack

### Speech-to-text (Amazon Transcribe)

| Language | Code | Streaming | Notes |
|---|---|---|---|
| **Hindi** | hi-IN | ✅ batch + streaming | Full feature set incl. number transcription |
| **English (Indian)** | en-IN | ✅ batch + streaming | |
| **Kannada** | kn-IN | ✅ batch + streaming\* | ⭐ **Correction to bible #35:** Kannada *is* supported |
| Tamil, Telugu, Marathi, Bengali, Gujarati, Malayalam, Punjabi, Odia | ta/te/mr/bn/gu/ml/pa/or-IN | ✅ batch + streaming\* | |

\* The asterisk means *"Streaming… not available in"* Cape Town, Tokyo, Malaysia, Thailand and Ningxia. **us-east-1 is fine.**

### Text-to-speech (Amazon Polly)

| Language | Voices | Engines |
|---|---|---|
| **Hindi (hi-IN)** | **Kajal** (F), **Arjun** (M), **Kiara** (F), Aditi (F) | Kajal: **generative + neural**; Arjun, Kiara: generative; Aditi: standard |
| English (Indian) | Kajal, Arjun, Kiara, Aditi, Raveena | Mixed |
| **Kannada / Tamil / Telugu / other Indian** | **None** | — |

**Generative engine regions:** us-east-1, us-west-2, ap-southeast-1 (Singapore), ap-southeast-2, GovCloud. **Not Mumbai (ap-south-1).** 📂 Our stack runs in us-east-1 with failover to us-west-2, both supported, and `speech.py` already falls back to neural on `EngineNotSupportedException`.

**Implication:** Suraksha can **understand** Kannada, Tamil and others today, but can only **speak** Hindi or English through Polly. Honest product line: *"She can speak Kannada to it; it answers in Hindi or English for now."* Indian-language TTS from other providers is out of scope and would break the "all on AWS" story.

### Reasoning (Amazon Bedrock, Nova 2 Lite)

- Model ID `us.amazon.nova-2-lite-v1:0` is confirmed as the **cross-region inference profile** (AWS migration blog).
- Known pitfall: IAM must allow the **inference-profile resource**, not only the foundation model (Braintrust KB). 📂 **Our CDK already does both**, for the primary *and* failover regions (`infra/ally_stack.py:280–284`).
- Region-by-region availability wasn't confirmed this session (the docs page is script-rendered). `ally/scripts/smoke_bedrock.py` is the authoritative check; run it once in your account before the event.

## 4. What only *your* watch can tell us (do this first)

| Unknown | How to measure | Time |
|---|---|---|
| Off-body sensor present on Watch4? | `getDefaultSensor(TYPE_LOW_LATENCY_OFFBODY_DETECT)` and log the result | 5 min |
| **Barometer noise floor at the wrist** (open flaw #5) | Watch still on a table 10 min, then on the wrist sitting/standing; log hPa at 5 Hz; compute std dev and the stand-vs-floor delta | 30 min |
| Battery % per hour, armed (#32) | Full charge → armed service → log every 30 min for 8 h | 8 h, passive |
| Step-detector latency | Walk 10 steps; log event timestamps | 10 min |
| Speaker audibility in a bathroom (#25) | Play cached Kajal audio at max volume behind a closed door | 5 min |

## What this changes for Suraksha (proposals; nothing edited until you agree)

1. **Bible §6 L1:** replace *"UNVERIFIED for your exact model"* for the barometer with **"confirmed in Samsung's Watch4 spec"**. Off-body stays "test on device".
2. **Recommend the 44 mm (361 mAh) model** in onboarding and the demo kit; note that the 40 mm has 247 mAh.
3. **Add the gyro/magnetometer 360° drop rule** to L2, since Watch4 has both sensors.
4. **Foreground service spec (ticket 16):** type `health`, `FOREGROUND_SERVICE_HEALTH`, `HIGH_SAMPLING_RATE_SENSORS` (already declared); heart rate only after a fall to avoid `BODY_SENSORS_BACKGROUND`.
5. **Correct #35 (language):** *"Understands Hindi, English, Kannada, Tamil, Telugu, Marathi, Bengali and more (Transcribe); speaks Hindi and English (Polly)."* That's a stronger, honest answer to a Bengaluru judge.
6. **Region note for Q&A:** us-east-1 because Polly's generative voices aren't in Mumbai; Singapore is the closest region if latency or data location matters.
7. **Make "measure on the watch" a first-hour checklist** (§4 above) before any Kotlin is written.

## Sources

- [Samsung Newsroom India: Galaxy Watch4 / Watch4 Classic spec table](https://news.samsung.com/in/galaxy-watch4-and-galaxy-watch4-classic-reshaping-the-smartwatch-experience) (read)
- [Samsung SG: Galaxy Watch4 Bluetooth 44 mm (sensor list)](https://www.samsung.com/sg/business/watches/galaxy-watch/galaxy-watch4-44mm-bt-sm-r870nzsaasa/) (snippet)
- [Android Developers: Foreground service types](https://developer.android.com/develop/background-work/services/fgs/service-types) (read: the Health section)
- [Android Developers: `Sensor` reference](https://developer.android.com/reference/android/hardware/Sensor) (`TYPE_LOW_LATENCY_OFFBODY_DETECT` API 26, `TYPE_PRESSURE`, `TYPE_STEP_DETECTOR`)
- [AWS: Transcribe supported languages](https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html) (read; Indian rows and the asterisk footnote)
- [AWS: Polly available voices](https://docs.aws.amazon.com/polly/latest/dg/available-voices.html) (read; en-IN and hi-IN rows)
- [AWS: Polly generative voices and regions](https://docs.aws.amazon.com/polly/latest/dg/generative-voices.html) (read)
- [AWS ML blog: Migrate from Nova 1 to Nova 2](https://aws.amazon.com/blogs/machine-learning/migrate-from-amazon-nova-1-to-amazon-nova-2-on-amazon-bedrock/) (snippet); [Braintrust KB: Nova 2 inference-profile IAM](https://docs.braintrust.dev/kb/bedrock-nova-2-inference-profile-iam-and-custom-provider-setup) (snippet)
- Repo: `wear-os/app/build.gradle.kts`, `wear-os/app/src/main/AndroidManifest.xml`, `infra/ally_stack.py:280–284`, `ally/voice/speech.py`

## Couldn't confirm

- **Off-body sensor on Watch4.** It must be tested on the device.
- **Watch4 battery hours under our load.** Samsung's mAh figure isn't hours; measure it.
- **Nova 2 Lite region list.** Rely on `smoke_bedrock.py` in your account.
- **Whether Transcribe's language identification accepts Kannada** in the same `LanguageOptions` set as en-IN/hi-IN for streaming. Not checked; test before claiming it on stage.
