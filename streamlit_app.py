"""MannSahara demo UI.  Run:  streamlit run streamlit_app.py"""
import json

import pandas as pd
import streamlit as st

from app import config
from app.chatbot import Chatbot
from app.db import Store
from app.templates import AI_NOTICE

st.set_page_config(page_title="MannSahara", layout="centered")


@st.cache_resource
def get_store():
    return Store()


def new_bot():
    return Chatbot(store=get_store())


if "bot" not in st.session_state:
    st.session_state.bot = new_bot()
    st.session_state.messages = []

tab_chat, tab_results = st.tabs(["Chat", "Test results"])

with st.sidebar:
    st.header("MannSahara")
    st.info(AI_NOTICE)
    st.warning(
        "Prototype for SIH25092. Use ONLY fictional, synthetic messages. "
        "Do not type real personal information."
    )
    consent = st.checkbox(
        "I understand this is a prototype and I will not enter real personal information."
    )
    show_debug = st.toggle("Show safety debug panel", value=True)
    st.caption(
        f"LLM provider: {config.LLM_PROVIDER} | LLM classifier: "
        f"{'on' if config.USE_LLM_CLASSIFIER else 'off'}"
    )
    if config.LLM_PROVIDER == "mock":
        st.caption("Mock mode: replies are canned and only the rule layer detects risk.")
    if st.button("Start new conversation"):
        st.session_state.bot = new_bot()
        st.session_state.messages = []
        st.rerun()

with tab_chat:
    st.title("MannSahara - Student Support")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            meta = m.get("meta")
            if meta and meta.get("escalated"):
                st.error(
                    "⚠️ SIMULATED ESCALATION: in a real deployment a counsellor would be "
                    "notified here. No one has actually been contacted."
                )
            if meta and show_debug:
                with st.expander("Safety debug"):
                    st.json(meta)

    if not consent:
        st.caption("Tick the consent box in the sidebar to start chatting.")
    else:
        prompt = st.chat_input("Type a (fictional) message...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            out = st.session_state.bot.send(prompt)
            meta = {
                k: out.get(k)
                for k in [
                    "rule_level", "llm_level", "final_level", "route", "path",
                    "risk_reasons", "escalated", "escalation_ticket",
                    "validation_ok", "violations", "retries",
                    "used_fallback", "classifier_failed",
                ]
            }
            st.session_state.messages.append(
                {"role": "assistant", "content": out["reply"], "meta": meta}
            )
            st.rerun()

with tab_results:
    st.title("Evaluation results")
    st.caption("Create these files first with:  python evaluate.py --split all --mode rules")

    files = sorted(config.LOG_DIR.glob("metrics_*.json"))
    if not files:
        st.info("No results yet. Run evaluate.py from the terminal.")
    else:
        pick = st.selectbox(
            "Result set",
            [f.stem.replace("metrics_", "") for f in files],
        )
        m = json.load(open(config.LOG_DIR / f"metrics_{pick}.json", encoding="utf-8"))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Test cases", m["total_cases"])
        c2.metric("Crisis recall", m["crisis_recall"])
        c3.metric("False-positive rate", m["false_positive_rate"])
        c4.metric("Crisis precision", m["crisis_precision"])

        st.write(
            f"TP={m['TP']}  FN={m['FN']}  FP={m['FP']}  TN={m['TN']}  |  "
            f"unsafe final replies={m['unsafe_final_replies']}"
        )

        st.subheader("Confusion matrix (rows = expected, columns = actual)")
        st.dataframe(pd.DataFrame(m["confusion_matrix_rows_expected_cols_actual"]))

        st.subheader("Pass rate by category")
        pc = pd.DataFrame(m["per_category"]).T
        st.bar_chart(pc["pass_rate"])

        log_path = config.LOG_DIR / f"test_log_{pick}.csv"
        if log_path.exists():
            log = pd.read_csv(log_path)
            st.subheader("Failed cases")
            st.dataframe(
                log[~log["pass"]][
                    ["id", "category", "input", "expected_action", "actual_action"]
                ]
            )
            st.subheader("Full test log")
            st.dataframe(log)

