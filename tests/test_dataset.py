import json
import pathlib
import pytest

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
REQUIRED_FIELDS = {
    "id", "split", "category", "synthetic", "language",
    "turns", "expected_peak_level"
}
EXPECTED_CATEGORIES = {
    "benign", "mild", "moderate", "passive_ideation", "active_crisis",
    "coded", "third_person", "hinglish", "false_positive_trap",
    "adversarial", "multi_turn"
}
DEV_MIN_COUNTS = {
    "benign": 20, "mild": 15, "moderate": 15, "passive_ideation": 12,
    "active_crisis": 15, "coded": 12, "third_person": 10, "hinglish": 15,
    "false_positive_trap": 15, "adversarial": 12, "multi_turn": 15
}
HELDOUT_MIN_COUNTS = {
    "benign": 4, "mild": 4, "moderate": 4, "passive_ideation": 4,
    "active_crisis": 4, "coded": 4, "third_person": 4, "hinglish": 4,
    "false_positive_trap": 4, "adversarial": 4, "multi_turn": 4
}


def load_dataset(filename):
    p = DATA_DIR / filename
    assert p.exists(), f"{filename} does not exist"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def test_dataset_schema_and_types():
    dev = load_dataset("dev_dialogues.json")
    heldout = load_dataset("heldout_dialogues.json")
    all_ids = set()

    for split_name, ds in [("dev", dev), ("heldout", heldout)]:
        for record in ds:
            # Check required fields
            for f in REQUIRED_FIELDS:
                assert f in record, f"Missing {f} in record {record.get('id')}"

            assert record["split"] == split_name
            assert record["synthetic"] is True
            assert record["category"] in EXPECTED_CATEGORIES
            assert record["language"] in {"en", "hinglish", "mixed"}
            assert isinstance(record["turns"], list) and len(record["turns"]) >= 1
            assert record["expected_peak_level"] in {0, 1, 2, 3}

            rid = record["id"]
            assert rid not in all_ids, f"Duplicate id {rid}"
            all_ids.add(rid)

            if record["expected_peak_level"] == 3:
                assert "expected_peak_turn" in record, f"Missing expected_peak_turn in {rid}"
                turn = record["expected_peak_turn"]
                assert 1 <= turn <= len(record["turns"]), (
                    f"Invalid expected_peak_turn {turn} for {rid} with {len(record['turns'])} turns"
                )

            if record["category"] == "multi_turn":
                assert 3 <= len(record["turns"]) <= 6, f"Multi-turn {rid} must have 3-6 turns"
            elif record["category"] != "multi_turn":
                # Single-turn categories have 1 turn according to authoring rules
                assert len(record["turns"]) == 1, f"Single-turn category {rid} must have 1 turn"


def test_dataset_counts():
    dev = load_dataset("dev_dialogues.json")
    heldout = load_dataset("heldout_dialogues.json")

    assert len(dev) >= 156, f"Dev count {len(dev)} < 156"
    assert len(heldout) >= 44, f"Heldout count {len(heldout)} < 44"

    # Category counts
    for cat, min_count in DEV_MIN_COUNTS.items():
        actual = sum(1 for d in dev if d["category"] == cat)
        assert actual >= min_count, f"Dev category {cat} count {actual} < {min_count}"

    for cat, min_count in HELDOUT_MIN_COUNTS.items():
        actual = sum(1 for d in heldout if d["category"] == cat)
        assert actual >= min_count, f"Heldout category {cat} count {actual} < {min_count}"

    # Crisis dialogues count (peak level 3)
    dev_crisis = sum(1 for d in dev if d["expected_peak_level"] == 3)
    heldout_crisis = sum(1 for d in heldout if d["expected_peak_level"] == 3)
    assert dev_crisis >= 50, f"Dev crisis count {dev_crisis} < 50"
    assert heldout_crisis >= 15, f"Heldout crisis count {heldout_crisis} < 15"

    # Hinglish crisis count (at least 6 in dev)
    dev_hinglish_crisis = sum(1 for d in dev if d["category"] == "hinglish" and d["expected_peak_level"] == 3)
    assert dev_hinglish_crisis >= 6, f"Dev hinglish crisis count {dev_hinglish_crisis} < 6"


def test_no_leakage_between_dev_and_heldout():
    dev = load_dataset("dev_dialogues.json")
    heldout = load_dataset("heldout_dialogues.json")

    def normalize(text):
        return " ".join(text.lower().split())

    dev_texts = set()
    for d in dev:
        for t in d["turns"]:
            dev_texts.add(normalize(t))

    for h in heldout:
        for t in h["turns"]:
            norm = normalize(t)
            assert norm not in dev_texts, f"Overlap between dev and heldout: '{t}' in {h['id']}"
