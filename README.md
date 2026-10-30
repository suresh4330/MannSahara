# MannSahara — Two-Agent AI Safety & Triage Platform

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://mannsahara-hk2ew72zzavcm9dkvhlepm.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/Framework-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Meta_Llama_3.3_70B-purple?style=for-the-badge&logo=meta&logoColor=white)
![Provider](https://img.shields.io/badge/Provider-OpenRouter-007ACC?style=for-the-badge)
![Crisis Safety Recall](https://img.shields.io/badge/Crisis_Recall-100%25-10B981?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**MannSahara** is a production-grade, two-agent AI safety, triage, and student mental health support platform architected for university academic environments (CSE473 / Smart India Hackathon SIH25092). It couples a deterministic regex safety net (with bilingual English & Hinglish coverage) with a Meta Llama 3.3 70B Instruct classifier, a multi-turn crisis latching state tracker, and an empathetic Coping Agent bound by strict clinical guardrails. In crisis scenarios, the system autonomously bypasses generative AI to immediately dispatch verified national emergency hotlines (Tele-MANAS, KIRAN, 112) and simulated counselor notifications.

> **Repository**: [https://github.com/suresh4330/MannSahara.git](https://github.com/suresh4330/MannSahara.git)  
> **Live Web Application**: [https://mannsahara-hk2ew72zzavcm9dkvhlepm.streamlit.app/](https://mannsahara-hk2ew72zzavcm9dkvhlepm.streamlit.app/)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Feature Highlights](#2-feature-highlights)
3. [What's New](#3-whats-new)
4. [Resume Highlights](#4-resume-highlights)
5. [Screenshots & UI Walkthrough](#5-screenshots--ui-walkthrough)
6. [Tech Stack](#6-tech-stack)
7. [Architecture](#7-architecture)
8. [How It Works](#8-how-it-works)
9. [Project Structure](#9-project-structure)
10. [Safety Triage & Defense Reference](#10-safety-triage--defense-reference)
11. [Environment Variables](#11-environment-variables)
12. [Run Locally](#12-run-locally)
13. [Run with Docker & Compose](#13-run-with-docker--compose)
14. [Troubleshooting](#14-troubleshooting)
15. [FAQ](#15-faq)
16. [Contributing](#16-contributing)
17. [Changelog](#17-changelog)
18. [Roadmap](#18-roadmap)
19. [Author](#19-author)
20. [License](#20-license)

---

## 1. Overview

University students frequently face acute academic distress, burnout, and emotional fatigue. While large language models can provide empathetic listening, unconstrained generative chatbots present critical clinical liabilities: fabricating medical advice, failing to detect subtle suicidal ideation, or hallucinating emergency contacts.

**MannSahara** solves this by establishing a **dual-agent defense pipeline**:
- **Agent 1 (Safety Gateway)**: Evaluates student turns in real time via deterministic regex rules and zero-temperature LLM classification, calculating a safety score $\max(\text{Rules}, \text{LLM})$ and updating a stateful multi-turn risk tracker.
- **Agent 2 (Coping Agent)**: Operates only within safe boundaries (Levels 0–2), generating empathetic, non-clinical grounding exercises and campus counseling referrals.
- **Deterministic Crisis Bypass**: At Level 3 (Crisis), generative LLM inference is completely bypassed. Fixed, clinically approved emergency resources and verified Indian national crisis hotlines are dispatched alongside simulated counselor alert payloads.

> **Research Prototype Notice**: MannSahara is an academic research prototype. It is **not therapy**, does **not diagnose or treat** medical conditions, and does not replace licensed psychological care.

---

## 2. Feature Highlights

- **Bilingual Deterministic Safety Net**: Hand-crafted, normalized regex patterns detecting explicit suicide, self-harm, and severe distress across English and Hinglish idioms (*"khatam karna chahta hoon"*, *"marne ka man karta hai"*).
- **Hyperbole Trap Disambiguation**: Contextual idiom filtering preventing false crisis alarms on benign academic hyperbole (*"this compiler assignment is killing me lol"*, *"dying to go home"*).
- **Hybrid Resolution Engine**: Multi-tiered scoring implementing $\max(\text{Rules}, \text{LLM})$ ensuring zero safety regression if the LLM classifier is slow or errs.
- **Multi-Turn Crisis Latch**: State tracker that irreversibly locks the session to Level 3 once crisis ideation is flagged, preventing students from talking the bot down into casual chat.
- **Persistence & Repetition Escalation**: Automatically elevates Level 1 distress to Level 2 (Campus Referral) if symptoms persist across 3+ consecutive turns or recur repeatedly.
- **Strict Output Guardrails**: Deterministic regex filter scanning assistant drafts to block unauthorized medical diagnoses, psychiatric prescriptions, method details, and therapist impersonation.
- **Real-Time Safety Telemetry Console**: Linear-inspired obsidian dashboard displaying live triage stages, tri-score breakdowns, prompt injection shields, and CSV audit downloads.
- **Verified Emergency Helplines**: Pre-verified official Indian government support hotlines:
  - **Tele-MANAS**: `14416` (Govt of India · 24x7 Free)
  - **KIRAN Mental Health**: `1800-599-0019` (Ministry of Social Justice)
  - **National Emergency**: `112`

---

## 3. What's New

### Version 2.0.0 Production Release
- **Linear-Inspired UI/UX Redesign**: Built from scratch with an obsidian dark theme (`#0D0F14`), elevated surfaces (`#1C202C`), Inter typography, and crisp SVG telemetry icons.
- **Instant Suggested Scenarios**: 4 interactive test cards (*Exam Stress*, *Insomnia*, *Academic Withdrawal*, *Hyperbole Trap*) for instant evaluator testing without typing.
- **Direct Benchmark Scorecard**: Integrated scorecard displaying verified evaluation metrics directly in the sidebar.
- **Single-Click Streamlit Cloud Deployment**: Native `.streamlit/config.toml` setup with entrypoint aliases for effortless cloud hosting.
- **100.0% Crisis Safety Recall**: Reached 70/70 crisis detection on the 156-dialogue development evaluation split with 0.0% false-alarm rate.

---

## 4. Resume Highlights

```
• Architected a dual-agent mental health safety pipeline (Safety Gateway + Coping Agent) utilizing Meta Llama 3.3 70B, achieving 100.0% crisis recall and 0.0% false-alarm rate across 156 multi-turn evaluation dialogues.
• Designed a hybrid multi-tier triage resolution system combining bilingual regex rules (English + Hinglish) with zero-temperature LLM classification, ensuring deterministic non-LLM bypass during Level 3 emergencies.
• Engineered stateful multi-turn risk tracking with irreversible crisis latching and symptom persistence escalation algorithms.
• Developed deterministic output guardrails intercepting unauthorized diagnostic claims, medication advice, and prompt injections.
• Built a high-performance Streamlit UI inspired by Linear design systems featuring real-time telemetry gauges and downloadable audit logs.
```

---

## 5. Screenshots & UI Walkthrough

### High-Contrast Obsidian Design System
The UI provides an AI safety operations command center with high-contrast elements and zero amateur emoji styling:

1. **Left Sidebar (Safety Command Center)**:
   - Dynamic 4-stage active triage state (`Level 0` Safe Green $\rightarrow$ `Level 1` Cyan $\rightarrow$ `Level 2` Amber $\rightarrow$ `Level 3` Crisis Crimson).
   - Real-time Multi-Agent Scoring Matrix comparing Deterministic Rules vs. LLM Classifier vs. Hybrid Resolution.
   - Active Defense Verification table (Prompt Injection, Output Guardrails, Crisis Latch, Generation Mode).
   - Verified Dev Benchmark Scorecard (100% Crisis Recall, 0% False Alarm, 95.5% Accuracy) with CSV download.
2. **Main Conversation Interface**:
   - Academic & Research Safety Notice communicating prototype boundaries.
   - 4 quick-action test scenario cards arranged above the fold.
   - Distinct student and assistant chat bubbles with timestamps and triage badges.
   - High-visibility Level 3 Emergency Panel with direct-dial hotline cards.

---

## 6. Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend & UI** | Streamlit 1.61, Custom CSS (Linear Obsidian Design System), HTML5, SVG Icons |
| **Core Language** | Python 3.11+ |
| **Language Models** | Meta Llama 3.3 70B Instruct (`meta-llama/llama-3.3-70b-instruct`) via OpenRouter |
| **Provider Neutrality**| OpenRouter, Ollama, Anthropic Claude, OpenAI GPT-4o, Google Gemini, Mock Client |
| **Data & Validation** | Pydantic v2 (Strict Schema Enforcement), Python Dataclasses |
| **Evaluation & Tests**| Pytest (43 Unit Tests), Pandas, Custom Wilson Score Interval Statistics |
| **DevOps & Container**| Docker, Docker Compose, Git, Streamlit Community Cloud |

---

## 7. Architecture

```
                             Student Turn
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │               AGENT 1: SAFETY GATEWAY                  │
      │  • Deterministic Rules Layer (English + Hinglish)      │
      │  • LLM Risk Classifier (JSON Schema Enforcement)       │
      │  • Hybrid Score Resolution: max(Rules, LLM)            │
      │  • Stateful Multi-Turn Tracker (Crisis Latch & T1/T2)  │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
                        ROUTER (Tracked Level)
         ┌─────────────┬─────────────┬─────────────┬──────────────┐
         ▼             ▼             ▼             ▼              │
    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────────┐ │
    │ Level 0 │   │ Level 1 │   │ Level 2 │   │     Level 3     │ │
    │ Routine │   │ Ground- │   │ Campus  │   │  CRISIS BYPASS  │ │
    │ Support │   │   ing   │   │ Referral│   │ (Zero LLM Call) │ │
    └────┬────┘   └────┬────┘   └────┬────┘   └────────┬────────┘ │
         │             │             │                 │          │
         └─────────────┼─────────────┘                 │          │
                       ▼                               ▼          │
      ┌─────────────────────────────────┐   ┌───────────────────┐ │
      │      AGENT 2: COPING AGENT      │   │ Deterministic     │ │
      │  (Empathetic Non-Clinical LLM)  │   │ Crisis Response   │ │
      └────────────────┬────────────────┘   │ • Tele-MANAS 14416│ │
                       │                    │ • KIRAN 1800599001│ │
                       ▼                    │ • Emergency 112   │ │
      ┌─────────────────────────────────┐   │ • Counselor Alert │ │
      │        OUTPUT GUARDRAILS        │   └─────────┬─────────┘ │
      │ (Regex Filter: No Diagnoses /   │             │           │
      │  No Prescriptions / No Claims)  │             │           │
      └────────────────┬────────────────┘             │           │
                       │                              │           │
                       ▼                              ▼           ▼
                   Safe Empathetic Reply         Emergency Hotline Card
```

---

## 8. How It Works

1. **Intake & Normalization**: The student input is decoded, stripped of invisible control characters, and normalized via Unicode NFKD.
2. **Deterministic Rules Evaluation**: The input runs against regex patterns detecting explicit self-harm, third-person crises, prompt injection attempts, and benign idioms.
3. **Structured LLM Classification**: In non-crisis cases, the input is analyzed by Meta Llama 3.3 70B with strict temperature 0.0, outputting a structured JSON schema: `{"risk_level": int, "signals": list, "confidence": float}`.
4. **Hybrid Resolution**: The system applies $\max(\text{Rules}, \text{LLM})$. If either flagged risk, the higher severity is adopted. If the LLM throws a timeout or error, the system fails closed to rules + safe fallback.
5. **Stateful Multi-Turn Tracking**:
   - If Level 3 is ever reached, the session **latches** into crisis mode permanently.
   - If Level 1 distress persists for 3+ consecutive turns, it automatically escalates to Level 2.
6. **Conditional Execution**:
   - **Levels 0–2**: The Coping Agent receives a constrained prompt, formulating supportive active listening and grounding exercises. The draft is validated against output guardrails before display.
   - **Level 3**: The Coping Agent LLM is **never invoked**. A pre-verified crisis message with official Indian helpline numbers is rendered immediately.

---

## 9. Project Structure

```
MannSahara/
├── .streamlit/
│   └── config.toml                # Native Streamlit dark theme settings
├── agents/
│   ├── classifier.py              # Zero-temp structured JSON LLM classifier
│   ├── coping_agent.py            # Empathetic coping response agent (Levels 0-2)
│   ├── guardrail.py               # Deterministic output safety filter
│   ├── llm_client.py              # Provider-neutral LLM client (OpenRouter/Ollama/etc.)
│   ├── rules.py                   # Bilingual regex safety net (English + Hinglish)
│   ├── safety_gateway.py          # Hybrid score combiner with fallback logic
│   ├── schemas.py                 # Pydantic v2 schemas for all telemetry
│   └── tracker.py                 # Multi-turn state tracker with crisis latch
├── config/
│   ├── resources.json             # Verified national helplines & campus contacts
│   └── templates.py               # Clinically approved deterministic reply templates
├── data/
│   ├── dev_dialogues.json         # 156 synthetic development dialogues
│   └── heldout_dialogues.json     # 44 frozen held-out evaluation dialogues
├── evaluation/
│   ├── ablation.py                # Comparative study (Rules vs LLM vs Hybrid)
│   ├── metrics.py                 # Evaluation metrics & Wilson score statistics
│   └── run_eval.py                # CLI evaluation runner
├── results/
│   ├── metrics.json               # Full evaluation metrics scorecard
│   ├── test_log.csv               # Complete 156-dialogue dev audit log
│   ├── RESULTS.md                 # Detailed research results breakdown
│   └── FAILURES.md                # Qualitative error analysis
├── tests/
│   ├── test_classifier.py         # Unit tests for JSON classifier
│   ├── test_dataset.py            # Dataset integrity & SHA-256 checks
│   ├── test_guardrail.py          # Output guardrail enforcement tests
│   ├── test_hybrid.py             # Hybrid scoring & fallback tests
│   ├── test_resources.py          # Helpline lookup & simulation tests
│   ├── test_router.py             # Router & level-3 bypass tests
│   ├── test_rules.py              # Regex rules & Hinglish idiom tests
│   └── test_tracker.py            # Multi-turn latching & persistence tests
├── tools/
│   ├── coping_tools.py            # Grounding, 4-7-8 breathing & sleep techniques
│   ├── notify_counselor_sim.py    # Simulated campus counselor alert dispatcher
│   └── resource_lookup.py         # Helpline lookup with verification checks
├── .env.example                   # Sanitized environment template
├── app.py                         # Production Streamlit web application
├── Dockerfile                     # Production container specification
├── docker-compose.yml             # Container orchestration
├── requirements.txt               # Locked production dependencies
├── router.py                      # Multi-agent pipeline orchestrator
└── streamlit_app.py               # Streamlit Cloud deployment entrypoint
```

---

## 10. Safety Triage & Defense Reference

### The 4-Tier Triage Taxonomy

| Level | Clinical Severity | Trigger Signals | System Action | Generation Engine |
| :---: | :--- | :--- | :--- | :--- |
| **Level 0** | **Normal Stress** | Exam anxiety, study focus, benign hyperbole (*"killing me lol"*) | Supportive active listening | Empathetic LLM |
| **Level 1** | **Mild Distress** | Sleep disruption, low energy, mild academic burnout | Supportive reflection + grounding exercise | Empathetic LLM |
| **Level 2** | **Moderate Distress** | 3+ turns of hopelessness, withdrawal, missing classes | Supportive reflection + Campus Counseling Referral | Empathetic LLM |
| **Level 3** | **Crisis** | Suicidal ideation, self-harm, coded goodbyes, method requests | **Emergency Hotline Dispatch + Simulated Counselor JSON** | **Bypassed (Deterministic)** |

### Active Defenses & Mitigations

```
┌───────────────────────────┬────────────────────────────────────────────────────────┐
│ Defense Mechanism         │ Operational Behavior                                   │
├───────────────────────────┼────────────────────────────────────────────────────────┤
│ Prompt Injection Shield   │ Intercepts "ignore rules", roleplay, and system probes │
│ Output Guardrail Filter   │ Intercepts diagnosis, medication names, dosage advice  │
│ Multi-Turn Crisis Latch   │ Locks session to Level 3; student cannot de-escalate   │
│ Persistence Escalator     │ Elevates Level 1 to Level 2 after 3 consecutive turns  │
│ Deterministic Bypass      │ Coping Agent LLM is NEVER invoked during Level 3       │
│ Offline Fallback Mode     │ Fails closed to rules + safe fallback on LLM errors    │
└───────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 11. Environment Variables

Configure your `.env` file in the project root:

```ini
# Core LLM Provider Configuration
LLM_PROVIDER=openrouter               # Options: openrouter | ollama | anthropic | openai | gemini | mock
LLM_MODEL=meta-llama/llama-3.3-70b-instruct

# Provider Authentication (Provide ONLY the key for your active provider)
OPENROUTER_API_KEY=sk-or-v1-...       # Your OpenRouter API Key
OLLAMA_HOST=http://localhost:11434    # Used only if LLM_PROVIDER=ollama
ANTHROPIC_API_KEY=                    # Used only if LLM_PROVIDER=anthropic
OPENAI_API_KEY=                       # Used only if LLM_PROVIDER=openai
GEMINI_API_KEY=                       # Used only if LLM_PROVIDER=gemini
```

---

## 12. Run Locally

### Prerequisites
- Python 3.11 or 3.12
- Git

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/suresh4330/MannSahara.git
cd MannSahara

# 2. Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and paste your OPENROUTER_API_KEY

# 5. Run automated test suite (43 tests)
pytest -q

# 6. Launch the Streamlit application
streamlit run app.py
```

The application will be live at `http://localhost:8501`.

---

## 13. Run with Docker & Compose

### Using Docker Compose
```bash
# Set your API key in .env, then run:
docker-compose up --build
```
Access the application at `http://localhost:8501`.

### Using Docker CLI Directly
```bash
# Build Docker image
docker build -t mannsahara:latest .

# Run container with environment variable
docker run -p 8501:8501 --env OPENROUTER_API_KEY=your_key_here mannsahara:latest
```

---

## 14. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `ValueError: No API token found` | Missing `OPENROUTER_API_KEY` | Set `OPENROUTER_API_KEY` in `.env` or cloud secrets. |
| `Port 8501 is already in use` | Another Streamlit instance is running | Kill the previous process or run with `--server.port 8502`. |
| `TypeError: classify() missing arguments`| Signature mismatch | Pass `classify(client, text, context)`. |
| Blank or Light UI styling | Streamlit theme default | Ensure `.streamlit/config.toml` exists with `base = "dark"`. |
| Python 3.14 build errors on Linux | Missing pre-built binary wheels | Switch Python version to `3.11` or `3.12`. |

---

## 15. FAQ

#### Q: Is MannSahara an AI therapist?
**No.** MannSahara is an academic research prototype for safety triage and supportive grounding. It explicitly disclaims therapy, does not diagnose or prescribe, and escalates emergencies to human clinicians.

#### Q: Why bypass generative AI completely during Level 3 Crisis?
Generative LLMs are non-deterministic and can hallucinate invalid helpline numbers or generate harmful, validating, or dismissive responses. Deterministic templates guarantee that 100% of crisis users receive verified, official emergency phone numbers instantly without latency or hallucinations.

#### Q: How does the system handle Indian slang and Hinglish?
The deterministic rules layer includes normalized patterns for common Hinglish idioms (*"khatam karna"*, *"marne ka dil kar raha hai"*, *"sab bekaar hai"*), while the hyperbole filter recognizes benign academic slang (*"assignment is killing me lol"*, *"dying to eat biryani"*).

#### Q: Can I run this completely offline without paying for APIs?
**Yes.** Set `LLM_PROVIDER=mock` for zero-cost offline testing, or install [Ollama](https://ollama.ai) and run `ollama run llama3.2:3b` with `LLM_PROVIDER=ollama`.

---

## 16. Contributing

Contributions are welcome! Please follow these steps:

1. Fork the Project repository.
2. Create your Feature Branch (`git checkout -b feature/SafetyEnhancement`).
3. Commit your changes (`git commit -m 'feat: Add Tamil language crisis patterns'`).
4. Ensure all tests pass (`pytest -q`).
5. Push to the Branch (`git push origin feature/SafetyEnhancement`).
6. Open a Pull Request.

---

## 17. Changelog

- **v2.0.0** (Current):
  - Complete senior-level UI/UX redesign inspired by Linear design systems.
  - Interactive suggested evaluation scenarios above the fold.
  - Integrated audit scorecard directly within the safety telemetry sidebar.
  - Streamlit Community Cloud one-click deployment integration.
- **v1.1.0**:
  - Validated held-out evaluation on 44 frozen dialogues (95.65% crisis safety recall).
  - Indian helpline verification on official Government of India portals.
- **v1.0.0**:
  - Initial implementation of the two-agent safety architecture (Phases 0–10).
  - Multi-turn state tracker with crisis latching and symptom escalation.

---

## 18. Roadmap

- [ ] **Voice Interface**: Audio streaming integration with Whisper STT and speech synthesis for accessibility.
- [ ] **Regional Language Expansion**: Native prompt and rule modules for Hindi, Telugu, Tamil, and Bengali.
- [ ] **On-Device Small Model Fine-Tuning**: Quantized 3B/7B LoRA fine-tuning for zero-network campus deployments.
- [ ] **Authenticated Counselor Dashboard**: Role-based portal for campus counselors to securely review anonymized triage logs.

---

## 19. Author

**Suresh**  
- **GitHub**: [@suresh4330](https://github.com/suresh4330)  
- **Project Repository**: [MannSahara](https://github.com/suresh4330/MannSahara)

---

## 20. License

Distributed under the **MIT License**. See `LICENSE` for more information. Developed for academic evaluation (CSE473 / Smart India Hackathon SIH25092).
