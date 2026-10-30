import pytest
from tools.resource_lookup import load_resources, unverified, contacts_block
from tools.notify_counselor_sim import notify_counselor_sim
from config.templates import crisis_reply, CRISIS_SELF, CRISIS_THIRD, DISCLAIMER, REFERRAL, FALLBACK
from tools.coping_tools import TECHNIQUES, choose_technique


def test_load_resources():
    resources = load_resources()
    assert isinstance(resources, list)
    assert len(resources) >= 4
    for r in resources:
        for k in ("id", "name", "number", "kind", "verified"):
            assert k in r


def test_unverified_returns_campus_entry():
    resources = load_resources()
    unver = unverified(resources)
    assert "Campus Counseling Cell" in unver


def test_crisis_replies_include_all_numbers():
    resources = load_resources()
    self_reply = crisis_reply(third_person=False, resources=resources)
    third_reply = crisis_reply(third_person=True, resources=resources)

    for r in resources:
        assert r["number"] in self_reply
        assert r["number"] in third_reply

    assert "SIMULATED" in self_reply
    assert "SIMULATED" in third_reply


def test_simulated_counselor_notification():
    notice = notify_counselor_sim(level=3, signals=["suicide_word"], turn_index=2)
    assert notice["simulated"] is True
    assert "SIMULATED" in notice["label"]
    assert "simulated" in notice["recipient"].lower()
    assert "No real person was contacted" in notice["label"]
    assert notice["risk_level"] == 3
    assert "suicide_word" in notice["signals"]
    assert notice["turn"] == 2


def test_coping_tools_available():
    assert "5-4-3-2-1" in TECHNIQUES["grounding_54321"]
    assert "breathing" in TECHNIQUES["box_breathing"].lower()
    assert choose_technique(["sleep"], "can't sleep") == TECHNIQUES["basic_sleep_routine"]
    assert choose_technique([], "exam stress") == TECHNIQUES["study_break_plan"]
