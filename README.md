# MannSahara

**Student Mental Health Support Chatbot — SIH25092**

> ⚠️ **This is an AI prototype for an academic project. It is NOT a counsellor, doctor, or emergency service. It cannot diagnose or treat anything. All test data is synthetic and fictional.**

---

## What it does

MannSahara is a Streamlit chatbot that uses a LangGraph agentic workflow to:
- Assess each student message for risk (rules + optional LLM classifier + conversation memory)
- Route to: supportive reply, check-in question, or crisis template + simulated escalation
- Validate every reply before showing it (output guardrail)
- Log every turn to SQLite
- Run 66 synthetic test cases and display metrics

## Quick start

```bash
# 1. Enter the project folder
cd mannsahara

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and edit the environment file (keep LLM_PROVIDER=mock for offline testing)
copy .env.example .env

# 5. Generate test cases
python make_test_cases.py

# 6. Run unit tests (should show 11 passed)
python -m pytest -q

# 7. Run evaluation
python evaluate.py --split all --mode rules

# 8. Launch the Streamlit app
streamlit run streamlit_app.py
```

## LLM providers

- **mock** (default) — no API key needed, offline mode; only rule-based risk detection
- **gemini** — set `LLM_PROVIDER=gemini` and `GEMINI_API_KEY=...` in `.env`
- **openai** — set `LLM_PROVIDER=openai` and `OPENAI_API_KEY=...`
- **ollama** — set `LLM_PROVIDER=ollama` and run `ollama pull qwen2.5:7b`

## Important disclaimers

- Escalation is **SIMULATED only**. No real contact is made with anyone.
- Do **not** enter real personal information.
- Helpline numbers must be re-verified by the student before any demo.
- This is a university project prototype, not a clinical or medical tool.

