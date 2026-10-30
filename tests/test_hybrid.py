import random
import pytest
from agents.safety_gateway import combine_scores, SafetyGateway
from agents.schemas import GatewayResult


class FailingClient:
    backend = "mock_failing"

    def complete(self, system, user, max_tokens=300):
        raise TimeoutError("Simulated LLM network timeout")


class StaticClient:
    def __init__(self, level=0):
        self.backend = "mock_static"
        self.level = level

    def complete(self, system, user, max_tokens=300):
        return f'{{"risk_level": {self.level}, "signals": ["test_signal"], "confidence": 0.9, "third_person": false}}'


def test_hybrid_property_test_random_pairs():
    # Unit test: for every turn, hybrid == max(rules, llm) and hybrid >= each
    random.seed(42)
    for _ in range(200):
        r = random.randint(0, 3)
        l = random.randint(0, 3)
        h = combine_scores("hybrid", r, l)
        assert h == max(r, l)
        assert h >= r
        assert h >= l


def test_combine_scores_modes():
    assert combine_scores("rules", 2, 0) == 2
    assert combine_scores("rules", 1, 3) == 1
    assert combine_scores("llm", 1, 3) == 3
    assert combine_scores("llm", 2, None) == 2  # D6 fallback to rules
    assert combine_scores("hybrid", 1, 2) == 2
    assert combine_scores("hybrid", 3, 0) == 3


def test_gateway_llm_failure_fallback():
    # LLM failure sets llm_error (exception class name only) and falls back to rules score
    gateway = SafetyGateway(client=FailingClient(), mode="hybrid")
    # Message triggering Level 3 in rules
    res = gateway.assess("I want to end my life right now.")
    assert isinstance(res, GatewayResult)
    assert res.rules_score == 3
    assert res.llm_score is None
    assert res.llm_error == "TimeoutError"
    # Never leaks text or secrets in llm_error
    assert "Simulated" not in res.llm_error
    assert res.hybrid_score == 3
    assert res.tracked_level == 3

