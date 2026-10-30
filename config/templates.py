from tools.resource_lookup import contacts_block

DISCLAIMER = (
    "I'm MannSahara, an AI support tool. I'm not a therapist, I can't diagnose or "
    "treat, and I'm not a replacement for professional care."
)

CRISIS_SELF = (
    "I'm really sorry you're going through this, and I'm glad you told me. What you're feeling "
    "matters, and you don't have to carry it alone.\n\n"
    "I'm an AI tool, so I can't give the kind of help a person can right now. Please reach out "
    "to someone who can:\n{contacts}\n\n"
    "If you are in immediate danger or have already hurt yourself, call the emergency number "
    "now or go to the nearest hospital.\n\n"
    "Please also tell someone near you right now (a friend, roommate, warden or family member) "
    "and ask them to stay with you.\n\n"
    "Demo note: the counselor alert shown beside this chat is SIMULATED. No real person has "
    "been contacted."
)

CRISIS_THIRD = (
    "Thank you for telling me. It's caring of you to look out for them, and taking this "
    "seriously is the right call.\n\n"
    "If they may be in danger right now, stay with them if you can and call the emergency "
    "number. These services can also advise you on how to help:\n{contacts}\n\n"
    "Please tell a warden, counselor or another trusted adult today, and look after yourself "
    "too. Demo note: any counselor alert here is SIMULATED; no real person has been contacted."
)

REFERRAL = (
    "It could really help to talk with a trained counselor. {campus}\n"
    "I can set up a demo appointment request (simulated: no real booking is made)."
)

FALLBACK = {
    0: "That sounds like a lot. Would you like to tell me more about what has been going on?",
    1: "That sounds really tiring. I'm here to listen, and a small break or a few slow breaths "
    "can sometimes take the edge off.",
    2: "I'm sorry it has felt this heavy for so long. You deserve proper support, and a "
    "counselor is the right person to help with this.",
}


def crisis_reply(third_person, resources):
    t = CRISIS_THIRD if third_person else CRISIS_SELF
    return t.format(contacts=contacts_block(resources))
