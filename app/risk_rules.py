"""Layer 1 of risk assessment: deterministic rules (English + Hinglish).
Levels: 0 normal | 1 distress | 2 ambiguous / indirect | 3 crisis
Design: rules favour RECALL. When unsure, the level goes UP, never down.
"""
import re
from dataclasses import dataclass, field

NORMAL, DISTRESS, AMBIGUOUS, CRISIS = 0, 1, 2, 3


def normalize(text: str) -> str:
    t = text.lower()
    t = t.replace("\u2019", "'").replace("\u2018", "'")
    return re.sub(r"\s+", " ", t).strip()


# Harmless idioms are removed BEFORE matching, so "this exam is killing me" is not a crisis.
IDIOMS = [
    r"\b(exam|exams|assignment|assignments|workload|deadline|deadlines|placement|placements"
    r"|this|that|it|college|semester|project|lab|work)\s+(is|are|was|were)\s+"
    r"(killing|kill)\s+(me|us)\b",
    r"\bdying (of|from) (boredom|laughter|embarrassment|hunger|curiosity)\b",
    r"\b(die|dying|died)\s+of\s+embarrassment\b",
    r"\bdead tired\b",
    r"\bto die for\b",
    r"\bkill for (a|an|some)\b",
    r"\b(mom|dad|mum|mother|father|parents|teacher|professor|prof|hod|sir|madam)"
    r"[^.?!]{0,15}\b(is|will|would|gonna)\s+(kill|killed|killing)\b",
    r"\bkill(ed|ing)?\s+it\b",
    r"\bi'?m\s+(so\s+)?dead\b",
    r"\bi'?ll\s+die\b",
    r"\bgoing to die (laughing|of laughter|of embarrassment|of boredom)\b",
    r"\bkilled\s+it\b",
    r"\bi give up on (this|the|my) (assignment|project|exam|subject|code|course|deadline)\b",
    r"\bjaan nikal gayi\b",
    r"\bpaper dekhke\s+(hi\s+)?jaan\b",
]

# Crisis phrases. negatable=True means "I don't want to die" is NOT treated as crisis,
# but is downgraded to ambiguous (level 2)
CRISIS_PATTERNS = [
    ("suicide_intent",
     r"\b(i|i'm|im|i am)\s+(want|wanna|going|plan|planning|thinking|decided|ready)\s+"
     r"[^.?!]{0,20}\b(to die|kill myself|end it( all)?|take my own life)\b",
     False),
    ("want_to_die", r"\b(want to|wanna)\s+(die|be dead)\b", True),
    ("kill_myself", r"\bkill(ing)?\s+myself\b", False),
    ("end_life", r"\b(end|ending|take|taking)\s+(my|my own)\s+life\b", False),
    ("end_it_all", r"\bend(ing)?\s+it\s+all\b", False),
    ("thinking_of_ending",
     r"\b(thinking|thought|thoughts)\s+(of|about)\s+(ending|killing|hurting)\s+"
     r"(it all|my life|myself)\b",
     True),
    ("wish_dead", r"\bwish i (was|were) dead\b", True),
    ("want_dead", r"\bwant to be dead\b", True),
    ("dont_want_live", r"\bdon'?t want to (live|be alive|wake up)\b", True),
    ("no_reason_live", r"\bno reason to (live|go on|be alive)\b", False),
    ("better_off", r"\bbetter off (dead|without me)\b", False),
    ("never_wake_up",
     r"\b(wish|want|hope|hoping)\b[^\.\?\!]{0,35}\b(never\s+wake\s+up|never\s+waking\s+up)\b"
     r"|\b(never\s+wake\s+up)\b",
     False),
    ("self_harm_act",
     r"\b(hurt(ing)?|cut(ting)?|harm(ing)?|injur(ing|ed)?)\s+(myself|my\s+(wrists?|arms?|body))\b",
     False),
    ("suicidal_self",
     r"\b(i|i'm|im|i am|feel|feeling)\s+(suicidal|suicidal thoughts?)\b",
     False),
    ("goodbye_note",
     r"\b(wrote|written|writing)\s+(a |my )?(suicide|goodbye|last)\s+(note|letter|message)\b",
     False),
    ("giving_away", r"\bgiving away my (stuff|things|belongings)\b", False),
    ("last_message", r"\b(this is|it's)\s+(my\s+)?(last|final)\s+(message|goodbye)\b", False),
    ("method_dose",
     r"\b(how (many|much))\s+(pills?|tablets?|dose)\b"
     r"|\b(die|kill|lethal|overdose|dangerous|fatal)\s+(dose|amount|quantity)\b",
     False),
    ("method_request",
     r"\b(ways?|methods?)\s+(to\s+)?(die|kill myself|end my life|commit suicide)\b",
     False),
    ("painless_death", r"\bpainless(ly\s+)?(way|death|die|to die)\b", False),
    ("how_to_die",
     r"\bhow (to|do i|can i) (kill myself|commit suicide|end my life|die)\b",
     False),
    # Hinglish
    ("hi_mar_jaana",
     r"\bmar (jaana|jana)\s+(chahta|chahti|chahiye|hai)\b",
     False),
    ("hi_marna", r"\bmarna (chahta|chahti)\b", False),
    ("hi_jeene_ka_mann", r"\bjeene ka (mann|man)\s+(nahi|nahin)\b", False),
    ("hi_jeena_nahi", r"\bjeena (nahi|nahin)\s+(chahta|chahti)\b", False),
    ("hi_khud_ko", r"\bkhud ko (khatam|maar)\b", False),
    ("hi_zindagi_khatam", r"\bzindagi (khatam|end)\b", False),
    ("hi_suicide_karna", r"\bsuicide kar(na|ne|unga|ungi)\b", False),
    ("hi_jaan_de", r"\bjaan (de|dena)\s+(dun|du|dunga|dungi)\b", False),
    ("hi_main_na_rahun", r"\bmain na (rahu|rahun|rahoon|raha|rahi)\b", False),
    ("hi_jeene_mann_nahi", r"\bjeene ka mann nahi\b", False),
    ("hi_mujhe_suicide", r"\bmujhe suicide\b", False),
]

