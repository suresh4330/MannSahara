"""Chatbot = the compiled graph + per-conversation memory."""
import uuid
from . import config
from .graph import build_graph


class Chatbot:
    def __init__(self, conversation_id=None, store=None, use_llm_classifier=None):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.store = store
        if use_llm_classifier is None:
            use_llm_classifier = config.USE_LLM_CLASSIFIER
        self.graph = build_graph(store, use_llm_classifier)
        self.history = []          # [{"role": "user"|"assistant", "content": str}]
        self.risk_history = []     # final risk level of every previous turn
        self.safety_locked = False  # sticky: once a crisis is flagged it stays flagged
        self.awaiting_checkin = False
        self.turn = 0

    def send(self, user_message: str):
        self.turn += 1
        out = self.graph.invoke({
            "conversation_id": self.conversation_id,
            "turn": self.turn,
            "user_message": user_message,
            "history": list(self.history),
            "risk_history": list(self.risk_history),
            "safety_locked": self.safety_locked,
            "awaiting_checkin": self.awaiting_checkin,
            "escalated": False, "escalation_ticket": {}, "violations": [],
            "retries": 0, "retry_note": "", "used_fallback": False, "path": [],
        })
        self.history += [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": out["reply"]},
        ]
        self.risk_history.append(out["final_level"])
        if out["final_level"] >= 3:
            self.safety_locked = True
        self.awaiting_checkin = out["route"] == "checkin"
        if self.store is not None:
            self.store.log_turn(out)
        return out

