"""Central configuration. All settings come from environment variables / .env."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
# Environment variables supplied by the host (tests, deployment, or a process
# manager) take precedence over local development defaults in .env.
load_dotenv(ROOT / ".env")
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
LLM_MODEL = os.getenv("LLM_MODEL", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
USE_LLM_CLASSIFIER = os.getenv("USE_LLM_CLASSIFIER", "true").lower() == "true"
STORE_MESSAGES = os.getenv("STORE_MESSAGES", "true").lower() == "true"
DB_PATH = os.getenv("DB_PATH", str(ROOT / "mannsahara.db"))
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "6"))
LLM_MAX_OUTPUT_TOKENS = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "250"))
CLASSIFIER_MAX_OUTPUT_TOKENS = int(os.getenv("CLASSIFIER_MAX_OUTPUT_TOKENS", "150"))
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
# Optional prototype admin notification. This is never an emergency-service
# integration and is disabled unless the required Gmail settings are present.
EMAIL_ALERTS_ENABLED = os.getenv("EMAIL_ALERTS_ENABLED", "false").lower() == "true"
ADMIN_ALERT_EMAIL = os.getenv("ADMIN_ALERT_EMAIL", "").strip()
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
EMAIL_ALERT_TIMEOUT_SECONDS = int(os.getenv("EMAIL_ALERT_TIMEOUT_SECONDS", "12"))
# Keep the local model loaded between turns and constrain its working context.
# These affect Ollama only; provider-hosted models ignore them.
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "30m")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "1024"))
ACCUMULATION_WINDOW = 3     # turns to look back for repeated ambiguous signals

