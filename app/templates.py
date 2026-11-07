"""Pre-approved replies. Crisis and check-in replies are NEVER free-form LLM output."""
from .resources import format_resources

AI_NOTICE = (
    "MannSahara is an AI support prototype. It is not a counsellor, doctor or "
    "emergency service, and it cannot diagnose or treat anything."
)


def crisis_reply():
    return (
        "I'm really glad you told me, and I'm sorry you are carrying this. What you are "
        "feeling matters, and you deserve support from a real person right now. I'm an AI, "
        "so I can't give emergency help myself.\n\n"
        "If you might act on these thoughts, or you are in immediate danger, please call 112 "
        "now or go to the nearest hospital, and try not to be alone.\n\n"
        "You can also talk to a trained person right away:\n"
        f"{format_resources()}\n\n"
        "Is there someone you trust (a friend, family member, hostel warden or counsellor) "
        "who you can contact right now? I'm here and happy to keep talking while you reach out."
    )


def checkin_reply(third_person: bool = False):
    if third_person:
        return (
            "Thank you for telling me. It sounds like you are worried about someone you care "
            "about, and that is a lot to carry. If they are in immediate danger, please call "
            "112 or stay with them and get help from a trusted adult or counsellor.\n\n"
            "These services can also guide you on how to support them:\n"
            f"{format_resources()}\n\n"
            "How are you holding up yourself right now?"
        )
    return (
        "Thank you for sharing that with me. It sounds really heavy, and I want to make sure "
        "I understand. Are you having thoughts of harming yourself or ending your life?\n\n"
        "Whatever your answer is, you don't have to handle this alone. If you would like to "
        "talk to someone, here are some options:\n"
        f"{format_resources()}"
    )


def fallback_reply():
    return (
        "I want to be careful with my words here. I'm an AI and not a counsellor, so I may "
        "not be the best support for this. If you would like to talk to a person, these "
        "services can help:\n"
        f"{format_resources()}\n\n"
        "I'm still happy to listen if you want to tell me more."
    )

