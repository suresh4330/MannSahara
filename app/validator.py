"""Output guardrail: rejects unsafe LLM replies before the student sees them."""
import re

BANNED = [
    ("foreign_helplines",
     r"\b(988|741741|national suicide prevention lifeline|suicide & crisis lifeline|in the united states|u\.s\., canada|puerto rico)\b"),
    ("diagnosis",
     r"\byou (have|are suffering from|likely have|probably have|may have)\s+"
     r"(depression|an anxiety disorder|anxiety disorder|bipolar|ptsd|adhd|ocd|a disorder)\b"),
    ("medication_advice",
     r"\b(take|try|start|stop|increase|double)\s+"
     r"(some\s+)?(medication|medicine|antidepressants?|sertraline|fluoxetine|alprazolam|xanax"
     r"|sleeping pills?|tablets?|mg)\b"
     r"|\b(take|try|start|stop|increase|double)\s+\w+\s+"
     r"(medication|medicine|antidepressants?|sertraline|fluoxetine|alprazolam|xanax"
     r"|sleeping pills?|tablets?)\b"),
    ("method_details",
     r"\b(lethal dose|overdose|hang(ing)?|jump(ing)? off|from a bridge|from a building"
     r"|painless way)\b"),
    ("claims_contact",
     r"\bi (have|'ve|had|already) (contacted|called|notified|alerted|informed|messaged)\b"),
    ("will_contact",
     r"\bi (will|'ll|am going to) (contact|call|notify|alert|inform) "
     r"(your|a|the|someone|anyone|emergency|police|counsellor)\b"),
    ("false_promise",
     r"\b(i promise|i swear|i won't tell anyone|never tell anyone)\b"),
    ("dismissive",
     r"\b(just get over it|just relax|cheer up|it'?s not (that )?a big deal"
     r"|it'?s not serious|stop overthinking|you'?re overreacting)\b"),
    ("agrees_hopeless",
     r"\b(you'?re right|that'?s true|i agree)\b.{0,60}\b(hopeless|pointless|no way out|worthless)\b"),
    ("claims_human",
     r"\bi('m| am) a (human|real person|licensed|therapist|doctor|psychologist)\b"),
]

MAX_LEN = 1500


def validate(reply: str):
    """Return (ok, violations)."""
    violations = []
    text = (reply or "").strip()
    if not text:
        return False, ["empty_reply"]
    if len(text) > MAX_LEN:
        violations.append("too_long")
    if text.endswith(("(", "[", "{", ":", "—")):
        violations.append("truncated_reply")
    low = text.lower().replace("\u2019", "'")
    for name, pattern in BANNED:
        if re.search(pattern, low):
            violations.append(name)
    return (len(violations) == 0), violations
