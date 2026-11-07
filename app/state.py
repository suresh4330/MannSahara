from typing import TypedDict


class ChatState(TypedDict, total=False):
    # identity and memory (carried between turns by Chatbot)
    conversation_id: str
    turn: int
    user_message: str
    history: list
    risk_history: list
    safety_locked: bool
    awaiting_checkin: bool
    # risk assessment
    rule_level: int
    llm_level: int
    final_level: int
    risk_reasons: list
    classifier_failed: bool
    injection: bool
    third_person: bool
    # routing and output
    route: str
    reply: str
    escalated: bool
    escalation_ticket: dict
    validation_ok: bool
    violations: list
    retries: int
    retry_note: str
    used_fallback: bool
    next_step: str
    path: list

