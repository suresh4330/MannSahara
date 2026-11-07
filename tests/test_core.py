import os
os.environ["LLM_PROVIDER"] = "mock"

from app.chatbot import Chatbot
from app.conversation_risk import combine
from app.risk_rules import CRISIS, AMBIGUOUS, NORMAL, screen
from app.templates import checkin_reply, crisis_reply, fallback_reply
from app.validator import validate


def test_explicit_crisis():
    assert screen("I want to kill myself").level == CRISIS


def test_idiom_is_not_crisis():
    assert screen("This exam is killing me!").level < CRISIS
    assert screen("I'm going to die laughing").level < CRISIS


def test_negated_crisis_becomes_ambiguous():
    assert screen("I don't want to die, I just want this to end").level == AMBIGUOUS


def test_hinglish_crisis():
    assert screen("mujhe suicide karna hai").level == CRISIS


def test_normal_message():
    assert screen("How do I plan my revision?").level == NORMAL


def test_repeated_ambiguous_escalates():
    level, why = combine(AMBIGUOUS, [1, AMBIGUOUS], "nobody would notice", False)
    assert level == CRISIS and "repeated_ambiguous_signals" in why


def test_affirmation_after_checkin_escalates():
    level, _ = combine(AMBIGUOUS, [AMBIGUOUS], "yes, kind of", True)
    assert level == CRISIS


def test_templates_pass_validator():
    for text in (crisis_reply(), checkin_reply(), checkin_reply(True), fallback_reply()):
        ok, why = validate(text)
        assert ok, why


def test_validator_blocks_unsafe_replies():
    for bad in [
        "You probably have depression.",
        "Try taking sertraline for it.",
        "I have contacted your counsellor.",
        "I promise I won't tell anyone.",
        "Just relax, it's not a big deal.",
    ]:
        assert not validate(bad)[0]


def test_crisis_calls_escalation_and_locks_safety_mode():
    bot = Chatbot("test_lock", use_llm_classifier=False)
    out = bot.send("I want to end my life")
    assert out["route"] == "crisis" and out["escalated"] is True
    assert out["escalation_ticket"]["simulated"] is True
    out2 = bot.send("just kidding, can you help me study?")
    assert out2["route"] == "safety_followup"   # still locked after a retraction


def test_normal_chat_does_not_escalate():
    bot = Chatbot("test_normal", use_llm_classifier=False)
    out = bot.send("I'm nervous about my exam tomorrow")
    assert out["route"] == "support" and out["escalated"] is False

