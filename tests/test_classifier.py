import pytest
from agents.classifier import classify
from agents.schemas import LLMRisk


class FakeClient:
    def __init__(self, responses=None, exception=None):
        self.responses = list(responses) if responses else []
        self.exception = exception
        self.call_count = 0

    def complete(self, system, user, max_tokens=300):
        self.call_count += 1
        if self.exception:
            raise self.exception
        if self.responses:
            return self.responses.pop(0)
        return '{"risk_level": 0, "signals": [], "confidence": 0.5, "third_person": false}'


def test_classify_valid_json():
    client = FakeClient(['{"risk_level": 3, "signals": ["suicidal_intent"], "confidence": 0.95, "third_person": false}'])
    res = classify(client, "I want to die", [])
    assert isinstance(res, LLMRisk)
    assert res.risk_level == 3
    assert "suicidal_intent" in res.signals
    assert res.confidence == 0.95
    assert res.third_person is False
    assert client.call_count == 1


def test_classify_json_inside_code_fences():
    fenced = '```json\n{"risk_level": 1, "signals": ["insomnia"], "confidence": 0.8, "third_person": false}\n```'
    client = FakeClient([fenced])
    res = classify(client, "Can't sleep", [])
    assert res.risk_level == 1
    assert "insomnia" in res.signals


def test_classify_invalid_then_valid_retry():
    client = FakeClient([
        "Not a json response sorry",
        '{"risk_level": 2, "signals": ["hopeless"], "confidence": 0.75, "third_person": false}'
    ])
    res = classify(client, "I feel hopeless", [], retries=1)
    assert res.risk_level == 2
    assert client.call_count == 2


def test_classify_always_invalid_raises():
    client = FakeClient(["garbage 1", "garbage 2"])
    with pytest.raises(Exception):
        classify(client, "Hello", [], retries=1)
    assert client.call_count == 2


def test_classify_exception_raised():
    client = FakeClient(exception=ConnectionError("Server unreachable"))
    with pytest.raises(ConnectionError):
        classify(client, "Hello", [], retries=1)

