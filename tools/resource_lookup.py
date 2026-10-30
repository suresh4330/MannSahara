import json
import pathlib

CONFIG = pathlib.Path(__file__).resolve().parent.parent / "config" / "resources.json"


def load_resources(path=CONFIG):
    res = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))["resources"]
    for r in res:
        for k in ("id", "name", "number", "kind", "verified"):
            if k not in r:
                raise ValueError(f"resource missing {k}: {r}")
    return res


def unverified(resources):
    return [r["name"] for r in resources if not r["verified"] or "REPLACE_ME" in r["number"]]


def contacts_block(resources):
    return "\n".join(f"- {r['name']}: {r['number']}" for r in resources)
