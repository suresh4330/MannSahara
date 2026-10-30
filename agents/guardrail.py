"""Deterministic output guardrail for generated replies.
Blocks diagnoses, medications, method details, false contact claims, therapist claims,
and dismissive minimizing language.
"""
import re

PATTERNS = {
    "diagnosis": (
        r"\byou\s+(have|probably\s+have|are\s+suffering\s+from)\s+(depression|bipolar|ptsd|ocd|adhd)\b|"
        r"\bi\s+diagnos|\byou(?:'re|\s+are)\s+(clinically\s+)?depressed\b"
    ),
    "medication": (
        r"\b\d+\s?(mg|ml)\b|"
        r"\b(sertraline|fluoxetine|escitalopram|alprazolam|clonazepam|diazepam)\b"
    ),
    "method_detail": (
        r"\b(lethal|fatal)\s+dose\b|"
        r"\bhow\s+many\s+(pills|tablets)\b"
    ),
    "false_contact_claim": (
        r"\bi(?:'ve|\s+have)?\s+(contacted|notified|alerted|called|informed)\b"
        r".{0,40}\b(counsel\w*|warden|police|ambulance|your\s+(parents|family))\b"
    ),
    "therapist_claim": (
        r"\bas\s+your\s+(therapist|counsel+or|doctor)\b|"
        r"\bi(?:'m|\s+am)\s+your\s+(therapist|counsel+or|doctor)\b"
    ),
    "minimizing": (
        r"\bjust\s+cheer\s+up\b|"
        r"\bit'?s\s+not\s+that\s+bad\b|"
        r"\byou'?ll\s+be\s+fine\b"
    ),
}

COMPILED = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}


class Guardrail:
    def check(self, draft: str, level: int):
        v = [k for k, rx in COMPILED.items() if rx.search(draft)]
        if not draft.strip():
            v.append("empty")
        if len(draft) > 1200:
            v.append("too_long")
        return (not v), v

