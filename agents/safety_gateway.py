"""Safety Gateway combining rules and LLM scoring, running multi-turn tracker,
and returning structured GatewayResult.
"""
from typing import Optional
from agents import rules
from agents.classifier import classify
from agents.schemas import GatewayResult
from agents.tracker import RiskTracker


def combine_scores(mode: str, rules_score: int, llm_score: Optional[int]) -> int:
    """The ONLY place scores are combined. Eval and ablation import this same function."""
    if mode == "rules":
        return rules_score
    if mode == "llm":
        return llm_score if llm_score is not None else rules_score  # D6 fallback
    if mode == "hybrid":
        return max(rules_score, llm_score if llm_score is not None else 0)
    raise ValueError(f"Unknown mode: {mode}")


class SafetyGateway:
    def __init__(self, client, mode: str = "hybrid", tracker: Optional[RiskTracker] = None):
        self.client = client
        self.mode = mode
        self.tracker = tracker or RiskTracker()
        self.context = []

    def reset(self):
        self.tracker.reset()
        self.context = []

    def assess(self, text: str) -> GatewayResult:
        r_score, signals, injection = rules.score_rules(text)
        l_score, err, third = None, None, "third_person" in signals

        try:
            out = classify(self.client, text, self.context)
            l_score = out.risk_level
            third = third or out.third_person
            signals = signals + [f"llm:{s}" for s in out.signals]
        except Exception as e:
            err = type(e).__name__  # class name only: never print or expose keys or text

        hybrid = combine_scores(self.mode, r_score, l_score)
        tracked = self.tracker.update(hybrid)
        self.context.append(text)

        return GatewayResult(
            rules_score=r_score,
            llm_score=l_score,
            hybrid_score=hybrid,
            tracked_level=tracked,
            signals=signals,
            third_person=third,
            injection_attempt=injection,
            llm_error=err,
            llm_backend=getattr(self.client, "backend", "unknown"),
        )

