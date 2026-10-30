"""Streamlit interactive demo application for MannSahara.
Includes chat interface, live safety telemetry panel, simulated counselor alerts,
and test suite execution / CSV download per Section 10 of the guide.
"""
import subprocess
import sys
import pathlib
import streamlit as st

from router import build_pipeline
from tools.resource_lookup import unverified

st.set_page_config(page_title="MannSahara (research prototype)", layout="wide")
st.title("MannSahara")
st.warning(
    "AI support tool, not therapy. Cannot diagnose or treat. Research prototype, "
    "tested on synthetic data only."
)

if "pipe" not in st.session_state:
    st.session_state.pipe = build_pipeline()
    st.session_state.msgs = []
    st.session_state.last = None

pipe, last = st.session_state.pipe, st.session_state.last

with st.sidebar:
    st.header("Safety panel")
    backend = getattr(pipe.gateway.client, "backend", "unknown")
    st.caption(f"LLM backend: {backend}")
    if backend == "mock":
        st.error("MOCK LLM: not a real model. Results are not LLM results.")

    unver = unverified(pipe.resources)
    if unver:
        st.warning("Unverified contacts: " + ", ".join(unver))

    if last:
        st.metric("Risk level", last.level)
        st.write("Action:", last.action)
        g = last.gateway
        st.write(f"Rules {g.rules_score} | LLM {g.llm_score} | Hybrid {g.hybrid_score}")
        st.write("Signals:", g.signals if g.signals else "none")
        if g.injection_attempt:
            st.warning("Prompt injection flag set")
        if last.guardrail_triggered:
            st.warning(f"Guardrail triggered: {', '.join(last.violations)}")
        if g.llm_error:
            st.warning(f"Classifier error: {g.llm_error}")
        if last.notice:
            with st.expander("SIMULATED counselor notification", expanded=True):
                st.json(last.notice)

    if st.button("New conversation", use_container_width=True):
        pipe.reset()
        st.session_state.msgs = []
        st.session_state.last = None
        st.rerun()

    st.divider()
    st.caption("Runs the dev set. Makes many model calls.")
    if st.button("Run test suite", use_container_width=True):
        with st.spinner("Executing evaluation across dev dialogues..."):
            out = subprocess.run(
                [sys.executable, "-m", "evaluation.run_eval", "--split", "dev"],
                capture_output=True,
                text=True,
            )
        st.code((out.stdout or out.stderr)[-3000:])

    log = pathlib.Path("results/test_log.csv")
    if log.exists():
        st.download_button(
            "Download test_log.csv",
            log.read_bytes(),
            "test_log.csv",
            "text/csv",
            use_container_width=True,
        )

# Render conversation history
for m in st.session_state.msgs:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# User chat input
if text := st.chat_input("Type a message"):
    st.session_state.msgs.append({"role": "user", "content": text})
    res = pipe.handle(text)
    st.session_state.msgs.append({"role": "assistant", "content": res.reply})
    st.session_state.last = res
    st.rerun()

