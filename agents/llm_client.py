"""Provider-neutral LLM client supporting OpenRouter, Ollama, Anthropic, OpenAI, Gemini, and Mock.
Adheres to Section 4 and Section 3.4 of the implementation guide.
"""
import os
import requests


def _get_setting(key: str, default: str = "") -> str:
    """Read a setting from os.environ, falling back to st.secrets for Streamlit Cloud."""
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default


class LLMClient:
    backend = "base"

    def complete(self, system: str, user: str, max_tokens: int = 300) -> str:
        raise NotImplementedError


class OpenRouterClient(LLMClient):
    backend = "openrouter"

    def __init__(self):
        self.api_key = (
            _get_setting("OPENROUTER_API_KEY")
            or _get_setting("ANTHROPIC_AUTH_TOKEN")
            or _get_setting("OPENAI_API_KEY")
        )
        if not self.api_key:
            raise ValueError("No API token found for OpenRouter (set OPENROUTER_API_KEY or ANTHROPIC_AUTH_TOKEN)")
        self.model = _get_setting("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct")
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def complete(self, system: str, user: str, max_tokens: int = 300) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.0,
        }
        r = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        choice = data["choices"][0]["message"]
        content = choice.get("content")
        if not content and "reasoning" in choice:
            content = choice.get("reasoning")
        return (content or "").strip()


class OllamaClient(LLMClient):
    backend = "ollama"

    def __init__(self):
        self.model = os.environ.get("LLM_MODEL", "llama3.2")
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    def complete(self, system: str, user: str, max_tokens: int = 300) -> str:
        r = requests.post(
            f"{self.host}/api/chat",
            timeout=90,
            json={
                "model": self.model,
                "stream": False,
                "options": {"temperature": 0, "num_predict": max_tokens},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        r.raise_for_status()
        return r.json()["message"]["content"]


class AnthropicClient(LLMClient):
    backend = "anthropic"

    def __init__(self):
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
        base_url = os.getenv("ANTHROPIC_BASE_URL")
        self.c = anthropic.Anthropic(api_key=api_key, base_url=base_url) if base_url else anthropic.Anthropic(api_key=api_key)
        self.model = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")

    def complete(self, system: str, user: str, max_tokens: int = 300) -> str:
        r = self.c.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=0,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return r.content[0].text


class OpenAIClient(LLMClient):
    backend = "openai"

    def __init__(self):
        import openai
        self.c = openai.OpenAI()
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    def complete(self, system: str, user: str, max_tokens: int = 300) -> str:
        r = self.c.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return r.choices[0].message.content


class GeminiClient(LLMClient):
    backend = "gemini"

    def __init__(self):
        from google import genai
        self.client = genai.Client()
        self.model = os.getenv("LLM_MODEL", "gemini-2.5-flash")

    def complete(self, system: str, user: str, max_tokens: int = 300) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=user,
            config={
                "system_instruction": system,
                "temperature": 0.0,
                "max_output_tokens": max_tokens,
            },
        )
        return response.text


class MockClient(LLMClient):
    backend = "mock"

    def complete(self, system: str, user: str, max_tokens: int = 300) -> str:
        # DEVELOPMENT ONLY. Results must be labeled as not from a real LLM.
        return '{"risk_level": 0, "signals": [], "confidence": 0.1, "third_person": false}'


def get_client() -> LLMClient:
    from dotenv import load_dotenv
    load_dotenv()
    p = _get_setting("LLM_PROVIDER", "mock").lower()
    if p == "openrouter":
        return OpenRouterClient()
    if p == "ollama":
        return OllamaClient()
    if p == "anthropic":
        return AnthropicClient()
    if p == "openai":
        return OpenAIClient()
    if p == "gemini":
        return GeminiClient()
    if p == "mock":
        return MockClient()
    raise ValueError(f"unsupported LLM_PROVIDER: {p}")
