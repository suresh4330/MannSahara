"""Loads data/resources.json. The bot never invents phone numbers: only this file is used."""
import json
from . import config


def load():
    with open(config.DATA_DIR / "resources.json", encoding="utf-8") as f:
        return json.load(f)


def format_resources():
    r = load()
    lines = [f"- {r['emergency']['name']}: {r['emergency']['number']}"]
    for h in r["helplines"]:
        lines.append(f"- {h['name']}: {h['number']} ({h['website']})")
    for c in r["campus"]:
        lines.append(f"- {c['name']}: {c['contact']}")
    return "\n".join(lines)

