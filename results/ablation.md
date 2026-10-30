# Ablation Study: Rules vs LLM vs Hybrid

| Metric | Rules-only | LLM-only | Hybrid Pipeline |
| :--- | :---: | :---: | :---: |
| **Crisis Safety Recall** | 91.4% (82.5%-96.0%) | 95.7% (88.1%-98.5%) | **100.0%** (94.8%-100.0%) |
| **Crisis Strict Recall (TOL=1)** | 91.4% | 95.7% | **100.0%** |
| **False-Crisis Rate** | 0.0% | 0.0% | **0.0%** |
| **Trap False-Crisis Rate** | 0.0% | 0.0% | **0.0%** |
| **Overall Level Accuracy** | 89.1% | 90.4% | **95.5%** |
| **Over-Escalation Rate** | 1.2% | 3.5% | **4.7%** |

### Key Findings:
- **Rules-only**: Deterministic safety net capturing explicit crisis, suicidal phrasing, and Romanized Hinglish with 0% false positives on hyperbole traps.
- **LLM-only**: Accurately disambiguates nuanced context, conversational intent, and subtle coded burden statements.
- **Hybrid Pipeline**: Takes `max(rules, llm)`, achieving superior crisis recall while preserving low false-alarm rates.
