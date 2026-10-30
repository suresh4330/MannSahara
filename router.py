"""Router and full conversational safety Pipeline.
Guarantees Level 3 NEVER calls the Coping Agent LLM, provides deterministic crisis replies,
and applies output guardrails with safe fallback on Levels 0-2.
"""
from typing import List, Dict, Any, Optional
from config.templates import FALLBACK, REFERRAL, crisis_reply
from tools.notify_counselor_sim import notify_counselor_sim
from tools.coping_tools import choose_technique
from agents.schemas import TurnResult

ACTION = {0: "supportive_chat", 1: "coping", 2: "referral"}


class Pipeline:
    def __init__(self, gateway, coping, guardrail, resources: List[Dict[str, Any]]):
        self.gateway = gateway
        self.coping = coping
        self.guardrail = guardrail
        self.resources = resources
        self.reset()

    def reset(self):
        self.gateway.reset()
        self.history, self.turn = [], 0

    def handle(self, text: str) -> TurnResult:
        self.turn += 1
        g = self.gateway.assess(text)
        lvl = g.tracked_level

        if lvl >= 3:
            # HARD REQUIREMENT: No Coping Agent LLM call at Level 3
            res = TurnResult(
                reply=crisis_reply(g.third_person, self.resources),
                level=3,
                action="crisis_response",
                gateway=g,
                notice=notify_counselor_sim(3, g.signals, self.turn),
                guardrail_triggered=False,
                violations=[],
                reply_from_llm=False,
            )
        else:
            try:
                draft = self.coping.reply(text, lvl, self.history)
                ok, viol = self.guardrail.check(draft, lvl)
            except Exception:
                draft, ok, viol = "", False, ["coping_error"]

            body = draft if ok else FALLBACK[lvl]
            if lvl == 1:
                body += "\n\n" + choose_technique(g.signals, text)
            if lvl == 2:
                body += "\n\n" + REFERRAL.format(campus=self._campus())

            res = TurnResult(
                reply=body,
                level=lvl,
                action=ACTION[lvl],
                gateway=g,
                notice=None,
                guardrail_triggered=not ok,
                violations=viol,
                reply_from_llm=ok,
            )

        self.history += [("student", text), ("assistant", res.reply)]
        return res

    def _campus(self) -> str:
        c = next((r for r in self.resources if r.get("kind") == "campus"), None)
        return f"{c['name']}: {c['number']}" if c else ""


def build_pipeline(mode: str = "hybrid") -> Pipeline:
    from agents.llm_client import get_client
    from agents.safety_gateway import SafetyGateway
    from agents.coping_agent import CopingAgent
    from agents.guardrail import Guardrail
    from tools.resource_lookup import load_resources

    client = get_client()
    return Pipeline(
        gateway=SafetyGateway(client, mode=mode),
        coping=CopingAgent(client),
        guardrail=Guardrail(),
        resources=load_resources(),
    )

