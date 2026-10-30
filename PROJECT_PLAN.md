# MannSahara Project Plan
Source spec: MannSahara_Implementation_Guide.pdf (primary). Date created: 2026-10-30

## Requirements (R1-R20 from the guide)
- R1: Two cooperating agents: Safety Gateway and Coping Agent - todo
- R2: Four risk levels 0 to 3 as defined in section 6 - todo
- R3: Hybrid scoring: rules layer plus LLM classifier, take the higher score - todo
- R4: Multi-turn risk tracker with crisis latch, reset per conversation - todo
- R5: Level 3 reply is pre-written; the Coping Agent LLM is never called at Level 3 - todo
- R6: Coping Agent never diagnoses, gives medication advice, shares methods, or claims to replace a therapist - todo
- R7: Output guardrail checks every generated reply and falls back to a safe template - todo
- R8: Helplines and campus contacts live in config with a verified flag - todo
- R9: Counselor notification is simulated and labeled as simulated everywhere - todo
- R10: Synthetic dataset: dev set >= 150 dialogues, held-out set >= 40 dialogues, covering 10 categories - todo
- R11: test_log.csv with the columns in section 9.1 - todo
- R12: Metrics: crisis recall, false-crisis rate, escalation latency, referral correctness, guardrail violations - todo
- R13: Ablation: rules-only vs LLM-only vs hybrid on the same data - todo
- R14: Streamlit demo with chat, live safety panel, disclaimer, Run test suite button, CSV download - todo
- R15: No secrets in code or git - doing
- R16: No real clinical or student data - todo
- R17: Automated tests with pytest - doing
- R18: README and report with honest claims and limitations - todo
- R19: PROJECT_PLAN.md and PROGRESS.md maintained - doing
- R20: No fabricated results - doing

## Decisions in force (D1-D10)
- D1: Passive suicidal ideation -> Level 3 (crisis path).
- D2: Third-person concern -> Level 3 with third-person variant if explicit; Level 2 if vague worry.
- D3: Method/lethality requests -> Level 3. Never provide method details.
- D4: Prompt injection -> Never lowers level; scored on remaining content; flagged injection_attempt.
- D5: Crisis latch -> Once Level 3 is reached, every subsequent turn stays Level 3 until reset.
- D6: LLM classifier failure -> Fall back to rules score, record llm_error, count in report.
- D7: LLM backend -> Real model for final results. Mock allowed for development/tests, labeled clearly.
- D8: Languages -> English and Hinglish (Roman script).
- D9: Hyperbole -> Words like "killing me" / "dying" ignored when in academic/idiom context; explicit crisis phrases never suppressed.
- D10: Held-out set -> Written and frozen before rule tuning, used once at the end.

## Environment
- OS: Windows
- Python: 3.14.2
- Packages: streamlit 1.61.1, pydantic 2.13.4, pandas 2.3.x, pytest 9.0.3, requests 2.34.2, python-dotenv 1.2.2
- Git state: Initializing repo for MannSahara
- LLM backend: Mock for unit tests / dev; hosted API or local provider to be configured for final run

## Phases
| Phase | Goal | Verification command | Status |
|-------|------|----------------------|--------|
| 0 | Setup | pytest -q | done |
| 1 | Config, fixed templates, simulated tools | pytest tests/test_resources.py | done |
| 2 | Synthetic dataset (dev + held-out) | pytest tests/test_dataset.py | done |
| 3 | Rules layer (English + Hinglish) | pytest tests/test_rules.py | done |
| 4 | LLM client and classifier | pytest tests/test_classifier.py | done |
| 5 | Tracker and Safety Gateway | pytest tests/test_tracker.py tests/test_hybrid.py | done |
| 6 | Coping Agent and output guardrail | pytest tests/test_guardrail.py | done |
| 7 | Router and pipeline | pytest tests/test_router.py | done |
| 8 | Evaluation harness, test_log.csv, metrics, ablation | python -m evaluation.run_eval --split dev | done |
| 9 | Streamlit demo | App starts; manual walkthrough logged | done |
| 10 | Held-out run, README, report, final checklist | Section 11 checklist fully ticked | todo |

## Risks and open questions
- Ollama is not installed locally in PATH. For real LLM runs in Phase 4+, an API key (e.g. Gemini / Anthropic / OpenAI) or Ollama setup will be confirmed with the user.

