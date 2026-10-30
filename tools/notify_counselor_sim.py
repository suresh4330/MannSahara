from datetime import datetime, timezone


def notify_counselor_sim(level, signals, turn_index):
    return {
        "simulated": True,
        "label": "[SIMULATED DEMO NOTIFICATION] No real person was contacted.",
        "recipient": "campus counselor (simulated)",
        "risk_level": level,
        "signals": list(signals),
        "turn": turn_index,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": "Handoff summary holds signals only, never the full transcript.",
    }

