"""Table tests for the Get-Up Vote (bible v5 §6 L4)."""

from getup.vote import FallEvidence, HeartSample, PressureSample, decide

P_REF = 920.00  # her wrist pressure in the 10 s before the fall


def standing(start=0, end=30, arm_var=0.2):
    return [PressureSample(t, P_REF + 0.01, arm_var) for t in range(start, end + 1, 2)]


def on_floor(start=0, end=40, arm_var=0.2):
    # wrist ~0.8 m lower than standing -> ~0.09 hPa higher pressure
    return [PressureSample(t, P_REF + 0.09, arm_var) for t in range(start, end + 1, 2)]


def test_hero_case_theek_hoon_but_still_down_is_peela():
    ev = FallEvidence(
        says_ok=True, reply_text="theek hoon", reply_seconds=1.2,
        p_ref_hpa=P_REF, pressure=on_floor(arm_var=4.0),  # she waves an arm on the floor
        step_events=0, heart=[HeartSample(t, 104) for t in range(0, 40, 5)],
    )
    r = decide(ev)
    assert r.tier == "PEELA"
    assert r.votes == {"words": "up", "height": "down", "movement": "down", "voice": "abstain"}


def test_got_up_and_walked_is_hara_and_nobody_told():
    ev = FallEvidence(says_ok=True, reply_text="haan theek hoon, chal rahi hoon", reply_seconds=2.0,
                      p_ref_hpa=P_REF, pressure=standing(), step_events=9)
    r = decide(ev)
    assert r.tier == "HARA"
    assert r.votes["height"] == "up" and r.votes["movement"] == "up"


def test_waving_arm_at_standing_height_does_not_count():
    ev = FallEvidence(says_ok=True, reply_text="theek hoon", reply_seconds=1.0,
                      p_ref_hpa=P_REF, pressure=standing(arm_var=5.0), step_events=0)
    assert decide(ev).votes["height"] == "down"
    assert decide(ev).tier == "PEELA"


def test_missing_sensors_abstain_and_count_as_not_up():
    ev = FallEvidence(says_ok=True, reply_text="theek hoon", reply_seconds=1.0, step_events=7)
    r = decide(ev)
    assert r.votes["height"] == "abstain" and r.votes["voice"] == "abstain"
    assert r.tier == "PEELA"  # only 1 body vote, abstains don't help


def test_she_says_she_cant_get_up_is_laal():
    ev = FallEvidence(says_ok=False, reports_unwell=True, reply_text="uth nahi pa rahi", reply_seconds=1.5)
    assert decide(ev).tier == "LAAL"


def test_pain_words_with_ok_still_laal():
    ev = FallEvidence(says_ok=True, reply_text="theek hoon bas thoda dard hai", reply_seconds=2.5,
                      p_ref_hpa=P_REF, pressure=standing(), step_events=8)
    r = decide(ev)
    assert r.tier == "LAAL" and "pain_words" in r.flags


def test_silence_past_limit_is_laal():
    assert decide(FallEvidence(says_ok=None, silent_seconds=95)).tier == "LAAL"


def test_waiting_for_answer_is_not_resolved():
    assert decide(FallEvidence(says_ok=None, silent_seconds=10)).tier == "PEELA"


def test_sustained_high_heart_rate_raises_to_laal():
    ev = FallEvidence(says_ok=True, reply_text="haan main bilkul theek hoon", reply_seconds=2.0,
                      p_ref_hpa=P_REF, pressure=standing(), step_events=8,
                      heart=[HeartSample(t, 140) for t in range(0, 30, 5)])
    r = decide(ev)
    assert r.tier == "LAAL" and "hr_high" in r.flags


def test_drop_spin_offwrist_charging_are_grey():
    assert decide(FallEvidence(dropped=True)).tier == "GREY"
    assert decide(FallEvidence(spin_deg=400)).tier == "GREY"
    assert decide(FallEvidence(on_wrist=False)).tier == "GREY"
    assert decide(FallEvidence(charging=True)).tier == "GREY"


def test_voice_vote_uses_her_usual_rate():
    slow = FallEvidence(says_ok=True, reply_text="haan main theek hoon beta", reply_seconds=6.0, usual_wpm=105)
    normal = FallEvidence(says_ok=True, reply_text="haan main theek hoon beta", reply_seconds=2.5, usual_wpm=105)
    assert decide(slow).votes["voice"] == "down"
    assert decide(normal).votes["voice"] == "up"
