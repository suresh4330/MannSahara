import os
import sys
import pathlib
import requests
import json

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
endpoint = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {auth_token}",
    "Content-Type": "application/json"
}

from agents.classifier import SYSTEM, build_user_prompt
prompt = build_user_prompt("I want to end my life tonight, I can't take it anymore.", [])

models_to_test = [
    "deepseek/deepseek-chat",
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-small-24b-instruct-2501",
    "qwen/qwen-2.5-72b-instruct"
]

for m in models_to_test:
    print(f"\n--- Testing {m} ---")
    payload = {
        "model": m,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150
    }
    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=20)
        if r.status_code == 200:
            print("Status 200! Output:", r.json()["choices"][0]["message"]["content"])
        else:
            print(f"Status {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print("Error:", e)
