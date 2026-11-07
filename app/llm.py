"""One function, generate().
The mock provider needs no internet and no API key. It lets you run and test the whole
workflow offline. In mock mode the LLM classifier always answers level 0, so only the
rule layer decides risk.
"""
import json
from . import config

DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o-mini",
    "ollama": "qwen2.5:7b",
}


class LLMError(Exception):
    """Raised for any provider failure (network, key, blocked output, ...)"""


def _mock(system: str, json_mode: bool):
    if json_mode:
        return json.dumps({"risk_level": 0, "reason": "mock provider", "third_person": False})
    if "flagged as high-risk" in system:
        return (
            "I'm still here with you. Please try to reach someone you trust or one of the "
            "helplines I shared. Is there anyone who can be with you right now?"
        )
    return (
        "That sounds really stressful, and it makes sense that it is weighing on you. "
        "Would you like to tell me more about what has been hardest lately? "
        "I'm an AI, not a counsellor, but I'm happy to listen and share some simple ways to cope."
    )


def _gemini(system, messages, json_mode, temperature, model):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])]
        )
        for m in messages
    ]
    cfg = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        response_mime_type="application/json" if json_mode else None,
    )
    resp = client.models.generate_content(model=model, contents=contents, config=cfg)
    text = getattr(resp, "text", None)
    if not text:
        raise LLMError("Empty response (possibly blocked by the provider's safety filter)")
    return text


def _openai_compatible(system, messages, json_mode, temperature, model, provider):
    from openai import OpenAI
    if provider == "ollama":
        client = OpenAI(base_url=config.OLLAMA_BASE_URL, api_key="ollama")
    else:
        client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL or None)
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
        kwargs["max_tokens"] = 250
    else:
        kwargs["max_tokens"] = 600
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}] + messages,
        temperature=temperature,
        **kwargs,
    )
    text = resp.choices[0].message.content
    if not text:
        raise LLMError("Empty response from model")
    return text


def generate(system, messages, json_mode=False, temperature=0.4):
    """messages: list of {"role": "user"|"assistant", "content": str}. Raises LLMError."""
    provider = config.LLM_PROVIDER
    model = config.LLM_MODEL or DEFAULT_MODELS.get(provider, "")
    try:
        if provider == "mock":
            return _mock(system, json_mode)
        if provider == "gemini":
            return _gemini(system, messages, json_mode, temperature, model)
        if provider in ("openai", "ollama"):
            return _openai_compatible(system, messages, json_mode, temperature, model, provider)
    except LLMError:
        raise
    except Exception as exc:  # network, auth, quota, bad JSON mode, ...
        raise LLMError(f"{type(exc).__name__}: {exc}")
    raise LLMError(f"Unknown LLM_PROVIDER '{provider}'")

