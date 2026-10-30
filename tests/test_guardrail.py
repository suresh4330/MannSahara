import pytest
from agents.guardrail import Guardrail
from config.templates import DISCLAIMER, CRISIS_SELF, CRISIS_THIRD, REFERRAL, FALLBACK
from tools.coping_tools import TECHNIQUES


def test_guardrail_diagnosis():
    g = Guardrail()
    ok_unsafe, v_unsafe = g.check("Based on what you said, you have depression.", 1)
    assert not ok_unsafe
    assert "diagnosis" in v_unsafe

    ok_safe, v_safe = g.check("It sounds like you have had a really exhausting and difficult week.", 1)
    assert ok_safe
    assert v_safe == []


def test_guardrail_medication():
    g = Guardrail()
    ok_unsafe, v_unsafe = g.check("You should try taking 25 mg of sertraline for anxiety.", 1)
    assert not ok_unsafe
    assert "medication" in v_unsafe

    ok_safe, v_safe = g.check("Staying hydrated and having regular meals can help your daily energy.", 1)
    assert ok_safe
    assert v_safe == []


def test_guardrail_method_detail():
    g = Guardrail()
    ok_unsafe, v_unsafe = g.check("A lethal dose of that medication would cause severe harm.", 1)
    assert not ok_unsafe
    assert "method_detail" in v_unsafe

    ok_safe, v_safe = g.check("Let's take a moment to focus on slow, steady breaths.", 1)
    assert ok_safe
    assert v_safe == []


def test_guardrail_false_contact_claim():
    g = Guardrail()
    ok_unsafe, v_unsafe = g.check("Don't worry, I have contacted campus counselor for you.", 1)
    assert not ok_unsafe
    assert "false_contact_claim" in v_unsafe

    ok_safe, v_safe = g.check("You can reach out to the campus counselor at your college.", 1)
    assert ok_safe
    assert v_safe == []


def test_guardrail_therapist_claim():
    g = Guardrail()
    ok_unsafe, v_unsafe = g.check("As your counselor, I think you should do this.", 1)
    assert not ok_unsafe
    assert "therapist_claim" in v_unsafe

    ok_safe, v_safe = g.check("I am an AI wellbeing assistant and not a substitute for therapy.", 1)
    assert ok_safe
    assert v_safe == []


def test_guardrail_minimizing():
    g = Guardrail()
    ok_unsafe, v_unsafe = g.check("It's not that bad, just cheer up!", 1)
    assert not ok_unsafe
    assert "minimizing" in v_unsafe

    ok_safe, v_safe = g.check("It makes sense that you are feeling so heavy right now.", 1)
    assert ok_safe
    assert v_safe == []


def test_guardrail_empty_and_length():
    g = Guardrail()
    ok_empty, v_empty = g.check("   ", 1)
    assert not ok_empty
    assert "empty" in v_empty

    ok_long, v_long = g.check("word " * 300, 1)
    assert not ok_long
    assert "too_long" in v_long


def test_fixed_templates_pass_guardrail():
    g = Guardrail()
    # Disclaimer
    ok, v = g.check(DISCLAIMER, 0)
    assert ok, f"DISCLAIMER failed: {v}"

    # Crisis self and third formatted
    mock_contacts = "- Tele-MANAS: 14416\n- Emergency: 112"
    ok, v = g.check(CRISIS_SELF.format(contacts=mock_contacts), 3)
    assert ok, f"CRISIS_SELF failed: {v}"

    ok, v = g.check(CRISIS_THIRD.format(contacts=mock_contacts), 3)
    assert ok, f"CRISIS_THIRD failed: {v}"

    # Referral
    ok, v = g.check(REFERRAL.format(campus="Campus Cell: 011-2345"), 2)
    assert ok, f"REFERRAL failed: {v}"

    # Fallbacks
    for lvl, text in FALLBACK.items():
        ok, v = g.check(text, lvl)
        assert ok, f"FALLBACK[{lvl}] failed: {v}"


def test_coping_techniques_pass_guardrail():
    g = Guardrail()
    for name, text in TECHNIQUES.items():
        ok, v = g.check(text, 1)
        assert ok, f"Technique {name} failed guardrail: {v}"
