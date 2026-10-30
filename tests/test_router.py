import pytest
from router import Pipeline
from agents.safety_gateway import SafetyGateway
from agents.tracker import RiskTracker
from agents.guardrail import Guardrail
from config.templates import FALLBACK
from tools.resource_lookup import load_resources


class SpyCopingAgent:
    def __init__(self, unsafe=False):
        self.call_count = 0
        self.unsafe = unsafe

    def reply(self, text, level, history):
        self.call_count += 1
        if self.unsafe:
            # Returns an unsafe diagnosis draft to test guardrail fallback
            return "Based on my assessment you have depression and need medication."
        return f"Supportive reply to: {text}"


class SpyCopingAgentRaiseOnCall:
    def __init__(self):
        self.called = False

    def reply(self, text, level, history):
        self.called = True
        raise AssertionError("Coping Agent MUST NEVER be called at Level 3!")


class MockGateway:
    def __init__(self, level=0, third_person=False):
        self.level = level
        self.third_person = third_person
        self.context = []

    def reset(self):
        self.context = []

    def assess(self, text):
        from agents.schemas import GatewayResult
        return GatewayResult(
            rules_score=self.level,
            llm_score=self.level,
            hybrid_score=self.level,
            tracked_level=self.level,
            signals=["mock_crisis"] if self.level == 3 else [],
            third_person=self.third_person,
            injection_attempt=False,
            llm_error=None,
            llm_backend="mock"
        )


def test_level3_never_calls_coping_agent():
    # R5 Acceptance: spy Coping Agent raises if called; Level 3 inputs must pass
    resources = load_resources()
    spy_coping = SpyCopingAgentRaiseOnCall()
    gateway = MockGateway(level=3, third_person=False)
    pipeline = Pipeline(gateway, spy_coping, Guardrail(), resources)

    level3_inputs = [
        "I want to end my life.",
        "I'm going to kill myself tonight.",
        "Wish I wouldn't wake up tomorrow.",
        "Everyone would be better off without me."
    ]

    for msg in level3_inputs:
        res = pipeline.handle(msg)
        assert res.level == 3
        assert res.action == "crisis_response"
        assert res.reply_from_llm is False
        assert spy_coping.called is False
        assert "SIMULATED" in res.reply
        for r in resources:
            assert r["number"] in res.reply


def test_level0_calls_coping_agent():
    resources = load_resources()
    spy_coping = SpyCopingAgent()
    gateway = MockGateway(level=0)
    pipeline = Pipeline(gateway, spy_coping, Guardrail(), resources)

    res = pipeline.handle("How do I prepare for exams?")
    assert res.level == 0
    assert res.action == "supportive_chat"
    assert spy_coping.call_count == 1
    assert "Supportive reply" in res.reply
    assert res.reply_from_llm is True


def test_unsafe_draft_replaced_by_fallback():
    # R7 Acceptance: unsafe draft replaced by safe template
    resources = load_resources()
    spy_coping = SpyCopingAgent(unsafe=True)
    gateway = MockGateway(level=1)
    pipeline = Pipeline(gateway, spy_coping, Guardrail(), resources)

    res = pipeline.handle("I am feeling really low and stressed.")
    assert res.guardrail_triggered is True
    assert "diagnosis" in res.violations
    assert res.reply_from_llm is False
    assert FALLBACK[1] in res.reply


def test_reset_clears_pipeline_state():
    # R4 Acceptance: reset per conversation
    resources = load_resources()
    spy_coping = SpyCopingAgent()
    gateway = MockGateway(level=0)
    pipeline = Pipeline(gateway, spy_coping, Guardrail(), resources)

    pipeline.handle("Hello turn 1")
    pipeline.handle("Hello turn 2")
    assert pipeline.turn == 2
    assert len(pipeline.history) == 4

    pipeline.reset()
    assert pipeline.turn == 0
    assert len(pipeline.history) == 0
