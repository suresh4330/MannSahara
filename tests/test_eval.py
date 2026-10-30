import pytest
from evaluation.metrics import wilson, compute_metrics


def test_wilson_interval_bounds():
    low, high = wilson(10, 10)
    assert low > 0.6
    assert high <= 1.0

    low0, high0 = wilson(0, 10)
    assert low0 >= 0.0
    assert high0 < 0.4

    empty_low, empty_high = wilson(0, 0)
    assert empty_low == 0.0
    assert empty_high == 0.0


def test_compute_metrics_sanity():
    mock_rows = [
        # Crisis dialogue passing
        {
            "category": "active_crisis", "expected_peak_level": 3, "actual_peak_level": 3,
            "latency_turns": 0, "first_turn_at_level3": 1, "safety_pass": True, "strict_pass": True,
            "final_response": "14416", "llm_errors": 0
        },
        # Benign dialogue
        {
            "category": "benign", "expected_peak_level": 0, "actual_peak_level": 0,
            "latency_turns": None, "first_turn_at_level3": None, "safety_pass": True, "strict_pass": True,
            "final_response": "chat", "llm_errors": 0
        },
        # Trap dialogue
        {
            "category": "false_positive_trap", "expected_peak_level": 0, "actual_peak_level": 0,
            "latency_turns": None, "first_turn_at_level3": None, "safety_pass": True, "strict_pass": True,
            "final_response": "chat", "llm_errors": 0
        },
    ]
    m = compute_metrics(mock_rows)
    assert m["total_dialogues"] == 3
    assert m["crisis_dialogues"] == 1
    assert m["crisis_safety_recall"] == 1.0
    assert m["false_crisis_rate"] == 0.0
    assert m["trap_false_crisis_rate"] == 0.0
    assert m["final_reply_violations"] == 0

