# Ally

Family care for an aging parent, **without making her feel watched**.

> Most days, Ally says nothing at all. That's the point.

Amma (72, Bengaluru, speaks Hindi) talks to Ally on a tablet and wears a watch, keeps her phone on her, or both. Her children, Rahul (Pune) and Priya (Bengaluru), get a calm dashboard. They only get a push notification when something is actually wrong. Amma decides what they may know, by voice.

## What it does

| Moment | What happens | Built with |
|---|---|---|
| First movement of the day | The watch or phone posts `wake` (once per day, whichever is first); Ally speaks a ≤3-sentence morning check-in grounded only in real data; "after I wake up" reminders are scheduled | Postgres · Groq · Edge TTS |
| Amma talks | Wispr Flow (Groq Whisper fallback) → Strands companion agent with tools → typed `CompanionReply` → Edge neural voice speaks | Wispr Flow · Strands Agents · Groq · edge-tts |
| Any tool call | A Strands `BeforeToolCallEvent` hook asks Cedar first; every allow/deny is written to an audit log Amma can read | Strands hooks · Cedar · Postgres |
| Not up by her usual time | The one-minute sweep opens an investigation and asks **Amma first** | `/ally/cron/sweep` |
| Possible fall (watch or phone) | Ask her first, short window; a second report from the other device is deduped | Postgres |
| No reply, or she says she's unwell | A deterministic gate → LLM judge (severity + confidence) → tier policy in code | Groq → Gemini |
| Family escalation | Rahul → timeout → Priya → ask Amma about the neighbour → neighbour only if Cedar allows (rings the guard handset) → otherwise notify everyone; replies come back from notification buttons | `escalation/machine.py` · Web Push |
| Family asks "Did she sleep okay?" | Answers only from records returned by tools this turn, or "not sure" / "private" | Strands · Cedar |

## Architecture

```
Web (static) ── Ally JWT ──┐      Wear OS watch / Android phone ── device key ──┐
                           ▼                                                     ▼
                FastAPI (uvicorn, Render Docker) — routes under /ally and /suraksha
                  ├─ Strands agents → LiteLLM → Groq llama-3.3-70b (Gemini 2.5 Flash fallback)
                  ├─ Cedar ConsentGuard on every tool call
                  ├─ Wispr Flow STT (Groq Whisper fallback) · edge-tts voices
                  ├─ escalation workflow: state on the ESC row, timeouts via the sweep
                  └─ SQLAlchemy single table (Postgres on Neon, SQLite locally/tests)
cron-job.org (1 min) → POST /ally/cron/sweep: reminders · wake window · investigation + escalation timeouts
```

**Design rules:**
- No silent fallbacks. If both LLM providers fail, the API returns `llm_unavailable` and the UI says so.
- The model decides language and judgement; code decides actions.
- Safety can't be switched off; conversations are never shared.
- Only history before today is simulated and labelled. Today is live.
- Degrade loudly: a sick dependency shows up in `/health/deep`, never as a quietly worse answer.

## Local development

```bash
cd ally
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env              # ALLY_DEV_TOOLS=1 enables the dev identity switcher
python -m pytest -q               # offline tests (in-memory SQLite, no network)
python scripts/seed.py --users --password 'pick-one'
python scripts/smoke_llm.py       # live LLM check: every schema, exits non-zero on failure
uvicorn app:app --reload --port 8002
```

`DATABASE_URL` empty means SQLite at `ally/ally.db`. `ALLY_INPROC_SCHEDULER=1` runs the sweep inside
the API so timeouts fire without a cron.

Simulate devices:

```bash
curl -X POST localhost:8002/ally/device -H 'X-Ally-Device-Key: <key>' -H 'content-type: application/json' -d '{"kind":"fall","source":"phone"}'
```

## Deploy

See the root README's *Deploy (Render, free)* section and [`../render.yaml`](../render.yaml).

## Limitations
- Ally is not an emergency service. The family screen always shows 112.
- iOS web push requires the app installed to the home screen and has no action buttons; the respond page covers it.
