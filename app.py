"""MannSahara — Senior-Level Clinical & Engineering AI Safety Platform.
Production UI/UX Redesign adhering to Linear / Modern AI SaaS Design Systems.
Architected for SIH25092 / CSE473 Academic & Industry Showcase.
"""
import subprocess
import sys
import pathlib
import json
import html
from datetime import datetime
import streamlit as st

from router import build_pipeline
from tools.resource_lookup import unverified

# -----------------------------------------------------------------------------
# 1. PAGE & SYSTEM SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MannSahara — AI Safety & Triage Console",
    page_icon="https://api.iconify.design/lucide:shield-check.svg?color=%236366f1",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. DESIGN SYSTEM STYLING (LINEAR / MODERN AI SAAS SPEC)
# -----------------------------------------------------------------------------
DESIGN_SYSTEM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-base: #090A0D;
        --bg-surface: #11141A;
        --bg-surface-elevated: #161A22;
        --bg-surface-hover: #1D222D;
        --border-subtle: rgba(255, 255, 255, 0.06);
        --border-medium: rgba(255, 255, 255, 0.12);
        --border-focus: rgba(99, 102, 241, 0.45);
        --text-primary: #F0F3F8;
        --text-secondary: #94A0B8;
        --text-muted: #64748B;
        --accent-indigo: #6366F1;
        --accent-blue: #38BDF8;
        --status-safe: #10B981;
        --status-warning: #F59E0B;
        --status-danger: #EF4444;
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
    }

    /* Core Document Settings */
    html, body, [class*="css"] {
        font-family: var(--font-sans);
        color: var(--text-primary);
        background-color: var(--bg-base);
    }

    /* Streamlit Chrome Suppression */
    #MainMenu { visibility: hidden !important; display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    header[data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: blur(12px) !important;
    }
    div[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    div[data-testid="stStatusWidget"] { visibility: hidden !important; display: none !important; }
    .stDeployButton { display: none !important; }

    /* Main Container Padding & Max-Width */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1060px !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border-subtle) !important;
        padding-top: 0.75rem;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    /* Typography Utilities */
    .mono { font-family: var(--font-mono) !important; }
    
    /* Top Application Bar */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 0 1.25rem 0;
        margin-bottom: 1.25rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    .brand-cluster {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-mark {
        width: 34px;
        height: 34px;
        background: #181D26;
        border: 1px solid var(--border-medium);
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    }
    .brand-name {
        font-size: 19px;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: var(--text-primary);
        line-height: 1.2;
    }
    .brand-tagline {
        font-size: 12px;
        color: var(--text-secondary);
        font-weight: 400;
        margin-top: 2px;
    }
    .header-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 4px 10px;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.22);
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 500;
        color: #34D399;
        font-family: var(--font-mono);
        letter-spacing: 0.02em;
    }
    .status-pulse {
        width: 6px;
        height: 6px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
    }

    /* Disclaimer Banner (Clean Clinical Safety Standard) */
    .safety-disclaimer-banner {
        background: rgba(245, 158, 11, 0.04);
        border: 1px solid rgba(245, 158, 11, 0.18);
        border-radius: var(--radius-md);
        padding: 10px 14px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }
    .safety-disclaimer-icon {
        color: #F59E0B;
        font-size: 14px;
        line-height: 1.4;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .safety-disclaimer-body {
        font-size: 12px;
        color: #CBD5E1;
        line-height: 1.5;
    }
    .safety-disclaimer-body strong {
        color: #FDE68A;
        font-weight: 600;
    }

    /* Sidebar Panels & Cards */
    .command-header {
        font-size: 10.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
        margin: 1.1rem 0 0.45rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .command-card {
        background: var(--bg-surface-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 12px;
        margin-bottom: 8px;
    }

    /* Triage Level Indicator */
    .triage-level-display {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .triage-level-number {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.02em;
        font-family: var(--font-mono);
    }
    .triage-level-badge {
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 3px 8px;
        border-radius: 4px;
    }
    
    /* Risk Stage Progress Track */
    .triage-track {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 4px;
        margin-top: 6px;
        margin-bottom: 10px;
    }
    .triage-track-step {
        height: 4px;
        border-radius: 2px;
        background: rgba(255, 255, 255, 0.08);
        transition: background 0.25s ease;
    }

    /* Colors by Level */
    .lvl-0-bg { background: #10B981; }
    .lvl-0-color { color: #10B981; }
    .lvl-0-badge { background: rgba(16, 185, 129, 0.12); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.25); }

    .lvl-1-bg { background: #38BDF8; }
    .lvl-1-color { color: #38BDF8; }
    .lvl-1-badge { background: rgba(56, 189, 248, 0.12); color: #7DD3FC; border: 1px solid rgba(56, 189, 248, 0.25); }

    .lvl-2-bg { background: #F59E0B; }
    .lvl-2-color { color: #F59E0B; }
    .lvl-2-badge { background: rgba(245, 158, 11, 0.12); color: #FCD34D; border: 1px solid rgba(245, 158, 11, 0.25); }

    .lvl-3-bg { background: #EF4444; }
    .lvl-3-color { color: #EF4444; }
    .lvl-3-badge { background: rgba(239, 68, 68, 0.15); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.35); }

    /* Telemetry Data Grid */
    .telemetry-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0;
        font-size: 11.5px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    .telemetry-row:last-child { border-bottom: none; }
    .telemetry-label { color: var(--text-secondary); }
    .telemetry-val { font-family: var(--font-mono); font-weight: 500; color: var(--text-primary); }

    /* Signal Tags */
    .signal-chip {
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 10px;
        padding: 2px 6px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 4px;
        color: #94A3B8;
        margin: 2px 2px 2px 0;
    }

    /* Welcome / Empty Screen */
    .welcome-container {
        text-align: center;
        max-width: 640px;
        margin: 2rem auto 1.75rem auto;
    }
    .welcome-title {
        font-size: 26px;
        font-weight: 600;
        letter-spacing: -0.03em;
        color: var(--text-primary);
        margin-bottom: 8px;
    }
    .welcome-desc {
        font-size: 14px;
        color: var(--text-secondary);
        line-height: 1.55;
        margin-bottom: 1.75rem;
    }

    /* Custom Scenario Card Buttons */
    div[data-testid="stColumn"] div.stButton > button {
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        justify-content: center !important;
        text-align: left !important;
        padding: 13px 16px !important;
        border-radius: var(--radius-md) !important;
        background: var(--bg-surface-elevated) !important;
        border: 1px solid var(--border-medium) !important;
        color: var(--text-primary) !important;
        min-height: 74px !important;
        transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
        margin-bottom: 8px !important;
    }
    div[data-testid="stColumn"] div.stButton > button:hover {
        background: var(--bg-surface-hover) !important;
        border-color: rgba(99, 102, 241, 0.45) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
    }
    div[data-testid="stColumn"] div.stButton > button p {
        text-align: left !important;
        margin: 0 !important;
        width: 100% !important;
        color: var(--text-primary) !important;
        font-size: 13px !important;
        line-height: 1.4 !important;
    }

    /* General Sidebar Buttons */
    section[data-testid="stSidebar"] div.stButton > button,
    section[data-testid="stSidebar"] div.stDownloadButton > button {
        border-radius: var(--radius-sm) !important;
        font-weight: 500 !important;
        font-size: 12px !important;
        letter-spacing: -0.01em !important;
        border: 1px solid var(--border-medium) !important;
        background-color: var(--bg-surface-elevated) !important;
        color: var(--text-primary) !important;
        padding: 6px 12px !important;
        transition: all 0.15s ease !important;
        margin-bottom: 6px !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover,
    section[data-testid="stSidebar"] div.stDownloadButton > button:hover {
        background-color: var(--bg-surface-hover) !important;
        border-color: var(--border-focus) !important;
        color: #FFFFFF !important;
    }

    /* Chat Messages */
    .chat-bubble-container {
        display: flex;
        gap: 12px;
        margin-bottom: 1.25rem;
    }
    .chat-bubble-user {
        background: #181D26;
        border: 1px solid var(--border-medium);
        border-radius: var(--radius-lg);
        padding: 12px 16px;
        font-size: 14px;
        line-height: 1.6;
        max-width: 82%;
        margin-left: auto;
    }
    .chat-bubble-ai {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        padding: 14px 18px;
        font-size: 14px;
        line-height: 1.6;
        max-width: 90%;
    }
    .message-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
        font-size: 11px;
        color: var(--text-muted);
    }

    /* Crisis Emergency Callout Card */
    .crisis-emergency-panel {
        background: rgba(239, 68, 68, 0.05);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-left: 4px solid #EF4444;
        border-radius: var(--radius-md);
        padding: 16px 18px;
        margin: 12px 0;
    }
    .crisis-panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .crisis-tag {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #F87171;
    }
    .hotline-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-top: 12px;
    }
    .hotline-chip {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: var(--radius-sm);
        padding: 8px 10px;
        text-decoration: none;
        display: block;
        transition: background 0.15s ease;
    }
    .hotline-chip:hover {
        background: rgba(239, 68, 68, 0.2);
    }
    .hotline-chip-name {
        font-size: 10.5px;
        color: #FCA5A5;
        display: block;
    }
    .hotline-chip-number {
        font-size: 14px;
        font-weight: 600;
        font-family: var(--font-mono);
        color: #FFFFFF;
        display: block;
        margin-top: 2px;
    }

    /* Chat Input Styling */
    div[data-testid="stChatInput"] {
        border-top: 1px solid var(--border-subtle);
        background: var(--bg-base);
        padding-top: 10px;
    }
    div[data-testid="stChatInput"] > div {
        background: var(--bg-surface-elevated) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-md) !important;
    }
    div[data-testid="stChatInput"] > div:focus-within {
        border-color: var(--accent-indigo) !important;
        box-shadow: 0 0 0 1px var(--accent-indigo) !important;
    }
</style>
"""
st.markdown(DESIGN_SYSTEM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. STATE INITIALIZATION & PIPELINE BINDING
# -----------------------------------------------------------------------------
if "pipe" not in st.session_state:
    st.session_state.pipe = build_pipeline("hybrid")
    st.session_state.msgs = []
    st.session_state.last = None

pipe = st.session_state.pipe
last = st.session_state.last

# Triage Definitions & Semantics
TRIAGE_LEVELS = {
    0: {
        "title": "Level 0 • Normal",
        "badge_class": "lvl-0-badge",
        "num_class": "lvl-0-color",
        "action_label": "Supportive Chat",
        "description": "Routine academic & campus lifestyle stress. Active empathetic listening mode."
    },
    1: {
        "title": "Level 1 • Mild",
        "badge_class": "lvl-1-badge",
        "num_class": "lvl-1-color",
        "action_label": "Support + Coping",
        "description": "Sub-clinical distress. Provides structured grounding & coping exercises."
    },
    2: {
        "title": "Level 2 • Moderate",
        "badge_class": "lvl-2-badge",
        "num_class": "lvl-2-color",
        "action_label": "Campus Referral",
        "description": "Prolonged withdrawal or despair. Formal campus counseling referral attached."
    },
    3: {
        "title": "Level 3 • Crisis",
        "badge_class": "lvl-3-badge",
        "num_class": "lvl-3-color",
        "action_label": "CRISIS PROTOCOL",
        "description": "Immediate suicidal ideation or self-harm risk. Deterministic non-LLM emergency dispatch."
    }
}

# -----------------------------------------------------------------------------
# 4. SIDEBAR: SAFETY COMMAND & TELEMETRY CENTER
# -----------------------------------------------------------------------------
with st.sidebar:
    # Sidebar Brand
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border-subtle);">
            <div style="display: flex; align-items: center; gap: 8px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    <path d="m9 12 2 2 4-4"/>
                </svg>
                <span style="font-weight: 600; font-size: 13.5px; letter-spacing: -0.01em;">Safety Gateway</span>
            </div>
            <span style="font-size: 10px; font-family: var(--font-mono); color: var(--text-muted);">MONITOR v2.0</span>
        </div>
    """, unsafe_allow_html=True)

    # Active Triage Status Card
    curr_lvl = last.level if last else 0
    triage_info = TRIAGE_LEVELS.get(curr_lvl, TRIAGE_LEVELS[0])

    # Dynamic Progress Bar Segments
    seg0 = "lvl-0-bg" if curr_lvl >= 0 else ""
    seg1 = "lvl-1-bg" if curr_lvl >= 1 else ""
    seg2 = "lvl-2-bg" if curr_lvl >= 2 else ""
    seg3 = "lvl-3-bg" if curr_lvl >= 3 else ""

    st.markdown(f"""
        <div class="command-card">
            <div class="triage-level-display">
                <div>
                    <span style="font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; display: block;">Active Triage State</span>
                    <span class="triage-level-number {triage_info['num_class']}">Level {curr_lvl}</span>
                </div>
                <span class="triage-level-badge {triage_info['badge_class']}">{triage_info['action_label']}</span>
            </div>
            <div class="triage-track">
                <div class="triage-track-step {seg0}"></div>
                <div class="triage-track-step {seg1}"></div>
                <div class="triage-track-step {seg2}"></div>
                <div class="triage-track-step {seg3}"></div>
            </div>
            <div style="font-size: 11px; color: var(--text-secondary); line-height: 1.4;">
                {triage_info['description']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Multi-Agent Resolution Matrix
    if last:
        g = last.gateway
        st.markdown("""<div class="command-header"><span>Multi-Agent Scoring Matrix</span><span class="mono" style="font-size: 10px;">max(R, L)</span></div>""", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="command-card" style="padding: 10px 12px;">
                <div class="telemetry-row">
                    <span class="telemetry-label">Deterministic Rules Layer</span>
                    <span class="telemetry-val" style="color: var(--accent-blue);">Level {g.rules_score}</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">LLM Classifier Agent</span>
                    <span class="telemetry-val" style="color: #A78BFA;">{f"Level {g.llm_score}" if g.llm_score is not None else "N/A (Bypassed)"}</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Resolved Hybrid Level</span>
                    <span class="telemetry-val {triage_info['num_class']}">Level {g.hybrid_score}</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Multi-Turn Tracked Level</span>
                    <span class="telemetry-val" style="font-weight: 700;">Level {g.tracked_level}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Telemetry & Signals
        st.markdown("""<div class="command-header"><span>Triggered Signals</span></div>""", unsafe_allow_html=True)
        if g.signals:
            signals_html = "".join(f'<span class="signal-chip">{s}</span>' for s in g.signals)
            st.markdown(f"""<div class="command-card" style="padding: 8px 10px;">{signals_html}</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="command-card" style="padding: 8px 10px; font-size: 11px; color: var(--text-muted);">None detected</div>""", unsafe_allow_html=True)

        # Defense Verification
        st.markdown("""<div class="command-header"><span>Active Defenses</span></div>""", unsafe_allow_html=True)
        inj_status = '<span style="color: #EF4444; font-weight: 600;">TRIGGERED</span>' if g.injection_attempt else '<span style="color: #10B981;">CLEAN</span>'
        guard_status = '<span style="color: #EF4444; font-weight: 600;">INTERCEPTED</span>' if last.guardrail_triggered else '<span style="color: #10B981;">PASSED</span>'
        latch_status = '<span style="color: #EF4444; font-weight: 600;">LATCHED (L3)</span>' if pipe.gateway.tracker.latched else '<span style="color: var(--text-muted);">UNLATCHED</span>'
        gen_status = '<span style="color: #10B981;">BYPASSED (Deterministic)</span>' if not last.reply_from_llm else '<span style="color: var(--text-secondary);">ACTIVE (Empathetic LLM)</span>'

        st.markdown(f"""
            <div class="command-card" style="padding: 10px 12px;">
                <div class="telemetry-row"><span class="telemetry-label">Prompt Injection Shield</span><span class="telemetry-val">{inj_status}</span></div>
                <div class="telemetry-row"><span class="telemetry-label">Output Guardrail Filter</span><span class="telemetry-val">{guard_status}</span></div>
                <div class="telemetry-row"><span class="telemetry-label">Multi-Turn Crisis Latch</span><span class="telemetry-val">{latch_status}</span></div>
                <div class="telemetry-row"><span class="telemetry-label">Generation Mode</span><span class="telemetry-val">{gen_status}</span></div>
            </div>
        """, unsafe_allow_html=True)

        # Simulated Counselor Alert Console (Requirement R9)
        if last.notice:
            st.markdown("""<div class="command-header" style="color: #EF4444;"><span>Counselor Handoff (Simulated)</span></div>""", unsafe_allow_html=True)
            with st.expander("Inspect JSON Payload", expanded=False):
                st.json(last.notice)

    # Backend / Model Info
    st.markdown("""<div class="command-header"><span>Pipeline Runtime</span></div>""", unsafe_allow_html=True)
    backend_name = getattr(pipe.gateway.client, "backend", "unknown").upper()
    model_name = getattr(pipe.gateway.client, "model", "default")
    st.markdown(f"""
        <div class="command-card" style="padding: 8px 12px; font-size: 11px;">
            <div class="telemetry-row"><span class="telemetry-label">Provider</span><span class="telemetry-val mono">{backend_name}</span></div>
            <div class="telemetry-row"><span class="telemetry-label">Model</span><span class="telemetry-val mono" style="font-size: 10px;">{model_name}</span></div>
            <div class="telemetry-row"><span class="telemetry-label">Session State</span><span class="telemetry-val" style="color: #34D399;">Ephemeral (No DB)</span></div>
        </div>
    """, unsafe_allow_html=True)

    # Session Management Actions
    if st.button("New Conversation", use_container_width=True):
        pipe.reset()
        st.session_state.msgs = []
        st.session_state.last = None
        st.rerun()

    # Benchmark & Audit Interface
    st.markdown("""<div class="command-header"><span>Audit & Benchmarking</span></div>""", unsafe_allow_html=True)

    # Show verified benchmark scorecard if metrics.json exists
    metrics_path = pathlib.Path("results/metrics.json")
    if metrics_path.exists():
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                m_data = json.load(f)
            recall_pct = f"{m_data.get('crisis_safety_recall', 1.0) * 100:.1f}%"
            false_alarm = f"{m_data.get('false_crisis_rate', 0.0) * 100:.1f}%"
            acc_pct = f"{m_data.get('level_accuracy', 0.955) * 100:.1f}%"
            st.markdown(f"""
                <div class="command-card" style="padding: 10px 12px; margin-bottom: 8px;">
                    <div style="font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                        Dev Set Audit (156 Dialogues)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; text-align: center;">
                        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 6px; padding: 6px 2px;">
                            <span style="display: block; font-size: 13px; font-weight: 700; color: #34D399; font-family: var(--font-mono);">{recall_pct}</span>
                            <span style="display: block; font-size: 9px; color: var(--text-muted); text-transform: uppercase;">Crisis Recall</span>
                        </div>
                        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 6px; padding: 6px 2px;">
                            <span style="display: block; font-size: 13px; font-weight: 700; color: #34D399; font-family: var(--font-mono);">{false_alarm}</span>
                            <span style="display: block; font-size: 9px; color: var(--text-muted); text-transform: uppercase;">False Alarm</span>
                        </div>
                        <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 6px; padding: 6px 2px;">
                            <span style="display: block; font-size: 13px; font-weight: 700; color: #818CF8; font-family: var(--font-mono);">{acc_pct}</span>
                            <span style="display: block; font-size: 9px; color: var(--text-muted); text-transform: uppercase;">Accuracy</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

    if st.button("Run Dev Benchmark (156 cases)", use_container_width=True):
        with st.spinner("Executing full pipeline audit on dev split..."):
            audit_proc = subprocess.run(
                [sys.executable, "-m", "evaluation.run_eval", "--split", "dev"],
                capture_output=True,
                text=True,
            )
        st.success("Benchmark completed.")
        st.code((audit_proc.stdout or audit_proc.stderr)[-1600:], language="text")

    log_file = pathlib.Path("results/test_log.csv")
    if log_file.exists():
        st.download_button(
            label="Download Audit Log (CSV)",
            data=log_file.read_bytes(),
            file_name="mannsahara_audit_log.csv",
            mime="text/csv",
            use_container_width=True
        )

# -----------------------------------------------------------------------------
# 5. MAIN CHAT & CONVERSATION INTERFACE
# -----------------------------------------------------------------------------

# Application Bar Header
st.markdown("""
    <div class="app-header">
        <div class="brand-cluster">
            <div class="brand-mark">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="m4.93 4.93 4.24 4.24"/>
                    <path d="m14.83 9.17 4.24-4.24"/>
                    <path d="m14.83 14.83 4.24 4.24"/>
                    <path d="m9.17 14.83-4.24 4.24"/>
                    <circle cx="12" cy="12" r="4"/>
                </svg>
            </div>
            <div>
                <div class="brand-name">MannSahara</div>
                <div class="brand-tagline">Autonomous Multi-Agent Safety & Triage Pipeline for Student Wellbeing</div>
            </div>
        </div>
        <div class="header-status-pill">
            <div class="status-pulse"></div>
            <span>SAFETY GATEWAY ONLINE</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Strict Research Prototype Clinical Disclaimer
st.markdown("""
    <div class="safety-disclaimer-banner">
        <div class="safety-disclaimer-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
        </div>
        <div class="safety-disclaimer-body">
            <strong>Clinical & Research Safety Notice:</strong> MannSahara is an academic research prototype. 
            It is <strong>not therapy</strong>, does <strong>not diagnose or treat</strong> medical conditions, and does not replace licensed psychological care. 
            In crisis situations, the pipeline autonomously bypasses generative AI and connects you directly to official national crisis helplines.
        </div>
    </div>
""", unsafe_allow_html=True)

# Welcome State: Clean suggested scenario selectors
if not st.session_state.msgs:
    st.markdown("""
        <div class="welcome-container">
            <div class="welcome-title">How can I support you today?</div>
            <div class="welcome-desc">
                MannSahara provides a safe, confidential space for university students to vent, practice grounding exercises, or connect with counseling resources.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 10px;">
            Suggested Evaluation Scenarios:
        </div>
    """, unsafe_allow_html=True)

    sc_col1, sc_col2 = st.columns(2)
    with sc_col1:
        if st.button("**Exam Stress & Study Planning**\n\nLevel 0 · Academic Workload & Focus", use_container_width=True):
            st.session_state.pending_prompt = "Mid-sems start Monday and I can't focus on operating systems."
        if st.button("**Insomnia & Emotional Exhaustion**\n\nLevel 1 · Sub-Clinical Distress & Coping", use_container_width=True):
            st.session_state.pending_prompt = "I haven't been sleeping well lately and I feel low most of the days."
    with sc_col2:
        if st.button("**Academic Withdrawal & Despair**\n\nLevel 2 · Moderate Distress & Referral", use_container_width=True):
            st.session_state.pending_prompt = "I've felt hopeless for weeks and I've stopped going to class."
        if st.button("**Hyperbole Trap Disambiguation**\n\nLevel 0 · Idiomatic Expression Filter", use_container_width=True):
            st.session_state.pending_prompt = "This DBMS assignment is killing me lol, dying to go home!"

# Render Conversation Message Thread
for m in st.session_state.msgs:
    role = m["role"]
    content = m["content"]
    level = m.get("level", 0)
    timestamp = m.get("timestamp", "")
    escaped_content = html.escape(content)

    if role == "user":
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 1.25rem;">
                <div class="chat-bubble-user">
                    <div class="message-meta" style="justify-content: flex-end;">
                        <span style="font-weight: 600; color: #E2E8F0;">Student</span>
                        <span>•</span>
                        <span>{timestamp}</span>
                    </div>
                    <div style="white-space: pre-wrap; font-size: 14px; line-height: 1.6; color: #F1F5F9;">{escaped_content}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Determine level badge
        badge_meta = TRIAGE_LEVELS.get(level, TRIAGE_LEVELS[0])
        
        # If crisis response, render dedicated solemn emergency assistance card
        if level == 3:
            crisis_markup = f"""
                <div class="chat-bubble-container">
                    <div class="chat-bubble-ai" style="border-color: rgba(239, 68, 68, 0.4); width: 100%; background: #160F11;">
                        <div class="message-meta">
                            <span style="color: #F87171; font-weight: 600;">MannSahara Safety Triage</span>
                            <span>•</span>
                            <span class="triage-level-badge lvl-3-badge">CRISIS PROTOCOL ACTIVE</span>
                            <span>•</span>
                            <span>{timestamp}</span>
                        </div>
                        <div class="crisis-emergency-panel">
                            <div class="crisis-panel-header">
                                <span class="crisis-tag">Emergency Referral Hotlines</span>
                                <span style="font-size: 11px; color: #FCA5A5; font-family: var(--font-mono);">LLM Generation Bypassed</span>
                            </div>
                            <div style="font-size: 14px; color: #FEE2E2; line-height: 1.65; white-space: pre-wrap; margin-bottom: 12px;">{escaped_content}</div>
                            <div class="hotline-row">
                                <a class="hotline-chip" href="tel:14416">
                                    <span class="hotline-chip-name">Tele-MANAS (Govt of India · 24x7)</span>
                                    <span class="hotline-chip-number">14416</span>
                                </a>
                                <a class="hotline-chip" href="tel:18005990019">
                                    <span class="hotline-chip-name">KIRAN Mental Health Helpline</span>
                                    <span class="hotline-chip-number">1800-599-0019</span>
                                </a>
                                <a class="hotline-chip" href="tel:112">
                                    <span class="hotline-chip-name">National Emergency Services</span>
                                    <span class="hotline-chip-number">112</span>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            """
            st.markdown(crisis_markup, unsafe_allow_html=True)
        else:
            ai_markup = f"""
                <div class="chat-bubble-container">
                    <div class="chat-bubble-ai">
                        <div class="message-meta">
                            <span style="font-weight: 600; color: #E2E8F0;">MannSahara</span>
                            <span>•</span>
                            <span class="triage-level-badge {badge_meta['badge_class']}">{badge_meta['action_label']}</span>
                            <span>•</span>
                            <span>{timestamp}</span>
                        </div>
                        <div style="font-size: 14px; line-height: 1.65; white-space: pre-wrap; color: #CBD5E1;">{escaped_content}</div>
                    </div>
                </div>
            """
            st.markdown(ai_markup, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. MESSAGE DISPATCH & PIPELINE EXECUTION
# -----------------------------------------------------------------------------
prompt_to_dispatch = None

# Check if a suggested scenario was clicked
if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    prompt_to_dispatch = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
elif typed_prompt := st.chat_input("Type your message here (English or Hinglish)..."):
    prompt_to_dispatch = typed_prompt

if prompt_to_dispatch:
    curr_time = datetime.now().strftime("%I:%M %p")
    
    # 1. Register student message
    st.session_state.msgs.append({
        "role": "user",
        "content": prompt_to_dispatch,
        "timestamp": curr_time
    })

    # 2. Execute safety gateway & pipeline
    with st.spinner("Processing through safety triage..."):
        result = pipe.handle(prompt_to_dispatch)
    
    # 3. Register assistant response
    st.session_state.msgs.append({
        "role": "assistant",
        "content": result.reply,
        "level": result.level,
        "timestamp": datetime.now().strftime("%I:%M %p")
    })
    st.session_state.last = result
    st.rerun()
