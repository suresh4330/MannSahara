"""Pre-written evidence-based coping techniques for Level 1 support.
These texts are deterministic and pre-screened against the output guardrail.
"""

TECHNIQUES = {
    "grounding_54321": (
        "Grounding exercise (5-4-3-2-1):\n"
        "- Name 5 things you can see around you.\n"
        "- Name 4 things you can physically feel (like your desk or your shoes).\n"
        "- Name 3 distinct sounds you can hear right now.\n"
        "- Name 2 things you can smell (or two scents you like).\n"
        "- Name 1 positive thing about yourself or your effort today."
    ),
    "box_breathing": (
        "Box breathing exercise:\n"
        "1. Inhale slowly through your nose for 4 seconds.\n"
        "2. Hold your breath gently for 4 seconds.\n"
        "3. Exhale smoothly through your mouth for 4 seconds.\n"
        "4. Rest and hold empty for 4 seconds.\n"
        "Try repeating this cycle 3 or 4 times to help settle your nervous system."
    ),
    "study_break_plan": (
        "Structured study-break strategy:\n"
        "- Step away from your books and screen for 10-15 minutes.\n"
        "- Drink a glass of water and stretch your neck and shoulders.\n"
        "- Pick just one manageable sub-task to focus on when you return."
    ),
    "basic_sleep_routine": (
        "Gentle wind-down routine for sleep:\n"
        "- Put aside phones and study materials 30 minutes before bed.\n"
        "- Write down tomorrow's to-do items on a notebook to set them aside for tonight.\n"
        "- Lie down in a comfortable position and focus on letting your muscles release tension."
    ),
}


def choose_technique(signals=None, text=""):
    signals = signals or []
    signals_lower = [str(s).lower() for s in signals]
    text_lower = text.lower() if text else ""

    if any("sleep" in s for s in signals_lower) or "sleep" in text_lower or "neend" in text_lower or "insomnia" in text_lower:
        return TECHNIQUES["basic_sleep_routine"]
    if any("exam" in s or "study" in s for s in signals_lower) or any(w in text_lower for w in ["exam", "study", "assignment", "syllabus", "test", "quiz"]):
        return TECHNIQUES["study_break_plan"]
    if any("panic" in s for s in signals_lower) or any(w in text_lower for w in ["panic", "breathless", "dizzy", "racing heart"]):
        return TECHNIQUES["box_breathing"]
    if any("stress" in s or "overwhelm" in s for s in signals_lower) or "ground" in text_lower:
        return TECHNIQUES["grounding_54321"]

    return TECHNIQUES["box_breathing"]

