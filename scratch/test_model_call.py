import os
import requests

auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
endpoint = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {auth_token}",
    "Content-Type": "application/json"
}

for model in ["google/gemini-3.8-flash", "meta-llama/llama-3.1-8b-instruct"]:
    print(f"Testing {model}...")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Return JSON: {\"status\": \"ok\"}"}],
        "max_tokens": 50
    }
    r = requests.post(endpoint, headers=headers, json=payload, timeout=20)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("Success! Reply:", r.json()["choices"][0]["message"]["content"])
        break
    else:
        print("Error:", r.text[:200])

