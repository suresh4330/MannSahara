import os
import sys
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.llm_client import AnthropicClient, MockClient, get_client
from agents.classifier import classify

print("Checking available LLM provider...")
provider = os.getenv("LLM_PROVIDER")
print(f"LLM_PROVIDER env var: {provider}")

# Check Anthropic
auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
base_url = os.getenv("ANTHROPIC_BASE_URL")
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"Has ANTHROPIC_AUTH_TOKEN: {bool(auth_token)}")
print(f"Has ANTHROPIC_BASE_URL: {bool(base_url)}")
print(f"Has ANTHROPIC_API_KEY: {bool(api_key)}")

if auth_token or api_key:
    try:
        os.environ["LLM_PROVIDER"] = "anthropic"
        client = get_client()
        print("Testing complete() with anthropic client...")
        res = client.complete("You are a helpful assistant.", "Reply with only the word OK", 10)
        print(f"Anthropic response: {res}")
    except Exception as e:
        print(f"Anthropic test failed with: {type(e).__name__}: {e}")

