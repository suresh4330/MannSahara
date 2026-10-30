import os
import requests

auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
headers = {"Authorization": f"Bearer {auth_token}"}
r = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=15)
if r.status_code == 200:
    models = [m["id"] for m in r.json().get("data", [])]
    # Filter for popular models like anthropic, openai, gemini, llama
    fast_models = [m for m in models if any(k in m for k in ["flash", "haiku", "gpt-4o-mini", "llama-3"])]
    print("Found models:", len(models))
    print("Sample fast models:", fast_models[:10])
else:
    print("Failed to fetch models:", r.status_code, r.text)

