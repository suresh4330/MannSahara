"""MannSahara — Senior Developer / Clinical-Grade Safety & Wellbeing Dashboard.
Features:
- Dual-Agent Architecture (Safety Gateway + Coping Agent)
- Real-Time Live Triage Telemetry (Risk Gauge, Tri-Score Breakdown, Signals)
- Deterministic Output Guardrails & Multi-Turn Latch Tracking
- Beautiful, modern health-tech UI (Glassmorphic design, custom badges, quick prompts)
- Verified Emergency Hotlines & Simulated Counselor Dispatch Console
- Integrated Evaluation Runner & CSV Download
"""
import subprocess
import sys
import pathlib
import json
from datetime import datetime
import streamlit as st

from router import build_pipeline
from tools.resource_lookup import unverified

# Page Configuration
st.set_page_config(
    page_title="MannSahara | Safety Triage & Wellbeing Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End CSS Styling
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre, .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Header Styling */
    .ms-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .ms-title-group {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .ms-logo {
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        color: white;
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        font-weight: 700;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
    }
    .ms-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
        background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .ms-subtitle {
        font-size: 13px;
        color: #94A3B8;
        margin: 0;
    }
    .ms-badges {
        display: flex;
        gap: 8px;
    }
    .ms-badge {
        font-size: 11px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 9999px;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    .badge-primary {
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-warning {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    /* Disclaimer Card */
    .disclaimer-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-left: 4px solid #F59E0B;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
        backdrop-filter: blur(8px);
    }
    .disclaimer-text {
        font-size: 12.5px;
        color: #E2E8F0;
        line-height: 1.4;
        margin: 0;
    }
    .disclaimer-text strong {
        color: #FBBF24;
    }

    /* Sidebar Telemetry Cards */
    .telemetry-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(8px);
    }
    .telemetry-header {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Risk Level Meter */
    .risk-meter {
        display: flex;
        gap: 6px;
        margin-top: 8px;
        margin-bottom: 12px;
    }
    .risk-seg {
        flex: 1;
        height: 6px;
        border-radius: 3px;
        background: rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    .risk-seg.active-0 { background: #10B981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.6); }
    .risk-seg.active-1 { background: #3B82F6; box-shadow: 0 0 8px rgba(59, 130, 246, 0.6); }
    .risk-seg.active-2 { background: #F59E0B; box-shadow: 0 0 8px rgba(245, 158, 11, 0.6); }
    .risk-seg.active-3 { background: #EF4444; box-shadow: 0 0 12px rgba(239, 68, 68, 0.8); }

    .risk-hero {
        display: flex;
        align-items: baseline;
        gap: 10px;
    }
    .risk-num {
        font-size: 32px;
        font-weight: 800;
        line-height: 1;
    }
    .risk-lbl {
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .risk-color-0 { color: #10B981; }
    .risk-color-1 { color: #3B82F6; }
    .risk-color-2 { color: #F59E0B; }
    .risk-color-3 { color: #EF4444; }

    /* Score Matrix */
    .score-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-top: 8px;
    }
    .score-box {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 8px;
        text-align: center;
    }
    .score-box-title {
        font-size: 10px;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
    }
    .score-box-val {
        font-size: 16px;
        font-weight: 700;
        margin-top: 2px;
    }

    /* Signals Pill Container */
    .signals-box {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-top: 6px;
    }
    .signal-pill {
        font-size: 10.5px;
        font-family: 'JetBrains Mono', monospace;
        padding: 3px 8px;
        border-radius: 6px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #CBD5E1;
    }

    /* Crisis Emergency Card in Main Chat */
    .crisis-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(153, 27, 27, 0.25) 100%);
        border: 1.5px solid #EF4444;
        border-radius: 12px;
        padding: 18px 20px;
        margin: 12px 0;
        box-shadow: 0 8px 24px rgba(239, 68, 68, 0.2);
    }
    .crisis-title {
        font-size: 16px;
        font-weight: 700;
        color: #FCA5A5;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }
    .hotline-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 10px;
        margin: 14px 0;
    }
    .hotline-btn {
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 8px;
        padding: 10px 14px;
        color: #FFFFFF;
        text-decoration: none;
        display: flex;
        flex-direction: column;
        transition: all 0.2s ease;
    }
    .hotline-btn:hover {
        background: rgba(239, 68, 68, 0.35);
        border-color: #EF4444;
        transform: translateY(-1px);
    }
    .hotline-name {
        font-size: 12px;
        color: #FECACA;
        font-weight: 500;
    }
    .hotline-num {
        font-size: 17px;
        font-weight: 700;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Quick Prompts Container */
    .prompt-chip-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin: 1rem 0;
    }
    .prompt-chip {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px 14px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .prompt-chip:hover {
        background: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.4);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
if "pipe" not in st.session_state:
    st.session_state.pipe = build_pipeline("hybrid")
    st.session_state.msgs = []
    st.session_state.last = None

pipe = st.session_state.pipe
last = st.session_state.last

# Level Metas
LEVEL_META = {
    0: {"name": "Normal Stress", "color": "0", "badge": "badge-success", "desc": "Supportive Chat • Routine Academic Guidance"},
    1: {"name": "Mild Distress", "color": "1", "badge": "badge-primary", "desc": "Supportive Reflection + Coping Technique"},
    2: {"name": "Moderate Distress", "color": "2", "badge": "badge-warning", "desc": "Referral Block + Campus Booking Protocol"},
    3: {"name": "Crisis Protocol", "color": "3", "badge": "badge-warning", "desc": "DETERMINISTIC CRISIS DISPATCH • Zero LLM Reply"}
}

# -------------------------------------------------------------
# SIDEBAR: LIVE SAFETY & TRIAGE TELEMETRY DASHBOARD
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <div style="font-size: 18px;">🛡️</div>
            <div style="font-size: 15px; font-weight: 700; letter-spacing: -0.01em;">Safety Gateway Telemetry</div>
        </div>
        <div style="font-size: 11px; color: #94A3B8; margin-bottom: 14px;">Real-Time Dual-Agent Risk Monitoring</div>
    """, unsafe_allow_html=True)

    # LLM Backend Status
    backend = getattr(pipe.gateway.client, "backend", "unknown")
    model_name = getattr(pipe.gateway.client, "model", "default")
    st.markdown(f"""
        <div class="telemetry-card" style="padding: 10px 14px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 11px; color: #94A3B8;">LLM Provider</span>
                <span class="ms-badge badge-primary" style="font-size: 10px;">{backend.upper()}</span>
            </div>
            <div style="font-size: 11px; color: #CBD5E1; font-family: 'JetBrains Mono', monospace; margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                {model_name}
            </div>
        </div>
    """, unsafe_allow_html=True)

    if backend == "mock":
        st.error("⚠️ MOCK LLM ACTIVE: Results are stubs for testing and not real AI outputs.")

    # Unverified Helpline Warning Check
    unver = unverified(pipe.resources)
    if unver:
        st.warning(f"⚠️ Unverified contacts detected: {', '.join(unver)}")

    # Current Level & Live Triage Status
    curr_lvl = last.level if last else 0
    curr_meta = LEVEL_META.get(curr_lvl, LEVEL_META[0])

    # Segments for visual meter
    seg_0 = "active-0" if curr_lvl >= 0 else ""
    seg_1 = "active-1" if curr_lvl >= 1 else ""
    seg_2 = "active-2" if curr_lvl >= 2 else ""
    seg_3 = "active-3" if curr_lvl >= 3 else ""

    st.markdown(f"""
        <div class="telemetry-card">
            <div class="telemetry-header">
                <span>Active Triage Level</span>
                <span class="ms-badge {curr_meta['badge']}">{curr_meta['name']}</span>
            </div>
            <div class="risk-hero">
                <div class="risk-num risk-color-{curr_meta['color']}">Level {curr_lvl}</div>
            </div>
            <div class="risk-meter">
                <div class="risk-seg {seg_0}"></div>
                <div class="risk-seg {seg_1}"></div>
                <div class="risk-seg {seg_2}"></div>
                <div class="risk-seg {seg_3}"></div>
            </div>
            <div style="font-size: 11.5px; color: #CBD5E1;">
                {curr_meta['desc']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Multi-Agent Tri-Score Matrix
    if last:
        g = last.gateway
        st.markdown(f"""
            <div class="telemetry-card">
                <div class="telemetry-header">
                    <span>Scoring Resolution</span>
                    <span style="font-size: 10px; color: #60A5FA;">max(Rules, LLM)</span>
                </div>
                <div class="score-grid">
                    <div class="score-box">
                        <div class="score-box-title">Rules</div>
                        <div class="score-box-val" style="color: #38BDF8;">{g.rules_score}</div>
                    </div>
                    <div class="score-box">
                        <div class="score-box-title">LLM</div>
                        <div class="score-box-val" style="color: #A78BFA;">{g.llm_score if g.llm_score is not None else 'N/A'}</div>
                    </div>
                    <div class="score-box">
                        <div class="score-box-title">Hybrid</div>
                        <div class="score-box-val risk-color-{curr_meta['color']}">{g.hybrid_score}</div>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <div style="font-size: 10.5px; font-weight: 600; color: #94A3B8; text-transform: uppercase;">Detected Signals</div>
                    <div class="signals-box">
                        {''.join(f'<span class="signal-pill">{s}</span>' for s in g.signals) if g.signals else '<span style="font-size: 11px; color: #64748B;">No adverse signals detected</span>'}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Defenses & Guardrails Telemetry
        st.markdown(f"""
            <div class="telemetry-card">
                <div class="telemetry-header">
                    <span>Active Safety Defenses</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 6px; font-size: 11.5px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #CBD5E1;">Prompt Injection Shield:</span>
                        <span style="color: {'#EF4444; font-weight: 700;' if g.injection_attempt else '#34D399;'}">
                            {'⚠️ DETECTED' if g.injection_attempt else '✓ CLEAN'}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #CBD5E1;">Output Guardrail:</span>
                        <span style="color: {'#EF4444; font-weight: 700;' if last.guardrail_triggered else '#34D399;'}">
                            {'⚠️ FALLBACK INTERCEPT' if last.guardrail_triggered else '✓ VERIFIED SAFE'}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #CBD5E1;">Multi-Turn Crisis Latch:</span>
                        <span style="color: {'#EF4444; font-weight: 700;' if pipe.gateway.tracker.latched else '#64748B;'}">
                            {'🔒 LATCHED (L3)' if pipe.gateway.tracker.latched else '○ UNLATCHED'}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #CBD5E1;">LLM Generator Bypassed:</span>
                        <span style="color: {'#34D399; font-weight: 700;' if not last.reply_from_llm else '#64748B;'}">
                            {'✓ YES (Rule Template)' if not last.reply_from_llm else '○ NO (Empathetic LLM)'}
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if g.llm_error:
            st.error(f"⚠️ Classifier Fallback Fired: {g.llm_error}")

        if last.notice:
            st.markdown("""
                <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 8px; padding: 10px; margin-bottom: 12px;">
                    <div style="font-size: 11px; font-weight: 700; color: #FCA5A5; text-transform: uppercase;">Simulated Handoff Active</div>
                    <div style="font-size: 11px; color: #FECACA; margin-top: 3px;">Demo alert payload dispatched (Signals only, no transcript).</div>
                </div>
            """, unsafe_allow_html=True)
            with st.expander("View Simulated Alert Payload", expanded=False):
                st.json(last.notice)

    # Actions: New Chat & Evaluation Tools
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Start New Conversation", use_container_width=True):
        pipe.reset()
        st.session_state.msgs = []
        st.session_state.last = None
        st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 14px 0;'>", unsafe_allow_html=True)
    st.markdown("<div class='telemetry-header'><span>Benchmark & Audit Suite</span></div>", unsafe_allow_html=True)

    if st.button("⚡ Run Dev Benchmark (156 cases)", use_container_width=True):
        with st.spinner("Executing full safety pipeline across 156 development dialogues..."):
            out = subprocess.run(
                [sys.executable, "-m", "evaluation.run_eval", "--split", "dev"],
                capture_output=True,
                text=True,
            )
        st.success("Benchmark completed!")
        st.code((out.stdout or out.stderr)[-2000:], language="bash")

    log_path = pathlib.Path("results/test_log.csv")
    if log_path.exists():
        st.download_button(
            label="📥 Download Audit Log (test_log.csv)",
            data=log_path.read_bytes(),
            file_name="mannsahara_test_log.csv",
            mime="text/csv",
            use_container_width=True
        )

# -------------------------------------------------------------
# MAIN CONTENT AREA
# -------------------------------------------------------------

# Top Brand Header
st.markdown("""
    <div class="ms-header">
        <div class="ms-title-group">
            <div class="ms-logo">M</div>
            <div>
                <h1 class="ms-title">MannSahara</h1>
                <p class="ms-subtitle">Autonomous Two-Agent Safety & Wellbeing Pipeline for Students • CSE473 / SIH25092</p>
            </div>
        </div>
        <div class="ms-badges">
            <span class="ms-badge badge-primary">Dual-Agent v2.0</span>
            <span class="ms-badge badge-success">Guardrails Active</span>
            <span class="ms-badge" style="background: rgba(148, 163, 184, 0.15); color: #CBD5E1; border: 1px solid rgba(148, 163, 184, 0.3);">Synthetic Protocol</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Prominent Ethical Disclaimer Card
st.markdown("""
    <div class="disclaimer-card">
        <div style="font-size: 20px;">ℹ️</div>
        <div class="disclaimer-text">
            <strong>Clinical & Research Safety Notice:</strong> MannSahara is an academic research prototype.
            It is <strong>not therapy</strong>, does <strong>not diagnose or treat</strong> medical conditions, and does not replace licensed psychological care.
            In severe or crisis situations, the pipeline autonomously bypasses LLM generation and connects you directly to official national crisis helplines.
        </div>
    </div>
""", unsafe_allow_html=True)

# Quick Sample Inquiries for Easy Testing if no messages yet
if not st.session_state.msgs:
    st.markdown("<div style='font-size: 13px; font-weight: 600; color: #94A3B8; margin-bottom: 8px;'>TRY A TEST SCENARIO:</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 Exam Stress (Level 0 - Normal)", use_container_width=True):
            st.session_state.preset_prompt = "Mid-sems start Monday and I can't focus on operating systems."
        if st.button("🌙 Insomnia & Low Energy (Level 1 - Mild)", use_container_width=True):
            st.session_state.preset_prompt = "I haven't been sleeping well lately and I feel low most of the days."
    with col2:
        if st.button("🌧️ Persistent Hopelessness (Level 2 - Moderate)", use_container_width=True):
            st.session_state.preset_prompt = "I've felt hopeless for weeks and I've stopped going to class."
        if st.button("🚨 Hyperbole Trap Disambiguation", use_container_width=True):
            st.session_state.preset_prompt = "This DBMS assignment is killing me lol, dying to go home!"

# Render Existing Conversation Messages
for m in st.session_state.msgs:
    role = m["role"]
    content = m["content"]
    level = m.get("level", 0)

    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"<div style='font-size: 14.5px;'>{content}</div>", unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar="🧠"):
            # If crisis response, render dedicated high-visibility crisis card
            if level == 3:
                st.markdown(f"""
                    <div class="crisis-card">
                        <div class="crisis-title">🚨 Immediate Crisis Support Activated</div>
                        <div style="font-size: 14px; color: #FEE2E2; line-height: 1.5; white-space: pre-wrap;">{content}</div>
                        <div class="hotline-grid">
                            <a class="hotline-btn" href="tel:14416">
                                <span class="hotline-name">Tele-MANAS (24/7 National)</span>
                                <span class="hotline-num">📞 14416</span>
                            </a>
                            <a class="hotline-btn" href="tel:18005990019">
                                <span class="hotline-name">KIRAN Mental Health</span>
                                <span class="hotline-num">📞 1800-599-0019</span>
                            </a>
                            <a class="hotline-btn" href="tel:112">
                                <span class="hotline-name">Emergency Response</span>
                                <span class="hotline-num">📞 112</span>
                            </a>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='font-size: 14.5px; line-height: 1.6;'>{content}</div>", unsafe_allow_html=True)

# Prompt Input Handling (From Text Box or Preset Buttons)
prompt_to_send = None
if "preset_prompt" in st.session_state and st.session_state.preset_prompt:
    prompt_to_send = st.session_state.preset_prompt
    st.session_state.preset_prompt = None
elif user_input := st.chat_input("Share what's on your mind (English or Hinglish)..."):
    prompt_to_send = user_input

if prompt_to_send:
    # Append user turn
    st.session_state.msgs.append({"role": "user", "content": prompt_to_send})

    # Execute pipeline
    res = pipe.handle(prompt_to_send)
    st.session_state.msgs.append({
        "role": "assistant",
        "content": res.reply,
        "level": res.level
    })
    st.session_state.last = res
    st.rerun()
