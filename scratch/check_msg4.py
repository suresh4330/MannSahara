import os
import sys
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.llm_client import get_client
from agents.classifier import SYSTEM, build_user_prompt

client = get_client()
prompt = build_user_prompt("I want to end my life tonight, I can't take it anymore.", [])
raw = client.complete(SYSTEM, prompt, 200)
print(f"RAW OUTPUT: length={len(raw)}")
print(repr(raw))

