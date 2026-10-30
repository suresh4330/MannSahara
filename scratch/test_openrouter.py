import os
import requests

auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
base_url = os.getenv("ANTHROPIC_BASE_URL")
print(f"Base URL: {base_url}")

# Let's test standard OpenRouter chat completions endpoint
if "openrouter" in base_url.lower():
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "google/gemini-2.0-flash-001",
        "messages": [{"role": "user", "content": "Reply with only 'ONLINE'"}],
        "max_tokens": 10
    }
    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        print("Status code:", r.status_code)
        print("Response:", r.text[:300])
    except Exception as e:
        print("Error:", e)

