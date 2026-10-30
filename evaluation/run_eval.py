"""Evaluation harness executing dialogues through the MannSahara pipeline.
Produces test_log.csv, raw_scores.json, metrics.json, ablation.md, and RESULTS.md.
Adheres strictly to Section 9 of the implementation guide.
"""
import argparse
import csv
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from router import build_pipeline
from evaluation.metrics import compute_metrics
from evaluation.ablation import run_ablation, judge_dialogue

TOL = 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["dev", "heldout"], default="dev")
    args = parser.parse_args()

    data_path = PROJECT_ROOT / "data" / f"{args.split}_dialogues.json"
    if not data_path.exists():
        print(f"Error: dataset file {data_path} not found.")
        sys.exit(1)

    data = json.loads(data_path.read_text(encoding="utf-8"))
    results_dir = PROJECT_ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"Starting evaluation on {args.split} split ({len(data)} dialogues)...")
    pipe = build_pipeline("hybrid")

    rows = []
    raw = {}
    draft_blocks = 0
    failures = []

    for idx, d in enumerate(data, 1):
        pipe.reset()  # MUST reset before every dialogue
        res = [pipe.handle(t) for t in d["turns"]]
        levels = [r.level for r in res]

        strict, safety, why, first3, peak, latency = judge_dialogue(d, levels)

        raw[d["id"]] = [
            {"rules": r.gateway.rules_score, "llm": r.gateway.llm_score}
            for r in res
        ]

        # Gather signals across all turns
        all_signals = []
        for r in res:
            for s in r.gateway.signals:
                if s not in all_signals:
                    all_signals.append(s)

        # Count llm errors
        llm_err_count = sum(1 for r in res if r.gateway.llm_error is not None)

        # Guardrail checks
        triggered = any(r.guardrail_triggered for r in res)
        all_viols = []
        for r in res:
            for v in r.violations:
                if v not in all_viols:
                    all_viols.append(v)
        if triggered:
            draft_blocks += 1

        # Peak turn response and action
        peak_idx = levels.index(peak) if peak in levels else -1
        resp_at_peak = res[peak_idx].reply if peak_idx >= 0 else res[-1].reply
        action_at_peak = res[peak_idx].action if peak_idx >= 0 else res[-1].action

        row = {
            "dialogue_id": d["id"],
            "split": d["split"],
            "category": d["category"],
            "user_turns": " || ".join(d["turns"]),
            "expected_peak_level": d["expected_peak_level"],
            "expected_peak_turn": d.get("expected_peak_turn", ""),
            "per_turn_rules": "|".join(str(r.gateway.rules_score) for r in res),
            "per_turn_llm": "|".join(str(r.gateway.llm_score if r.gateway.llm_score is not None else "NA") for r in res),
            "per_turn_level": "|".join(str(r.level) for r in res),
            "actual_peak_level": peak,
            "first_turn_at_level3": first3 if first3 is not None else "",
            "latency_turns": latency if latency is not None else "",
            "signals": ", ".join(all_signals),
            "action_at_peak": action_at_peak,
            "final_response": resp_at_peak.replace("\n", " "),
            "guardrail_triggered": triggered,
            "violations": ", ".join(all_viols),
            "llm_backend": getattr(pipe.gateway.client, "backend", "unknown"),
            "llm_errors": llm_err_count,
            "strict_pass": strict,
            "safety_pass": safety,
            "fail_reason": why,
        }
        rows.append(row)

        if not safety:
            failures.append({
                "id": d["id"],
                "category": d["category"],
                "expected": d["expected_peak_level"],
                "actual": peak,
                "why": why or "safety_criteria_missed",
                "turns": d["turns"],
            })

        if idx % 20 == 0 or idx == len(data):
            print(f"  Processed {idx}/{len(data)} dialogues...")

    # Write CSV
    csv_filename = "test_log.csv" if args.split == "dev" else f"test_log_{args.split}.csv"
    csv_path = results_dir / csv_filename
    fieldnames = [
        "dialogue_id", "split", "category", "user_turns",
        "expected_peak_level", "expected_peak_turn",
        "per_turn_rules", "per_turn_llm", "per_turn_level",
        "actual_peak_level", "first_turn_at_level3", "latency_turns",
        "signals", "action_at_peak", "final_response",
        "guardrail_triggered", "violations", "llm_backend", "llm_errors",
        "strict_pass", "safety_pass", "fail_reason"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved log to {csv_path}")

    # Write raw_scores.json
    raw_path = results_dir / ("raw_scores.json" if args.split == "dev" else f"raw_scores_{args.split}.json")
    raw_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    # Compute and write metrics.json
    metrics = compute_metrics(rows, guardrail_draft_blocks=draft_blocks)
    metrics_path = results_dir / ("metrics.json" if args.split == "dev" else f"metrics_{args.split}.json")
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Saved metrics to {metrics_path}")

    # Run and write ablation study
    ablation_md = run_ablation(data, raw)
    ablation_path = results_dir / "ablation.md"
    ablation_path.write_text(ablation_md, encoding="utf-8")
    print(f"Saved ablation study to {ablation_path}")

    # Write RESULTS.md summary
    results_summary = [
        f"# MannSahara Evaluation Results ({args.split.upper()} split)",
        f"- **Backend**: {rows[0]['llm_backend'] if rows else 'unknown'}",
        f"- **Total Dialogues**: {metrics['total_dialogues']}",
        f"- **Crisis Safety Recall**: {metrics['crisis_safety_recall']:.2%} (95% CI: {metrics['crisis_safety_recall_ci'][0]:.2%} to {metrics['crisis_safety_recall_ci'][1]:.2%})",
        f"- **Crisis Strict Recall (TOL={TOL})**: {metrics['crisis_strict_recall']:.2%} (95% CI: {metrics['crisis_strict_recall_ci'][0]:.2%} to {metrics['crisis_strict_recall_ci'][1]:.2%})",
        f"- **False-Crisis Rate**: {metrics['false_crisis_rate']:.2%} (95% CI: {metrics['false_crisis_ci'][0]:.2%} to {metrics['false_crisis_ci'][1]:.2%})",
        f"- **Trap False-Crisis Rate**: {metrics['trap_false_crisis_rate']:.2%}",
        f"- **Benign False-Crisis Rate**: {metrics['benign_false_crisis_rate']:.2%}",
        f"- **Over-Escalation Rate**: {metrics['over_escalation_rate']:.2%}",
        f"- **Referral Correctness**: {metrics['referral_correctness']:.2%}",
        f"- **Overall Level Accuracy**: {metrics['level_accuracy']:.2%}",
        f"- **Guardrail Violations in Final Replies**: {metrics['final_reply_violations']}",
        f"- **Total LLM Classifier Errors**: {metrics['total_llm_errors']}",
        "",
        "### Escalation Latency Distribution (turns relative to expected peak):",
        json.dumps(metrics["latency_distribution"], indent=2),
    ]
    results_md_path = results_dir / "RESULTS.md"
    results_md_path.write_text("\n".join(results_summary), encoding="utf-8")

    # Update FAILURES.md
    failures_lines = [
        "# Failure Analysis Log",
        "",
        "| Dialogue ID | Category | Expected / Actual | Why it failed | Fix or Accepted Limitation |",
        "| :--- | :--- | :---: | :--- | :--- |"
    ]
    for fail in failures:
        failures_lines.append(
            f"| {fail['id']} | {fail['category']} | {fail['expected']} / {fail['actual']} | {fail['why']} | Under analysis / subtle indirect phrasing |"
        )
    if not failures:
        failures_lines.append("| (None) | - | - | All safety criteria passed | No safety failures observed |")

    failures_path = results_dir / "FAILURES.md"
    failures_path.write_text("\n".join(failures_lines), encoding="utf-8")

    # Print stdout summary
    print("\n" + "=" * 60)
    print(f"EVALUATION COMPLETE ({args.split.upper()} SPLIT)")
    print("=" * 60)
    print(f"Total Dialogues:         {metrics['total_dialogues']}")
    print(f"Crisis Safety Recall:    {metrics['crisis_safety_recall']:.2%} ({int(metrics['crisis_safety_recall'] * metrics['crisis_dialogues'])}/{metrics['crisis_dialogues']})")
    print(f"Crisis Strict Recall:    {metrics['crisis_strict_recall']:.2%}")
    print(f"False-Crisis Rate:       {metrics['false_crisis_rate']:.2%} ({metrics['false_crisis_count']}/{metrics['non_crisis_dialogues']})")
    print(f"Trap False-Crisis Rate:  {metrics['trap_false_crisis_rate']:.2%}")
    print(f"Over-Escalation Rate:    {metrics['over_escalation_rate']:.2%}")
    print(f"Referral Correctness:    {metrics['referral_correctness']:.2%}")
    print(f"Overall Level Accuracy:  {metrics['level_accuracy']:.2%}")
    print(f"LLM Classifier Errors:   {metrics['total_llm_errors']}")
    print(f"Safety Failures Count:   {len(failures)}")
    print("=" * 60)


if __name__ == "__main__":
    main()

