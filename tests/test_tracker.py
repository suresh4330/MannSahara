import pytest
from agents.tracker import RiskTracker


def test_tracker_reset_clears_state():
    tracker = RiskTracker()
    tracker.update(3)
    assert tracker.latched is True
    assert len(tracker.history) == 1

    tracker.reset()
    assert tracker.latched is False
    assert len(tracker.history) == 0
    assert tracker.update(0) == 0


def test_tracker_latch_stays_three():
    tracker = RiskTracker()
    assert tracker.update(1) == 1
    assert tracker.update(3) == 3
    # Any subsequent score must stay latched at 3
    assert tracker.update(0) == 3
    assert tracker.update(1) == 3
    assert tracker.update(2) == 3


def test_tracker_t1_persistence():
    # M=3, W=4, level >= 1
    tracker = RiskTracker(mild_in_window=3, window=4)
    assert tracker.update(1) == 1
    assert tracker.update(0) == 0
    assert tracker.update(1) == 1
    # Now 3 turns out of last 4 have score >= 1
    assert tracker.update(1) == 2


def test_tracker_t2_repetition_to_crisis():
    # N=3 turns of level 2 -> latch 3
    tracker = RiskTracker(level2_to_crisis=3)
    assert tracker.update(2) == 2
    assert tracker.update(2) == 2
    assert tracker.update(2) == 3
    assert tracker.latched is True
    # Subsequent turn stays 3
    assert tracker.update(0) == 3

