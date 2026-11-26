# Suraksha

**Family care for an aging parent — without watching her.**

> Most days, Suraksha says nothing at all. That’s the point.

Suraksha is a **hardware-first, agentic companion** for aging at home: Galaxy Watch and/or an Android phone + tablet voice + long-term memory + proactive care + consent-aware family escalation — running entirely on **free services** (Render, Neon Postgres, Groq / Gemini, Wispr Flow, Edge TTS).

Amma (72, Bengaluru) wears the watch or keeps her phone on her, and talks to Suraksha in Hindi or Hinglish. Rahul and Priya get a calm family view. They are notified only when something is actually wrong — and only the person who can show up is asked first.

**Build story:** [`docs/suraksha-build-story.md`](docs/suraksha-build-story.md) (describes the original AWS build)  
**API / agent runbook:** [`ally/README.md`](ally/README.md)

---

## The problem

Adult children living in another city do not need a live feed of their parent’s day. Cameras and always-on dashboards steal independence. Silence leaves families guessing. Panic buttons only help if she can reach them and wants to press them.

Suraksha sits in between: it learns what is normal for Amma, talks to **her** first, remembers what she asked for, enforces what she said to keep private, and only then coordinates the person who can actually help.

---

## Who it’s for

| Who | What they get |
| --- | --- |
| **Parent (Amma)** | Watch + tablet companion; speak a task; almost no learning curve |
| **Family (Rahul, Priya)** | Calm home/command views; push only when needed; one-tap respond |
| **Nearby help (optional)** | Guard / neighbour path only if Cedar allows |

Suraksha is **not** an emergency service replacement. Family screens always surface **112**.

---

## What Suraksha does

| Capability | Detail |
| --- | --- |
| **Agentic voice companion** | Speak a task — reminders, check-ins, errands, health notes, consent. Tools run; it doesn’t only chat. |
| **All-in-one memory** | Single-table facts in Postgres: day log, mood, alerts, reminders, consent, audit — not a disposable chat blob. |
| **Hardware-first** | Galaxy Wear OS watch (wake, heart rate, fall) and/or the Android phone app (wake, steps, fall). Tablet for conversation. |
| **Fall detection** | Watch or phone signals (deduped if both fire) open investigation / scripts; family chain only after policy and judgement. |
| **Proactive care** | A sweep every minute (external cron or in-process): due reminders, wake-window misses, investigation timeouts. |
| **Ask her first** | Missed wake or worrying signal → Suraksha checks in with Amma before looping family. |
| **Consent that blocks tools** | Spoken privacy rules → Cedar templates → `ConsentGuard` on every tool call; audit she can read. |
| **Evidence-only family Q&A** | “Did she sleep okay?” → answers only from tool-returned records, or not sure / private. |
| **Family escalation** | Database-driven workflow: Rahul → timeout → Priya → ask about neighbour → neighbour if allowed → failsafe notify-all. |
| **Quiet by design** | Most days: no noise. Engagement is not the goal. |
| **Explore world (demo)** | 3D wardstone / gallery experience for storytelling. |

### Example moments

| Moment | What happens | Runs on |
| --- | --- | --- |
| First movement of the day | Watch or phone posts `wake`; short morning check-in; “after I wake” reminders schedule | FastAPI · Postgres · Groq · Edge TTS |
| Amma speaks a task | Wispr Flow → companion agent + tools → typed reply → Edge TTS speaks | Wispr Flow · Groq · Edge TTS |
| “Don’t tell Priya about my health” | Fixed Cedar `forbid` template; she confirms; tools blocked thereafter | Cedar · Postgres audit |
| Not up by usual time | Sweep opens investigation; asks Amma first | cron-job.org → `/ally/cron/sweep` |
| Fall / unwell / no reply | Gate → LLM judge → tier policy in code | Groq (Gemini fallback) |
| Family needed | Workflow asks each person in turn; Web Push accept/decline | Postgres · Web Push (VAPID) |
| Family asks a question | Family Q&A agent; Cedar principal = asker | Groq · Cedar · Postgres |

---

## Architecture

```
Galaxy Watch (Wear OS)   Android phone app   Parent tablet / Family web (Render static site)
        │                       │                         │  JWT (Ally-issued)
        └── device key ─────────┴──────────┬──────────────┘
                                           ▼
                        Ally API — FastAPI on Render (Docker, free)
                          ├─ companion · family Q&A · judge · morning (Strands agents)
                          ├─ Cedar ConsentGuard — before every tool
                          ├─ escalation workflow (state on the escalation row)
                          └─ /ally/cron/sweep ◄── cron-job.org, every minute
                                           │
        ┌───────────────┬──────────────────┼──────────────────┬────────────────┐
   Neon Postgres   Groq (Llama 3.3)    Wispr Flow STT     Edge neural TTS    Web Push
   single table    → Gemini fallback   → Groq Whisper
```

**Design rules**

- No silent LLM fallbacks to fake text — if both providers fail the UI shows `llm_unavailable`.
- The model decides language and judgement; **code** decides actions.
- Safety cannot be switched off; conversations are never shared as a feed.
- History before today may be simulated and labelled; **today is live**.

---

## Services (all free tiers)

