# MannSahara (मन सहारा)
### AI-Powered Student Mental Health Support & Crisis Safety Companion (SIH25092)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript-61DAFB.svg)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/Styling-TailwindCSS-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> [!IMPORTANT]
> **Prototype & Non-Clinical Disclaimer**: MannSahara is an academic prototype built for student mental wellbeing support. It is **not** a licensed medical, psychological, or psychiatric diagnostic tool, nor does it replace professional emergency services. In real emergencies, individuals should immediately contact **112** (India National Emergency) or **14416 / 1800-891-4416** (Tele-MANAS GoI). All training and evaluation datasets are completely synthetic.

---

## 🌟 Key Features

1. **Multi-Layer Hybrid Safety Architecture**:
   - **Layer 1: Deterministic Rule Engine**: Comprehensive regex matching supporting English and Hinglish expressions with full typo-resilience (e.g., suicide, poison/zeher, building jumps, self-harm, violent harm). Safely filters out harmless idioms (e.g., *"this exam is killing me"*).
   - **Layer 2: Zero-Shot LLM Classifier**: Evaluates veiled, multi-turn, or context-heavy ambiguity using structured JSON classification.
   - **Deterministic State Router**: Gated by LangGraph. Normal (0-1) &rarr; supportive reflection; Ambiguous (2) &rarr; direct check-in template; Crisis (3) &rarr; immediate pre-approved emergency referral template + persistent safety lock.
2. **Strict Output Validator**:
   - Verifies all generated text against banned tokens, medication advice, diagnosis attempts, false claims of contacting services, and incomplete/truncated replies. If validation fails, it triggers a controlled retry before falling back to pre-approved resources.
3. **Multi-Model Provider Flexibility**:
   - **Local Offline Inference**: Ollama (`qwen2.5:1.5b`, `qwen2.5:3b`, `qwen2.5:7b`) for complete data privacy with 0 API cost.
   - **Cloud Providers**: Google Gemini (`gemini-2.5-flash`), Groq (`qwen3.8-27b`), and OpenRouter (`liquid/lfm-2.5-2.6b`).
4. **Verified Indian Crisis Helplines**:
   - Integrated with verified resources from `data/resources.json`:
     - **National Emergency Number (India)**: `112`
     - **Tele-MANAS (Ministry of Health & Family Welfare, GoI)**: `14416` or `1-800-891-4416` (24x7 Free)
     - **Campus Counselling Cell**: Configurable per institution.
5. **Modern Single-Page Application**:
   - Built with React, TypeScript, Tailwind CSS, Framer Motion, and Lucide icons.
   - Features real-time safety badges, simulated escalation indicators, conversation reset, and full safety audit logs.
   - Single-port deployment: FastAPI serves the compiled React frontend directly from `frontend/dist`.

---

## 🏗️ Project Architecture

```
MannSahara/
├── app/
│   ├── alerts.py             # Optional crisis escalation notification system
│   ├── api.py                # FastAPI backend endpoints & static UI serving
│   ├── chatbot.py            # Chatbot session manager & persistent memory
│   ├── config.py             # Environment configurations
│   ├── conversation_risk.py  # Multi-turn risk aggregation & sticky safety lock
│   ├── db.py                 # SQLite storage for turns, audit logs, and metrics
│   ├── graph.py              # LangGraph state machine workflow
│   ├── llm.py                # Multi-provider LLM connector (Ollama, Gemini, Groq, OpenRouter)
│   ├── nodes.py              # Workflow node definitions (assess, router, support, crisis, checkin)
│   ├── resources.py          # Helpline loader and formatter
│   ├── risk_llm.py           # LLM-based secondary classifier
│   ├── risk_rules.py         # Deterministic regex safety rules (English + Hinglish)
│   ├── state.py              # State definition schemas
│   ├── templates.py          # Pre-approved deterministic crisis & check-in responses
│   └── validator.py          # Output validator & safety guardrails
├── data/
│   ├── resources.json        # Verified helpline registry
│   └── test_cases.json       # 66 synthetic test scenarios
├── frontend/
│   ├── src/                  # React + TypeScript frontend source
│   ├── package.json          # Node dependencies & build scripts
│   ├── tailwind.config.js    # Tailwind styling config
│   └── vite.config.ts        # Vite build configuration
├── tests/
│   └── test_core.py          # 11 unit test suites for safety & routing
├── .env.example              # Template environment configuration
├── .gitignore                # Git exclusions (credentials, databases, node_modules)
├── evaluate.py               # 66-case benchmark evaluation engine
├── make_test_cases.py        # Synthetic test data generator
├── requirements.txt          # Python requirements
└── README.md                 # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** & npm
- *(Optional for local AI)*: [Ollama](https://ollama.com/) with `ollama pull qwen2.5:1.5b`

### 1. Installation

Clone the repository:
```bash
git clone https://github.com/suresh4330/MannSahara.git
cd MannSahara
```

Set up the Python environment:
```bash
python -m venv .venv

# Windows:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

Configure environment variables:
```bash
cp .env.example .env
```
Edit `.env` to select your preferred provider (`mock`, `ollama`, `gemini`, `groq`, or `openrouter`).

---

### 2. Build Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

---

### 3. Run the Application

#### Option A: Unified Production Mode (Recommended — Port 8000)
Runs both the FastAPI backend and serves the compiled React UI on a single port:
```bash
python -m uvicorn app.api:api --host 127.0.0.1 --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

#### Option B: Development Mode (Hot-Reload)
- **Backend**:
  ```bash
  python -m uvicorn app.api:api --reload --port 8000
  ```
- **Frontend**:
  ```bash
  cd frontend
  npm run dev
  ```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Testing & Evaluation

### Run Unit Tests
```bash
python -m pytest tests/
```
All **11/11 tests** verify deterministic router decisions, idiom safety, and validator guards.

### Run 66-Case Benchmark Suite
```bash
# Rule-based evaluation (runs 100% offline)
python evaluate.py --split all --mode rules

# Hybrid evaluation (rules + LLM classifier)
python evaluate.py --split all --mode hybrid
```
Reports and metrics are written to `logs/test_log_*.csv` and `logs/metrics_*.json`.

---

## 🛡️ Responsible AI Principles

- **Zero Clinical Claims**: MannSahara never claims to be a doctor, therapist, or emergency service.
- **Privacy By Design**: Conversations can be logged with zero message text (`STORE_MESSAGES=false`). No personal identifying information is transmitted.
- **Fail-Safe Pre-Approved Output**: High-risk scenarios (Level 3 Crisis) **never** generate free-form LLM output. They deterministically output reviewed, pre-approved Indian emergency helpline templates.
- **Persistent Safety Locking**: Once a session triggers a crisis route, subsequent messages remain locked in `safety_followup` mode until the crisis state is addressed.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
