# MannSahara: Two-Agent Safety Pipeline for Student Mental Health Support

> **Research Prototype Notice**: MannSahara is an academic research prototype (CSE473 / SIH25092) developed strictly on synthetic data. **It is NOT therapy, does not diagnose or treat mental health conditions, and does not replace professional clinical care.** In crisis scenarios, it refers out to official national helplines and campus support.

---

## 1. What MannSahara Is and Is Not
- **What it IS**: A multi-tiered safety triage architecture combining deterministic regex safety rules (English and Hinglish) with an LLM classifier, a multi-turn risk tracker with a crisis latch, and an empathetic Coping Agent with strict output guardrails.
- **What it is NOT**:
  - It is **not** a therapist, counselor, psychiatrist, or medical device.
  - It **cannot** diagnose conditions (e.g., depression, bipolar, PTSD).
  - It **cannot** prescribe medications or dosage recommendations.
  - It **never** replaces human emergency intervention or professional clinicians.

---

## 2. System Architecture & The Four Risk Levels

```
                     Student User Message
                              |
                              v
       +-----------------------------------------------+
       |            AGENT 1: SAFETY GATEWAY            |
       |  rules_score = regex layer (English + Hinglish)|
       |  llm_score   = LLM classifier -> JSON         |
       |  hybrid      = max(rules_score, llm_score)    |
       |  tracked_lvl = multi-turn tracker (hybrid)    |
       +-----------------------+-----------------------+
                               |
                               v
                     ROUTER (tracked level)
        +----------+----------+-----------+------------------+
        | Level 0  | Level 1  |  Level 2  |     Level 3      |
        |  Normal  |   Mild   |  Moderate |      Crisis      |
        |   chat   |  chat +  | support + |  FIXED crisis    |
        |          |  coping  |  referral |  reply + helplines|
        |          | technique|  + mock   |  + simulated     |
        |          |          |  booking  | counselor notice |
        +----+-----+----+-----+-----+-----+--------+---------+
             |          |           |              | (No LLM called)
             v          v           v              v
        +---------------------------------+  [Deterministic Crisis
        |      AGENT 2: COPING AGENT      |   Template with Tele-MANAS,
        | (Constrained LLM, Levels 0-2)   |   KIRAN, 112 & Campus Cell]
        +----------------+----------------+
                         |
                         v
        +---------------------------------+
        |         OUTPUT GUARDRAIL        |
        |  (Deterministic safety filter)  |
        | Unsafe -> Fixed Safe Fallback   |
        +----------------+----------------+
                         |
                         v
                 Final Safe Reply
```

### Risk Taxonomy
| Level | Meaning | Signals | System Action |
| :---: | :--- | :--- | :--- |
| **0** | **Normal Stress** | Exams, homework, homesickness, deadlines, idioms like *"this exam is killing me"* | Supportive chat with disclaimer. |
| **1** | **Mild Distress** | Poor sleep, low mood, feeling overwhelmed without impairment | Supportive reflection + 1 evidence-based coping technique (grounding, box breathing, sleep routine). |
| **2** | **Moderate Distress**| Weeks of hopelessness, academic withdrawal, skipped classes, panic attacks, or vague worry about peers | Supportive reflection + campus counseling referral block with mock booking. |
| **3** | **Crisis** | Any active or passive suicidal ideation (*"wish I wouldn't wake up"*), self-harm, coded goodbyes, method requests, or explicit third-person crisis | **Immediate deterministic crisis message** with verified national helplines (`14416`, `1800-599-0019`, `112`), simulated counselor notification. **Coping Agent LLM is NEVER called.** |

---

## 3. Setup, Configuration & Running

### Prerequisites
- Python 3.10+ (tested on Python 3.14.2)
- Git