| Need | Service | Replaces |
| --- | --- | --- |
| API hosting | **Render** web service (Docker) | Lambda · API Gateway · ECR |
| Web hosting | **Render** static site | Amplify Hosting |
| Database | **Neon** Postgres (SQLite locally) | DynamoDB |
| LLM | **Groq** `llama-3.3-70b-versatile`, **Gemini** `2.5-flash` fallback (via LiteLLM) | Bedrock |
| Speech-to-text | **Wispr Flow**, Groq Whisper fallback | Transcribe |
| Text-to-speech | **Edge neural voices** (`edge-tts`) | Polly |
| Scheduler | **cron-job.org** → `POST /ally/cron/sweep` | EventBridge |
| Escalation workflow | `ally/escalation/machine.py` | Step Functions |
| Sign-in | Ally-issued JWT (bcrypt passwords) | Cognito |
| Secrets | Render environment variables | Secrets Manager |

---

## Product surfaces (web)

| Route | Audience | Purpose |
| --- | --- | --- |
| `/` | Everyone | Landing — problem, how it works, architecture, watch story |
| `/parent` | Amma | Tablet companion — talk, tasks, check-ins |
| `/parent/privacy` | Amma | What was shared; consent / audit |
| `/home` | Family | Calm family dashboard |
| `/command` | Family | Timeline / command center |
| `/family/respond` | Family | Push landing — accept / decline escalation |
| `/guard` | Nearby help | Guard handset surface |
| `/explore` | Demo | 3D wardstone / gallery world |

---

## Repository layout

```
ally/          Agentic API — agents, policy (Cedar), scoring, store, escalation,
               proactive, voice, tests
web/           Next.js (static export) — landing, parent, family, command, guard, explore
wear-os/       Kotlin · Compose — watch UI, fall / wake / vitals
phone/         Kotlin · Compose — Android phone app: fall / wake / steps (foreground service)
render.yaml    Render Blueprint for the API and the web app
docs/          Build story
backend/       Legacy Rakshak plumbing (not deployed; reference only)
```

---

## Local development

### Prerequisites

- Python 3.11+ and Node.js 20+
- Free API keys: Groq (and optionally Gemini, Wispr Flow) for live AI turns — everything else runs without keys
- Optional: Android Studio / JDK 17 + Android SDK for the watch and phone apps

### Agent API (`ally/` · port `8002`)

```bash
cd ally
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env               # fill GROQ_API_KEY and the secrets; DATABASE_URL empty = SQLite
python -m pytest -q                # offline tests, no network
python scripts/seed.py --users --password 'pick-a-password'
python scripts/smoke_llm.py        # live LLM check: every schema, exits non-zero on failure
uvicorn app:app --reload --port 8002
```

With `ALLY_INPROC_SCHEDULER=1` the per-minute sweep runs inside the API, so reminders, wake checks
and escalation timeouts work locally without a cron.

### Web (`web/` · port `3000`)

```bash
cd web
cp .env.local.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) · `/parent` · `/home` · `/command`.

Reset a demo day (keeps profile, family, consent, audit, labelled history):

```bash
python ally/scripts/reset_day.py --yes
```

### Watch and phone

Both post the same events to `POST /ally/watch` (or `/ally/device`) with header `X-Ally-Device-Key`;
the phone adds `"source": "phone"`. Wear both or either — the server records one wake per day and one
fall per 10-minute window.

- Watch: [`wear-os/README.md`](wear-os/README.md) — set `ALLY_API` and the device key in `local.properties`.
- Phone: [`phone/README.md`](phone/README.md) — API URL and device key are entered in the app's settings.

---

## Deploy (Render, free)

1. **Neon:** create a free project and copy the connection string.
2. **Keys:** Groq API key, Gemini API key (Google AI Studio), Wispr Flow API key (optional).
3. **VAPID keys:** `python ally/scripts/gen_vapid.py`.
4. **Render:** *New → Blueprint* on this repo. It reads [`render.yaml`](render.yaml) and creates
   `suraksha-api` and `suraksha-web`. Fill the prompted values: `DATABASE_URL`, the API keys, VAPID keys,
   `ALLY_SEED_PASSWORD`, `PUBLIC_WEB_URL` / `CORS_ORIGINS` (the web URL), and on the web service
   `NEXT_PUBLIC_SURAKSHA_API_URL` (the API URL).
5. **Seed:** from the API service's Shell tab, run `python scripts/seed.py --users`.
6. **Scheduler:** on [cron-job.org](https://cron-job.org) add a job every minute:
   `POST https://<api>.onrender.com/ally/cron/sweep` with header `X-Cron-Secret: <ALLY_CRON_SECRET>`.
   This also keeps the free instance from sleeping.
7. **Devices:** give the watch and phone the API URL and `ALLY_DEVICE_KEY` (or per-device keys).

---

## Limitations

- Not a medical device, EMR, or replacement for emergency services.
- iOS web push may require home-screen install; respond page covers action buttons.
- Render's free web service sleeps after 15 idle minutes; the every-minute cron keeps it awake. If the cron stops, the first request takes ~30–60 s.
- Free LLM tiers are rate-limited (Groq ~30 requests/minute) — ample for one family.
- Phone-only users get no heart rate or SpO₂; the phone is also less reliable for falls when it isn't on her.
- Physical watch and phone sensors cannot be emulated in the browser; simulate events with `curl` against `/ally/watch`.

---
