# Ablation Study: Rules vs LLM vs Hybrid

| Metric | Rules-only | LLM-only | Hybrid Pipeline |
| :--- | :---: | :---: | :---: |
| **Crisis Safety Recall** | 91.4% (82.5%-96.0%) | 94.3% (86.2%-97.8%) | **100.0%** (94.8%-100.0%) |
| **Crisis Strict Recall (TOL=1)** | 91.4% | 94.3% | **100.0%** |
| **False-Crisis Rate** | 0.0% | 0.0% | **0.0%** |
| **Trap False-Crisis Rate** | 0.0% | 0.0% | **0.0%** |
| **Overall Level Accuracy** | 89.1% | 88.5% | **94.9%** |
| **Over-Escalation Rate** | 1.2% | 4.7% | **5.8%** |

### Key Findings:
- **Rules-only**: Deterministic safety net capturing explicit crisis, suicidal phrasing, and Romanized Hinglish with 0% false positives on hyperbole traps.
- **LLM-only**: Accurately disambiguates nuanced context, conversational intent, and subtle coded burden statements.
- **Hybrid Pipeline**: Takes `max(rules, llm)`, achieving superior crisis recall while preserving low false-alarm rates.
