import os
import requests

auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
headers = {"Authorization": f"Bearer {auth_token}"}
r = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=15)
data = r.json().get("data", [])
# Look for free models or standard low-cost models
free_models = [m["id"] for m in data if m.get("pricing", {}).get("prompt") == "0"]
print("Free models:", free_models[:10])
gemini_models = [m["id"] for m in data if "gemini" in m["id"].lower()]
print("Gemini models:", gemini_models[:5])
llama_models = [m["id"] for m in data if "llama" in m["id"].lower() and "8b" in m["id"].lower()]
print("Llama 8b models:", llama_models[:5])

