"""Layer 3 of risk assessment: conversation-level memory (what makes the system stateful).
"""
import re
from . import config
from .risk_rules import AMBIGUOUS, CRISIS, normalize

AFFIRM = re.compile(
    r"^(yes|yeah|yep|yup|haan|ha|han|i do|i did|i am|i meant it|i mean it|i was serious"
    r"|serious|kind of|sort of|a little|maybe|i think so)\b"
)


def combine(current_level, risk_history, user_message, awaiting_checkin):
    """Return (final_level, reasons)."""
    level, reasons = current_level, []

    # a. Affirmation after a check-in escalates to crisis
    if awaiting_checkin and AFFIRM.match(normalize(user_message)):
        level = max(level, CRISIS)
        reasons.append("affirmed_after_checkin")

    # b. Two ambiguous signals within ACCUMULATION_WINDOW turns escalates to crisis
    window = risk_history[-(config.ACCUMULATION_WINDOW - 1):]
    if current_level >= AMBIGUOUS and any(x >= AMBIGUOUS for x in window):
        level = max(level, CRISIS)
        reasons.append("repeated_ambiguous_signals")

    return level, reasons

