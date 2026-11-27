"""The fall conversation on the watch, with the device key (bible v5 §17a step 7)."""

import base64
import importlib

import pytest
from fastapi.testclient import TestClient

from agents import companion
from agents.schemas import CompanionReply
from voice.transcribe import Transcript

KEY = {"x-ally-device-key": "device-key"}
WAV = base64.b64encode(b"RIFF....fake").decode()


@pytest.fixture
def client(monkeypatch, seeded, pushes, sfn):
    monkeypatch.setenv("ALLY_DEV_TOOLS", "1")
    import auth
    import config

    importlib.reload(config)
    importlib.reload(auth)
    import app as app_module

    importlib.reload(app_module)

    async def fake_tts(text, language):
        return {"audio_base64": base64.b64encode(text.encode()).decode(), "mime_type": "audio/mpeg"}

    heard: list[str] = []

    async def fake_stt(raw, language):
        text = heard.pop(0) if heard else ""
        return Transcript(text=text, language="hi-IN", duration_sec=1.2, provider="test")

    async def fake_respond(parent_id, text, *, investigating, source):
        reply = CompanionReply(say="अच्छा।", language="hi-IN", parent_says_okay="theek" in text)
        return reply, companion.RunEffects(), type("G", (), {"denied_tools": []})()

    monkeypatch.setattr(app_module.speech, "synthesize", fake_tts)
    monkeypatch.setattr(app_module.stt, "transcribe", fake_stt)
    monkeypatch.setattr(companion, "respond", fake_respond)
    c = TestClient(app_module.app)
    c.heard = heard
    return c


def test_fall_returns_the_question_as_audio(client):
    res = client.post("/suraksha/device/fall", headers=KEY)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["asked_parent"] and "गिर" in body["say"] and body["audio_base64"]


def test_spoken_theek_hoon_goes_through_the_vote_and_comes_back_as_audio(client):
    client.post("/suraksha/device/fall", headers=KEY)
    client.heard.append("theek hoon")
    res = client.post("/suraksha/device/answer", json={"audio_base64": WAV}, headers=KEY)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["fall_tier"] == "PEELA" and body["transcript_in"] == "theek hoon"
    assert "मान ली" in body["say"] and body["audio_base64"]


def test_unheard_answer_asks_her_to_repeat(client):
    client.post("/suraksha/device/fall", headers=KEY)
    res = client.post("/suraksha/device/answer", json={"audio_base64": WAV}, headers=KEY).json()
    assert res["stt_empty"] and "फिर से" in res["say"]


def test_pending_messages_come_with_audio(client):
    client.post("/suraksha/device/fall", headers=KEY)
    msgs = client.get("/suraksha/device/pending", headers=KEY).json()["messages"]
    assert msgs and all(m["audio_base64"] for m in msgs)
    assert client.get("/suraksha/device/pending", headers=KEY).json()["messages"] == []  # claimed once


def test_device_routes_need_the_key(client):
    assert client.post("/suraksha/device/fall", headers={"x-ally-device-key": "nope"}).status_code == 401
    assert client.get("/suraksha/device/pending").status_code == 401
