"""Runs every synthetic test case through the chatbot and writes the TEST LOG + metrics.
Usage:
  python evaluate.py --split all --mode rules      # rules only (works offline)
  python evaluate.py --split test --mode hybrid    # rules + LLM classifier (needs an API/LLM)
Tune the system on --split dev only. Run --split test once, at the end, and report that.
"""
import argparse
import json
import os

import pandas as pd
from app import config
from app.chatbot import Chatbot
from app.db import Store
from app.validator import validate

ACTIONS = ["support", "checkin", "escalate"]
ROUTE_TO_ACTION = {
    "support": "support",
    "safety_followup": "support",
    "checkin": "checkin",
    "crisis": "escalate",
}


def run_case(case, store, use_llm):
    bot = Chatbot(conversation_id=case["id"], store=store, use_llm_classifier=use_llm)
    routes, esc_turns, retries, fallbacks, bad_replies = [], [], 0, 0, 0
    last_reply = ""
    for i, msg in enumerate(case["turns"], 1):
        out = bot.send(msg)
        routes.append(out["route"])
        if out["escalated"]:
            esc_turns.append(i)
        retries += out.get("retries", 0)
        fallbacks += int(out.get("used_fallback", False))
        ok, _ = validate(out["reply"])
        bad_replies += int(not ok)
        last_reply = out["reply"]

    actual = max((ROUTE_TO_ACTION[r] for r in routes), key=ACTIONS.index)
    first_esc = esc_turns[0] if esc_turns else None
    passed = actual == case["expected_action"]
    exp_turn = case.get("expected_escalation_turn")
    if passed and case["expected_action"] == "escalate" and exp_turn:
        passed = first_esc is not None and first_esc <= exp_turn
    if passed and case.get("expect_locked"):
        after = routes[first_esc:]  # every route after the first escalation turn index
        passed = all(r in ("safety_followup", "crisis") for r in after)

    return {
        "id": case["id"], "split": case["split"], "category": case["category"],
        "input": " || ".join(case["turns"]),
        "actual_action": actual, "expected_action": case["expected_action"],
        "expected_escalation_turn": exp_turn,
        "actual_escalation_turn": first_esc,
        "route_per_turn": " > ".join(routes),
        "escalation_tool_called": bool(esc_turns),
        "fallback_used": fallbacks, "unsafe_final_replies": bad_replies,
        "retries": retries,
        "pass": passed, "notes": case.get("notes", ""),
        "final_reply_preview": last_reply[:140].replace("\n", " "),
    }


def metrics(df):
    pos = df["expected_action"] == "escalate"
    pred = df["actual_action"] == "escalate"
    tp = int((pos & pred).sum())
    fn = int((pos & ~pred).sum())
    fp = int((~pos & pred).sum())
    tn = int((~pos & ~pred).sum())

    def div(a, b):
        return round(a / b, 3) if b else 0.0

    prec = div(tp, tp + fp)
    rec = div(tp, tp + fn)
    f1 = round(2 * prec * rec / (prec + rec), 3) if (prec + rec) else 0.0

    timely = df[pos & pred & df["expected_escalation_turn"].notna()]
    delay = (timely["actual_escalation_turn"] - timely["expected_escalation_turn"])
    avg_late = float(delay.mean()) if len(delay) else 0.0

    confusion = pd.crosstab(
        df["expected_action"], df["actual_action"],
        rownames=["expected"], colnames=["actual"],
    ).reindex(index=ACTIONS, columns=ACTIONS, fill_value=0)

    per_cat = df.groupby("category")["pass"].agg(["sum", "count"])
    per_cat["pass_rate"] = (per_cat["sum"] / per_cat["count"]).round(3)

    return {
        "total_cases": len(df),
        "passed": int(df["pass"].sum()),
        "overall_pass_rate": div(int(df["pass"].sum()), len(df)),
        "crisis_cases": int(pos.sum()),
        "crisis_recall": rec,
        "crisis_precision": prec,
        "crisis_f1": f1,
        "TP": tp, "FN": fn, "FP": fp, "TN": tn,
        "false_positive_rate": div(fp, fp + tn),
        "escalation_tool_called_on_all_detected": bool(
            df.loc[pred, "escalation_tool_called"].all() if pred.any() else True
        ),
        "avg_turns_late": avg_late,
        "unsafe_final_replies": int(df["unsafe_final_replies"].sum()),
        "validator_retries": int(df["retries"].sum()),
        "fallbacks_used": int(df["fallback_used"].sum()),
        "confusion_matrix_rows_expected_cols_actual": confusion.to_dict(),
        "per_category": per_cat.rename(columns={"sum": "passed", "count": "n"}).to_dict("index"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["dev", "test", "all"], default="all")
    ap.add_argument("--mode", choices=["rules", "hybrid"], default="rules")
    args = ap.parse_args()

    with open(config.DATA_DIR / "test_cases.json", encoding="utf-8") as f:
        cases = json.load(f)

    if args.split != "all":
        cases = [c for c in cases if c["split"] == args.split]

    db_path = str(config.LOG_DIR / "eval.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    store = Store(db_path)

    use_llm = args.mode == "hybrid"
    rows = [run_case(c, store, use_llm) for c in cases]
    df = pd.DataFrame(rows)
    m = metrics(df)
    m.update({
        "mode": args.mode,
        "split": args.split,
        "llm_provider": config.LLM_PROVIDER,
        "llm_model": config.LLM_MODEL or "(provider default)",
    })

    tag = f"{args.mode}_{args.split}"
    df.to_csv(config.LOG_DIR / f"test_log_{tag}.csv", index=False, encoding="utf-8")

    with open(config.LOG_DIR / f"metrics_{tag}.json", "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)

    fails = df[~df["pass"]][["id", "category", "input", "expected_action", "actual_action"]]

    with open(config.LOG_DIR / f"test_report_{tag}.md", "w", encoding="utf-8") as f:
        f.write(f"# Test report ({tag})\n")
        f.write(f"- Cases: {m['total_cases']}  Passed: {m['passed']}\n")
        f.write(
            f"- Crisis recall: {m['crisis_recall']} "
            f"(TP={m['TP']}, FN={m['FN']})\n"
        )
        f.write(
            f"- False-positive rate: {m['false_positive_rate']} "
            f"(FP={m['FP']}, TN={m['TN']})\n"
        )
        f.write(f"- Crisis precision: {m['crisis_precision']}  F1: {m['crisis_f1']}\n\n")
        f.write("## Failures (analyse every one in your report)\n")
        if len(fails):
            f.write(fails.to_markdown(index=False))
        else:
            f.write("No failures.\n")

    print(
        f"Mode={args.mode} split={args.split} "
        f"cases={m['total_cases']} passed={m['passed']}"
    )
    print(
        f"Crisis recall={m['crisis_recall']} (TP={m['TP']} FN={m['FN']}) "
        f"FPR={m['false_positive_rate']} (FP={m['FP']} TN={m['TN']})"
    )
    print(
        f"Unsafe final replies={m['unsafe_final_replies']}  "
        f"Log: logs/test_log_{tag}.csv"
    )
    if len(fails):
        print("\nFAILED CASES:")
        print(fails.to_string(index=False))


if __name__ == "__main__":
    main()

