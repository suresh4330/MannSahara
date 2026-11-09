"""Local FastAPI adapter for the MannSahara safety workflow.

This module deliberately delegates every chat turn to ``Chatbot``.  It does not
reimplement classification, routing, templates, validation, or logging.
"""
from __future__ import annotations

import csv
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import alerts, config, llm
from .chatbot import Chatbot
from .db import Store

api = FastAPI(title="MannSahara API", version="1.0.0")
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = Store()
conversations: dict[str, Chatbot] = {}

PROVIDERS = {
    "ollama": {"label": "Ollama (Local)", "models": ["qwen2.5:1.5b", "qwen2.5:3b", "qwen2.5:7b"], "key": None},
    "gemini": {"label": "Google Gemini", "models": ["gemini-3-flash-preview", "gemini-3.5-flash", "gemini-3.5-flash-lite"], "key": "GEMINI_API_KEY"},
    "groq": {"label": "Groq", "models": ["qwen/qwen3.8-27b", "openai/gpt-oss-20b"], "key": "GROQ_API_KEY"},
    "openrouter": {"label": "OpenRouter", "models": ["liquid/lfm-2.5-2.6b:free", "openrouter/free"], "key": "OPENROUTER_API_KEY"},
}


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    message: str = Field(min_length=1, max_length=6000)


class ConfigRequest(BaseModel):
    provider: Literal["mock", "gemini", "groq", "openrouter", "ollama"]
    model: str = Field(min_length=1, max_length=120)
    endpoint: str | None = Field(default=None, max_length=300)
    api_key: str | None = Field(default=None, max_length=500)


def _current_config() -> dict:
    key_name = PROVIDERS.get(config.LLM_PROVIDER, {}).get("key")
    model = "Offline deterministic replies" if config.LLM_PROVIDER == "mock" else (
        config.LLM_MODEL or llm.DEFAULT_MODELS.get(config.LLM_PROVIDER, "")
    )
    return {
        "provider": config.LLM_PROVIDER,
        "model": model,
        "ollama_endpoint": config.OLLAMA_BASE_URL if config.LLM_PROVIDER == "ollama" else None,
        "api_key_configured": bool(getattr(config, key_name, "")) if key_name else False,
        "classifier_enabled": config.USE_LLM_CLASSIFIER,
        "admin_alert_email": config.ADMIN_ALERT_EMAIL,
        "email_alerts_enabled": alerts.enabled(),
    }


def _metrics_files() -> list[Path]:
    return sorted(config.LOG_DIR.glob("metrics_*.json"), key=lambda item: item.stat().st_mtime, reverse=True)


def _load_run(tag: str) -> tuple[dict, list[dict]]:
    metric_path = config.LOG_DIR / f"metrics_{tag}.json"
    log_path = config.LOG_DIR / f"test_log_{tag}.csv"
    if not metric_path.exists():
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    with metric_path.open(encoding="utf-8") as handle:
        metrics = json.load(handle)
    rows = []
    if log_path.exists():
        with log_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    return metrics, rows


@api.get("/api/health")
def health():
    return {"status": "ok", "workflow": "langgraph", "llm": _current_config()}


@api.post("/api/chat")
def chat(payload: ChatRequest):
    conversation_id = payload.conversation_id or str(uuid.uuid4())
    bot = conversations.get(conversation_id)
    if bot is None:
        bot = Chatbot(conversation_id=conversation_id, store=store)
        conversations[conversation_id] = bot
    output = bot.send(payload.message.strip())

    level = output.get("final_level", 0)
    return {
        "conversation_id": conversation_id,
        "reply": output["reply"],
        "timestamp": output.get("turn"),
        "safety": {
            "risk_level": level,
            "route": output.get("route"),
            "escalated": output.get("escalated", False),
            "risk_reasons": output.get("risk_reasons", []),
            "simulated": bool(output.get("escalation_ticket", {}).get("simulated")),
            "validation_ok": output.get("validation_ok", False),
        },
    }


@api.get("/api/conversations")
def list_conversations():
    return [
        {"id": cid, "turns": bot.turn, "preview": bot.history[0]["content"][:70] if bot.history else "New conversation"}
        for cid, bot in conversations.items()
    ]


@api.delete("/api/conversations/{conversation_id}")
def remove_conversation(conversation_id: str):
    conversations.pop(conversation_id, None)
    return {"deleted": True}


@api.get("/api/llm/providers")
def providers():
    return [{"id": provider, "label": details["label"]} for provider, details in PROVIDERS.items()]


