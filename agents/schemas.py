from dataclasses import dataclass, field
from typing import Optional, List
from pydantic import BaseModel, Field


class LLMRisk(BaseModel):
    risk_level: int = Field(ge=0, le=3)
    signals: List[str] = []
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    third_person: bool = False


@dataclass
class GatewayResult:
    rules_score: int
    llm_score: Optional[int]  # None if LLM failed or was not used
    hybrid_score: int  # combine_scores(mode, rules, llm)
    tracked_level: int  # after multi-turn tracker
    signals: list = field(default_factory=list)
    third_person: bool = False
    injection_attempt: bool = False
    llm_error: Optional[str] = None  # exception class name only, never keys or text
    llm_backend: str = "unknown"


@dataclass
class TurnResult:
    reply: str
    level: int
    action: str  # supportive_chat | coping | referral | crisis_response
    gateway: GatewayResult
    notice: Optional[dict] = None  # simulated counselor notification (Level 3)
    guardrail_triggered: bool = False
    violations: list = field(default_factory=list)
    reply_from_llm: bool = False  # must be False at Level 3

