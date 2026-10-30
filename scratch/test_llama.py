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
    "model": "meta-llama/llama-3.1-8b-instruct",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Output strictly JSON: {\"risk_level\": 0, \"signals\": [], \"confidence\": 0.9, \"third_person\": false}"}
    ],
    "max_tokens": 150
}
r = requests.post(endpoint, headers=headers, json=payload, timeout=20)
print(json.dumps(r.json(), indent=2))

