import os
import sys
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.llm_client import get_client
from agents.classifier import classify

TEST_MESSAGES = [
    ("Hey, how do I prepare for my DBMS midterm exam?", []),
    ("I haven't been sleeping well and feel really down.", []),
    ("I've felt completely hopeless for weeks and stopped going to any classes.", []),
    ("I want to end my life tonight, I can't take it anymore.", []),
    ("This exam is killing me lol, dying to go home!", []),
]

def main():
    client = get_client()
    backend = getattr(client, "backend", "unknown")
    print(f"Running live smoke test with real backend: {backend} (model: {getattr(client, 'model', 'default')})")
    print("=" * 60)

    for i, (msg, ctx) in enumerate(TEST_MESSAGES, 1):
        try:
            res = classify(client, msg, ctx)
            print(f"[{i}] Message: \"{msg}\"")
            print(f"    Risk Level: {res.risk_level}")
            print(f"    Signals: {res.signals}")
            print(f"    Confidence: {res.confidence}")
            print(f"    Third Person: {res.third_person}")
            print("-" * 60)
        except Exception as e:
            print(f"[{i}] ERROR on message: {e}")

if __name__ == "__main__":
    main()

