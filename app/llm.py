"""One function, generate().
The mock provider needs no internet and no API key. It lets you run and test the whole
workflow offline. In mock mode the LLM classifier always answers level 0, so only the
rule layer decides risk.
"""
import json
from urllib import request
from . import config

DEFAULT_MODELS = {
    "gemini": "gemini-3-flash-preview",
    "groq": "qwen/qwen3.8-27b",
    "openrouter": "liquid/lfm-2.5-2.6b:free",
    "ollama": "qwen2.5:1.5b",
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
    max_tokens = max(150, config.CLASSIFIER_MAX_OUTPUT_TOKENS if json_mode else config.LLM_MAX_OUTPUT_TOKENS)
    cfg_args = dict(
        system_instruction=system,
        temperature=temperature,
        response_mime_type="application/json" if json_mode else None,
        max_output_tokens=max_tokens,
    )
    try:
        cfg = types.GenerateContentConfig(
            **cfg_args,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
        resp = client.models.generate_content(model=model, contents=contents, config=cfg)
    except Exception as exc:
        if "INVALID_ARGUMENT" in str(exc) or "thinking_config" in str(exc):
            cfg = types.GenerateContentConfig(**cfg_args)
            resp = client.models.generate_content(model=model, contents=contents, config=cfg)
        else:
            raise
    text = getattr(resp, "text", None)
    if not text:
        raise LLMError("Empty response (possibly blocked by the provider's safety filter)")
    return text


def _chat_completion(base_url, api_key, system, messages, json_mode, temperature, model, extra_headers=None):
    max_tokens = max(150, config.CLASSIFIER_MAX_OUTPUT_TOKENS if json_mode else config.LLM_MAX_OUTPUT_TOKENS)
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}] + messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    if extra_headers:
        headers.update(extra_headers)

    req_data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=req_data,
        headers=headers,
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=config.LLM_TIMEOUT_SECONDS) as response:
            text = json.loads(response.read())["choices"][0]["message"]["content"]
    except Exception as exc:
        # If json_object format was rejected by a provider model (HTTP 400), retry without response_format
        if json_mode and "response_format" in payload:
            payload.pop("response_format", None)
            retry_req = request.Request(
                base_url.rstrip("/") + "/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with request.urlopen(retry_req, timeout=config.LLM_TIMEOUT_SECONDS) as response:
                text = json.loads(response.read())["choices"][0]["message"]["content"]
        else:
            raise
    if not text:
        raise LLMError("Empty response from model")
    return text


def _ollama(system, messages, json_mode, temperature, model):
    # Optimized for fast CPU/iGPU generation on laptops
    max_tokens = 40 if json_mode else min(90, config.LLM_MAX_OUTPUT_TOKENS)
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}] + messages,
        "stream": False,
        "keep_alive": "60m",
        "options": {
            "temperature": temperature,
            "num_ctx": 512,
            "num_predict": max_tokens,
            "num_thread": 4,
            "repeat_penalty": 1.1,
        },
    }
    if json_mode:
        payload["format"] = "json"
    native_url = config.OLLAMA_BASE_URL.rstrip("/")
    if native_url.endswith("/v1"):
        native_url = native_url[:-3]
    req = request.Request(
        native_url + "/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with request.urlopen(req, timeout=config.LLM_TIMEOUT_SECONDS) as response:
        text = json.loads(response.read())["message"]["content"]
    if not text:
        raise LLMError("Empty response from Ollama")
    return text


def _groq(system, messages, json_mode, temperature, model):
    return _chat_completion(
        "https://api.groq.com/openai/v1", config.GROQ_API_KEY,
        system, messages, json_mode, temperature, model,
    )


def _openrouter(system, messages, json_mode, temperature, model):
    return _chat_completion(
        "https://openrouter.ai/api/v1", config.OPENROUTER_API_KEY,
        system, messages, json_mode, temperature, model,
        extra_headers={"HTTP-Referer": "http://localhost:5173", "X-Title": "MannSahara"}
    )


def generate(system, messages, json_mode=False, temperature=0.4):
    """messages: list of {"role": "user"|"assistant", "content": str}. Raises LLMError."""
    provider = config.LLM_PROVIDER
    model = config.LLM_MODEL or DEFAULT_MODELS.get(provider, "")
    try:
        if provider == "mock":
            return _mock(system, json_mode)
        if provider == "gemini":
            return _gemini(system, messages, json_mode, temperature, model)
        if provider == "ollama":
            return _ollama(system, messages, json_mode, temperature, model)
        if provider == "groq":
            return _groq(system, messages, json_mode, temperature, model)
        if provider == "openrouter":
            return _openrouter(system, messages, json_mode, temperature, model)
    except LLMError:
        raise
    except Exception as exc:  # network, auth, quota, bad JSON mode, ...
        raise LLMError(f"{type(exc).__name__}: {exc}")
    raise LLMError(f"Unknown LLM_PROVIDER '{provider}'")