### Installation
```bash
# Clone the repository
git clone <repo-url>
cd MannSahara

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration (.env)
Create a `.env` file in the project root (never commit real secrets; `.env` is git-ignored):
```bash
# Example .env configuration
LLM_PROVIDER=openrouter  # openrouter | ollama | anthropic | openai | gemini | mock
LLM_MODEL=meta-llama/llama-3.3-70b-instruct
OPENROUTER_API_KEY=your_key_here
```

### Running the Test Suite
```bash
# Run all automated tests
pytest -q

# Run specific module tests
pytest tests/test_rules.py -q
pytest tests/test_classifier.py -q
pytest tests/test_tracker.py tests/test_hybrid.py -q
pytest tests/test_guardrail.py -q
pytest tests/test_router.py -q
pytest tests/test_dataset.py -q
pytest tests/test_resources.py -q
pytest tests/test_eval.py -q
```

### Running the Evaluation Harness
```bash
# Run full pipeline on the 156 development dialogues
python -m evaluation.run_eval --split dev

# Run full pipeline on the 44 frozen held-out dialogues
python -m evaluation.run_eval --split heldout
```

### Launching the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`. The demo includes:
- Main conversational chat window.
- Live Safety Telemetry sidebar showing risk levels, hybrid scores, signals, and injection warnings.
- Expandable simulated counselor alert payload.
- "Run test suite" button and `test_log.csv` download.

---

## 4. Evaluation Results & Ablation Study

Evaluated on 200 synthetic dialogues (156 development set + 44 held-out set) using `meta-llama/llama-3.3-70b-instruct`:

| Metric | Development Split (N=156) | Held-Out Split (N=44) |
| :--- | :---: | :---: |
| **Crisis Safety Recall (Headline)** | **100.00%** (70/70) [95% CI: 94.8%-100.0%] | **95.65%** (22/23) [95% CI: 79.0%-99.2%] |
| **Crisis Strict Recall (TOL=1)** | **100.00%** (70/70) [95% CI: 94.8%-100.0%] | **95.65%** (22/23) [95% CI: 79.0%-99.2%] |
| **False-Crisis Rate** | **0.00%** (0/62) [95% CI: 0.0%-5.8%] | **0.00%** (0/14) [95% CI: 0.0%-21.5%] |
| **Hyperbole Trap False-Crisis Rate** | **0.00%** (0/15) | **0.00%** (0/4) |
| **Referral Correctness** | **96.81%** | **96.67%** |
| **Overall Level Accuracy** | **94.87%** | **95.45%** |
| **Final Reply Guardrail Violations**| **0** | **0** |

### Ablation Study Summary
- **Rules-only**: 91.4% crisis recall, 0.0% false-crisis rate. Highly reliable on explicit phrases and Hinglish, but misses subtle implicit coded goodbyes.
- **LLM-only**: 94.3% crisis recall, 0.0% false-crisis rate. Excellent semantic understanding, but subject to latency and transient network failures.
- **Hybrid Pipeline (`max(rules, llm)`)**: **100.0% crisis recall** on dev, **94.9% overall accuracy**. Catches both explicit patterns and subtle semantic distress.

---

## 5. Limitations & Ethics Statement

1. **Tested on Synthetic Data Only**: All dialogues were authored specifically for research validation. Results may not fully generalize to the diversity, slang, or nuances of real student speech.
2. **Language Scope**: Covers English and Romanized Hinglish. Other regional Indian languages and non-Roman scripts are out of scope.
3. **No Clinical Diagnosis or Treatment**: MannSahara is designed strictly to listen empathetically, suggest mild grounding techniques, and refer out to qualified human professionals.
4. **Simulated Notification**: The counselor handoff alert is a demonstration simulation (`SIMULATED`). In a real-world deployment, an institutionally approved, staffed escalation protocol would be required.
5. **Ethical Deployment Requirements**: Any future production deployment must undergo rigorous Institutional Ethics Review (IRB), maintain informed user consent, zero transcript retention without opt-in, strict student data encryption, and 24/7 human clinical oversight.

