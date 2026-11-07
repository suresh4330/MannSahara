"""LangGraph workflow:
START -> assess -> (support | checkin | crisis -> escalate | safety_followup)
      -> validate -> (finalize | retry support/safety_followup)
"""
from langgraph.graph import END, START, StateGraph
from .nodes import make_nodes
from .state import ChatState


def build_graph(store=None, use_llm_classifier=True):
    nodes = make_nodes(store, use_llm_classifier)
    g = StateGraph(ChatState)

    for name, fn in nodes.items():
        g.add_node(name, fn)

    g.add_edge(START, "assess")

    g.add_conditional_edges(
        "assess",
        lambda s: s["route"],
        {
            "support": "support",
            "checkin": "checkin",
            "crisis": "crisis",
            "safety_followup": "safety_followup",
        },
    )

    g.add_edge("crisis", "escalate")
    g.add_edge("escalate", "validate")
    g.add_edge("support", "validate")
    g.add_edge("checkin", "validate")
    g.add_edge("safety_followup", "validate")

    g.add_conditional_edges(
        "validate",
        lambda s: s["next_step"],
        {
            "finalize": "finalize",
            "support": "support",
            "safety_followup": "safety_followup",
        },
    )

    g.add_edge("finalize", END)
    return g.compile()