AMBIGUOUS_PATTERNS = [
    ("hopeless", r"\bhopeless(ness)?\b"),
    ("worthless", r"\bworthless\b"),
    ("pointless_life", r"\b(life|everything)\s+(is\s+)?(pointless|meaningless|worthless)\b"),
    ("no_point", r"\b(no point|what'?s the point)\b"),
    ("cant_go_on",
     r"\b(can'?t|cannot|cant)\s+go on\b"
     r"|\b(can'?t|cannot|cant)\s+take (it|this)\s+(anymore|any more)\b"),
    ("give_up_life", r"\bgive up on (life|everything|living)\b"),
    ("burden", r"\bbur(den|den)\b"),
    ("disappear", r"\b(disappear|vanish)\b"),
    ("nobody_notice", r"\bnobody (would|will) (notice|care|miss)\b"),
    ("tired_of_life", r"\btired of (everything|life|living|it all)\b"),
    ("not_want_here", r"\bdon'?t want to be here\b"),
    ("suicide_topic", r"\bsuicide\b"),
    ("self_harm_topic", r"\bself[- ]?harm\b"),
    ("better_if_gone",
     r"\b(better|easier)\s+(if\s+)?(i\s+)?(wasn't|weren't|was gone|were gone)\b"),
    ("not_worth_living", r"\bnot worth (it|living)\b"),
    ("how_people_hurt",
     r"\bhow (do|can|would) (people|someone|a person)(\s+\w+)?\s+(hurt|harm|kill) "
     r"(themselves|themself|himself|herself)\b"),
    ("hi_sab_khatam", r"\bsab khatam\b"),
    ("hi_bojh", r"\bbojh\b"),
    ("hi_thak_gaya", r"\bthak (gaya|gayi) (hoon|hun|hu)\b"),
]

THIRD_PERSON_PATTERN = (
    r"\b((my\s+)?(friend|roommate|room\s*mate|brother|sister|cousin|classmate|batchmate)"
    r"|someone\s+i\s+know)"
    r"[^.?!]{0,35}\b(suicid\w*|kill(ing)?\s+(him|her|them)\w*"
    r"|end(ing)?\s+(his|her|their)\s+own"
    r"|cut(ting)?\s+(him|her|them)\w*)\b"
)

DISTRESS_PATTERNS = [
    r"\b(stress(ed)?|depressed|crying|nervous|worried|pressure|burnt? ?out|exhausted)\b",
    r"\bcan'?t sleep\b",
    r"\b(tension|ghabrahat|akela|akeli)\b",
]

INJECTION_PATTERNS = [
    r"\bignore (all |your |the |previous |any )?(instructions|rules|guidelines|prompt)\b",
    r"\b(you are|you're)\s+(now\s+)?(a|an)\b",
    r"\bpretend (you are|you're|to be|you have no)\b",
    r"\bjailbreak\b",
    r"\bact as (a|an|my) (doctor|psychiatrist|therapist)\b",
    r"\bdeveloper mode\b",
    r"\bdo anything now\b",
    r"\b(disable|disabled|turn off|ignore) the (safety|filters?|guardrails?)\b",
    r"\bsafety (mode|rules|filters?) (disabled|off)\b",
    r"^system:",
]

NEGATION_BEFORE = re.compile(r"\b(don't|do not|dont|never|not)\s*$")
NEGATION_INSIDE = re.compile(r"\b(don't|do not|dont|never|not)\b")


@dataclass
class RuleResult:
    level: int = NORMAL
    reasons: list = field(default_factory=list)
    injection: bool = False
    third_person: bool = False


def _strip_idioms(text: str) -> str:
    for pat in IDIOMS:
        text = re.sub(pat, " ", text)
    return text


def screen(user_message: str) -> "RuleResult":
    """Run all rules on ONE message. Conversation-level logic lives in conversation_risk.py."""
    raw = normalize(user_message)
    text = _strip_idioms(raw)
    result = RuleResult()

    result.injection = any(re.search(p, raw) for p in INJECTION_PATTERNS)
    if result.injection:
        result.reasons.append("prompt_injection_attempt")

    # 1. Crisis patterns
    for entry in CRISIS_PATTERNS:
        name, pattern, negatable = entry
        for m in re.finditer(pattern, text):
            prefix = text[max(0, m.start() - 30):m.start()]
            negated = NEGATION_BEFORE.search(prefix)
            if negatable and negated:
                result.level = max(result.level, AMBIGUOUS)
                result.reasons.append(f"negated_crisis:{name}")
            else:
                result.level = CRISIS
                result.reasons.append(f"crisis:{name}")

    # 2. Third-person friend/roommate disclosure
    try:
        if re.search(THIRD_PERSON_PATTERN, text):
            result.third_person = True
            result.level = max(result.level, AMBIGUOUS)
            result.reasons.append("third_person_disclosure")
    except re.error:
        pass

    # 3. Ambiguous patterns
    for name, pattern in AMBIGUOUS_PATTERNS:
        if re.search(pattern, text):
            result.level = max(result.level, AMBIGUOUS)
            result.reasons.append(f"ambiguous:{name}")

    # 4. Distress patterns (only if not already flagged)
    if result.level < DISTRESS and any(re.search(p, text) for p in DISTRESS_PATTERNS):
        result.level = DISTRESS
        result.reasons.append("distress")

    return result
