"""Evaluate rules-only performance on dev_dialogues.json.
Reports crisis recall, false-crisis rate, and specific misses honestly.
"""
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.rules import score_rules

def main():
    dev_path = pathlib.Path(__file__).resolve().parent.parent / "data" / "dev_dialogues.json"
    data = json.loads(dev_path.read_text(encoding="utf-8"))

    crisis_total = 0
    crisis_detected = 0
    non_crisis_total = 0
    false_crisis_count = 0
    misses = []
    false_crises = []

    for d in data:
        exp = d["expected_peak_level"]
        # Find peak score across turns using rules only
        rule_scores = [score_rules(t)[0] for t in d["turns"]]
        peak = max(rule_scores)

        if exp == 3:
            crisis_total += 1
            if peak >= 3:
                crisis_detected += 1
            else:
                misses.append((d["id"], d["category"], d["turns"], rule_scores))
        elif exp in (0, 1):
            non_crisis_total += 1
            if peak >= 3:
                false_crisis_count += 1
                false_crises.append((d["id"], d["category"], d["turns"], rule_scores))

    recall = crisis_detected / crisis_total if crisis_total else 0
    fcr = false_crisis_count / non_crisis_total if non_crisis_total else 0

    print("=== Rules-Only Dev Evaluation Summary ===")
    print(f"Total dialogues: {len(data)}")
    print(f"Expected Crisis (Level 3): {crisis_total}")
    print(f"Crisis Detected by Rules: {crisis_detected}")
    print(f"Crisis Recall: {recall:.2%} ({crisis_detected}/{crisis_total})")
    print(f"Non-Crisis (Level 0 or 1): {non_crisis_total}")
    print(f"False Crisis Count: {false_crisis_count}")
    print(f"False Crisis Rate: {fcr:.2%} ({false_crisis_count}/{non_crisis_total})")

    if misses:
        print(f"\nMissed Crisis Cases ({len(misses)}):")
        for mid, mcat, turns, scores in misses:
            print(f"- {mid} [{mcat}]: turns={turns} -> rules_scores={scores}")

    if false_crises:
        print(f"\nFalse Crisis Cases ({len(false_crises)}):")
        for fid, fcat, turns, scores in false_crises:
            print(f"- {fid} [{fcat}]: turns={turns} -> rules_scores={scores}")

if __name__ == "__main__":
    main()
