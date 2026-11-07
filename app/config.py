"""Central configuration. All settings come from environment variables / .env."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
LLM_MODEL = os.getenv("LLM_MODEL", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
USE_LLM_CLASSIFIER = os.getenv("USE_LLM_CLASSIFIER", "true").lower() == "true"
STORE_MESSAGES = os.getenv("STORE_MESSAGES", "true").lower() == "true"
DB_PATH = os.getenv("DB_PATH", str(ROOT / "mannsahara.db"))
MAX_HISTORY_TURNS = 10      # how many past messages the LLM sees
ACCUMULATION_WINDOW = 3     # turns to look back for repeated ambiguous signals

