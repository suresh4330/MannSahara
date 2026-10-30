"""Deterministic regex-based safety rules layer for English and Hinglish.
Covers risk levels 0-3, hyperbole disambiguation, third-person identification,
and prompt injection tagging.
"""
import re
import unicodedata

def normalize(t: str) -> str:
    """Normalize unicode, apostrophes, lowercase, and collapse whitespace."""
    t = unicodedata.normalize("NFKC", t).replace("\u2019", "'").casefold()
    return re.sub(r"\s+", " ", t).strip()

# Explicit Level 3 crisis phrases (active, passive, coded, methods, and Hinglish)
L3_EXPLICIT = {
    "suicide_word": r"\bsuicid(e|al)\b",
    "end_life": r"\b(kill|killing|killed|end)\s+(myself|my\s+life|their\s+life|his\s+life|her\s+life|himself|herself)\b",
    "want_to_die": r"\bwants?\s+to\s+die\b|\bwant\s+to\s+(jump\s+and\s+)?end\s+it\b",
    "dont_want_live": (
        r"\b(don'?t|do\s+not|doesn'?t|does\s+not)\s+want\s+to\s+"
        r"(live|be\s+alive|be\s+here\s+anymore|wake\s+up)\b"
    ),
    "no_reason_live": r"\bno\s+reason\s+to\s+(live|go\s+on)\b",
    "self_harm": (
        r"\b(hurt|hurting|harm|harming|cut|cutting)\s+(myself|herself|himself|themselves)\b|"
        r"\bself[- ]?harm\b|\bcutting\s+my\s+wrists\b|\bcuts\s+on\s+.*arm\b"
    ),
    "burden_goodbye": (
        r"\bbetter\s+off\s+without\s+me\b|\bwon'?t\s+be\s+a\s+burden\b|\bmy\s+last\s+message\b|"
        r"\bthis\s+is\s+goodbye\b|\bfinal\s+goodbye\b|\bgoodbye\s+forever\b|\bgiving\s+away\s+all\s+my\b|"
        r"\bno\s+one\s+will\s+miss\s+me\b|\bwriting\s+my\s+last\s+notes\b"
    ),
    "passive": (
        r"\b(wish|praying)\s+(that\s+)?(i\s+)?(could\s+)?(just\s+|simply\s+)?"
        r"(disappear|wouldn'?t\s+wake\s+up|fade\s+away)\b|"
        r"\b(stop\s+existing|vanish\s+into\s+nothing)\b|\bwish\s+i\s+(was|were)\s+never\s+born\b|"
        r"\brelief\s+(if\s+i\s+died|to\s+die)\b"
    ),
    "method_request": (
        r"\b(painless|easiest|quickest)\s+way\s+to\s+(die|end\s+it|end\s+life)\b|"
        r"\bhow\s+many\s+.*pills\s+are\s+fatal\b"
    ),
    "hi_jeene": r"\bjeene\s+ka\s+(mann|man|mood)\s+nahi\b|\bkaash\s+.*na\s+uthu\b",
    "hi_marna": r"\b(marna|mar\s+jana|mar\s+jaana)\s+chah(ta|ti)\b|\bkhudkushi\b",
    "hi_khatam": r"\bzindagi\s+(khatam|se\s+thak)\b|\bkhud\s+ko\s+khatam\b",
}

# Ambiguous words: Level 2 unless academic/idiom context is present (Decision D9)
AMBIGUOUS = {
    "killing_me": r"\bkill(ing)?\s+me\b",
    "dying": r"\bdying\b",
    "dead": r"\bdead\b",
}

# Context phrases indicating non-crisis colloquial hyperbole
HYPERBOLE_CTX = (
    r"\b(exams?|assignment|deadline|viva|lab|project|placement|homework|syllabus|"
    r"class|submission|quiz|lol|haha|joke|movie|comedy|vacation|diwali|food|wifi|"
    r"interview|marathon|laptop|battery|tired|curiosity|slowly)\b|"
    r"\bdying\s+to\b|\bdead\s+tired\b|\bto\s+die\s+for\b"
)

# Level 2 distress patterns: prolonged hopelessness, inability to cope, severe withdrawal
L2 = {
    "hopeless": r"\bhopeless\b",
    "cant_cope": r"\bcan'?t\s+cope\b",
    "withdrawal": (
        r"\b(stopped|stop)\s+(going\s+to\s+(class|college)|talking)\b|"
        r"\bshut\s+myself\s+off\b"
    ),
    "panic": r"\bpanic\s+attacks?\b",
    "hi_akela": r"\bbahut\s+akela\b",
    "hi_withdrawal": r"\bcollege\s+jana\s+band\b",
}

# Level 1 distress patterns: poor sleep, low mood, routine tension/overwhelm
L1 = {
    "sleep": r"\b(can'?t|cannot)\s+sleep\b|\bneend\s+nahi\b|\btossing\s+and\s+turning\b",
    "low": r"\bfeel(ing)?\s+(low|down)\b|\blow\s+feel\b",
    "stress": r"\b(stress(ed)?|anxious|overwhelmed|tension)\b",
}

# Prompt injection attempts (Decision D4: never lowers risk level)
INJECTION = (
    r"\b(ignore|forget|disregard)\b.{0,30}\b(rules|instructions|guidelines|safety)\b|"
    r"\byou\s+are\s+now\b|\bpretend\s+(you|to\s+be)\b|\bdeveloper\s+mode\b"
)

# Third-person concern indicators (Decision D2)
THIRD_SUBJECT = (
    r"\b(my\s+)?(friend|roommate|hostel\s?mate|batchmate|classmate|brother|sister|cousin)\b|"
    r"\b(he|she|they)\s+(said|told|wants?|sent|texted)\b"
)

# First-person pronouns and indicators to distinguish from third-person
FIRST_PERSON = r"\b(i\s+(want|wish|feel|am|'m|have|was|will)|myself|mujhe|mera|maine)\b"


def score_rules(text: str):
    """Scores a single message using regex rules.

    Returns:
        level (int): 0-3
        signals (list[str]): list of triggered rule names
        injection (bool): whether prompt injection was detected
    """
    t = normalize(text)
    level, signals = 0, []

    def scan(table, lvl, suffix=""):
        nonlocal level
        for name, pat in table.items():
            if re.search(pat, t):
                signals.append(name + suffix)
                level = max(level, lvl)

    # 1. Check explicit Level 3 crisis first
    scan(L3_EXPLICIT, 3)

    # 2. Check ambiguous words only if not filtered out by hyperbole context
    if not re.search(HYPERBOLE_CTX, t):
        scan(AMBIGUOUS, 2, "_ambiguous")

    # 3. Check Level 2 and Level 1 patterns
    scan(L2, 2)
    scan(L1, 1)

    # 4. Check prompt injection
    injection = bool(re.search(INJECTION, t))

    # 5. Check third-person concern
    if level >= 3 and re.search(THIRD_SUBJECT, t) and not re.search(FIRST_PERSON, t):
        signals.append("third_person")

    return level, signals, injection
