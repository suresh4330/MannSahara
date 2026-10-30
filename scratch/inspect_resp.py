import os
import requests
import json

auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
endpoint = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {auth_token}",
    "Content-Type": "application/json"
}

payload = {
    "model": "google/gemini-3.8-flash",
    "messages": [{"role": "user", "content": "Respond only with: OK"}],
    "max_tokens": 50
}
r = requests.post(endpoint, headers=headers, json=payload, timeout=20)
print(json.dumps(r.json(), indent=2))