@api.get("/api/llm/models")
def models(provider: str):
    if provider not in PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    available = PROVIDERS[provider]["models"][:]
    if provider == "ollama":
        try:
            import urllib.request
            with urllib.request.urlopen(config.OLLAMA_BASE_URL.rstrip("/v1") + "/api/tags", timeout=2) as response:
                installed = [item["name"] for item in json.load(response).get("models", [])]
            available = installed or available
        except Exception:
            pass
    return {"provider": provider, "models": available}


@api.get("/api/llm/config")
def llm_config():
    return _current_config()


@api.post("/api/llm/config")
def update_config(payload: ConfigRequest):
    if payload.provider != "ollama" and payload.endpoint:
        raise HTTPException(status_code=400, detail="Only Ollama supports a configurable endpoint")
    if payload.endpoint and not payload.endpoint.startswith(("http://localhost", "http://127.0.0.1")):
        raise HTTPException(status_code=400, detail="Ollama endpoint must be a local URL")
    config.LLM_PROVIDER = payload.provider
    config.LLM_MODEL = payload.model.strip()
    if payload.endpoint:
        config.OLLAMA_BASE_URL = payload.endpoint.rstrip("/")
    key_name = PROVIDERS[payload.provider]["key"]
    if key_name and payload.api_key:
        setattr(config, key_name, payload.api_key.strip())
    # Future conversations receive the selected runtime config. Existing safety state is never reset.
    return _current_config()


@api.post("/api/llm/test-connection")
def test_connection(payload: ConfigRequest):
    update_config(payload)
    try:
        response = llm.generate("Reply with exactly: connection ready.", [{"role": "user", "content": "Connection test"}], temperature=0)
    except llm.LLMError as exc:
        raise HTTPException(status_code=502, detail="Connection failed. Check the provider, model, key, and endpoint.") from exc
    return {"connected": True, "preview": response[:80]}


@api.get("/api/evaluation/runs")
def evaluation_runs():
    return [{"id": item.stem.removeprefix("metrics_"), "modified": item.stat().st_mtime} for item in _metrics_files()]


@api.get("/api/evaluation/summary")
def evaluation_summary(run: str | None = None):
    if run is None:
        files = _metrics_files()
        if not files:
            return {"available": False}
        run = files[0].stem.removeprefix("metrics_")
    metrics, _ = _load_run(run)
    return {"available": True, "run": run, "metrics": metrics}


@api.get("/api/evaluation/logs")
def evaluation_logs(run: str):
    _, rows = _load_run(run)
    return {"run": run, "rows": rows}


@api.get("/api/evaluation/test-cases")
def test_cases(run: str | None = None):
    with (config.DATA_DIR / "test_cases.json").open(encoding="utf-8") as handle:
        cases = json.load(handle)
    actual = {}
    if run:
        _, rows = _load_run(run)
        actual = {row["id"]: row for row in rows}
    return {"cases": [{**case, "result": actual.get(case["id"])} for case in cases]}


@api.get("/api/safety/overview")
def safety_overview():
    db_path = Path(config.DB_PATH)
    if not db_path.exists():
        return {"available": False, "events": []}
    with sqlite3.connect(db_path) as connection:
        total = connection.execute("SELECT COUNT(*) FROM turns").fetchone()[0]
        escalations = connection.execute("SELECT COUNT(*) FROM escalations").fetchone()[0]
        notifications = connection.execute("SELECT status, COUNT(*) FROM admin_notifications GROUP BY status").fetchall()
        by_level = dict(connection.execute("SELECT final_level, COUNT(*) FROM turns GROUP BY final_level").fetchall())
        rows = connection.execute(
            "SELECT created_at, final_level, route, escalated, risk_reasons FROM turns ORDER BY id DESC LIMIT 12"
        ).fetchall()
    return {
        "available": True,
        "total_turns": total,
        "escalations": escalations,
        "risk_levels": by_level,
        "safety_config": {
            "workflow": "LangGraph", "escalation": "simulated", "validator": "enabled",
            "admin_email_alert": {
                "enabled": alerts.enabled(),
                "recipient_configured": bool(config.ADMIN_ALERT_EMAIL),
                "notifications": dict(notifications),
            },
        },
        "events": [
            {"timestamp": row[0], "risk_level": row[1], "route": row[2], "escalated": bool(row[3]), "triggers": json.loads(row[4] or "[]")}
            for row in rows
        ],
    }


# Static frontend serving for production single-port deployment
dist_dir = Path(__file__).parent.parent / "frontend" / "dist"
if dist_dir.exists():
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    api.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")

    @api.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        target = dist_dir / full_path
        if target.is_file():
            return FileResponse(target)
        return FileResponse(dist_dir / "index.html")
