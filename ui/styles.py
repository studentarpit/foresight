"""Inject global CSS and Google Fonts for the Foresight premium dark UI."""

import streamlit as st

_FONTS_HTML = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap" rel="stylesheet">
"""

_CSS = """
<style>
/* ── Base ─────────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  color: #f0f0f0;
}

/* Hide default Streamlit chrome */
#MainMenu  { visibility: hidden; }
footer     { visibility: hidden; }
header[data-testid="stHeader"] { visibility: hidden; height: 0; }

.main .block-container {
  padding-top: 1.2rem;
  padding-bottom: 2rem;
  max-width: 1440px;
}

/* ── Foresight Persistent Header ─────────────────────────────────────────── */
.fs-header-hr {
  border: none;
  border-top: 1px solid rgba(255,255,255,0.07);
  margin: 10px 0 18px 0;
}
.fs-logo-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.fs-hex {
  width: 34px; height: 34px;
  background: linear-gradient(135deg, #00e676, #00b34a);
  clip-path: polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);
}
.fs-wordmark {
  font-family: 'DM Serif Display', serif;
  font-size: 1.55em;
  font-weight: 400;
  color: #f0f0f0;
  letter-spacing: 0.02em;
  line-height: 1.1;
}
.fs-tagline {
  font-size: 0.7em;
  color: rgba(255,255,255,0.38);
  letter-spacing: 0.05em;
  font-family: 'DM Mono', monospace;
}
.market-pill {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.72em;
  font-weight: 600;
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.04em;
}
.market-open   { background: rgba(0,230,118,0.12); color: #00e676; border: 1px solid rgba(0,230,118,0.3); }
.market-closed { background: rgba(255,82,82,0.12);  color: #ff5252; border: 1px solid rgba(255,82,82,0.3); }
.scan-ts {
  font-size: 0.68em;
  color: rgba(255,255,255,0.3);
  font-family: 'DM Mono', monospace;
  line-height: 1.4;
}

/* ── Metric summary strip ─────────────────────────────────────────────────── */
.metric-card {
  background: #12121a;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 4px;
}
.metric-label {
  font-size: 0.68em;
  color: rgba(255,255,255,0.38);
  text-transform: uppercase;
  letter-spacing: 0.09em;
  margin-bottom: 6px;
  font-family: 'DM Mono', monospace;
}
.metric-value {
  font-size: 1.9em;
  font-weight: 700;
  font-family: 'DM Mono', monospace;
  line-height: 1;
}
.metric-sub {
  font-size: 0.68em;
  color: rgba(255,255,255,0.3);
  margin-top: 4px;
  font-family: 'DM Mono', monospace;
}
.mv-green  { color: #00e676; }
.mv-yellow { color: #ffd740; }
.mv-white  { color: #f0f0f0; }
.mv-red    { color: #ff5252; }

/* ── Section divider labels ───────────────────────────────────────────────── */
.section-lbl {
  font-size: 0.66em;
  color: rgba(255,255,255,0.28);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-family: 'DM Mono', monospace;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 20px 0 10px 0;
}
.section-lbl::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255,255,255,0.06);
}

/* ── Signal badges ────────────────────────────────────────────────────────── */
.sig-strong-buy {
  background: rgba(0,230,118,0.14); color: #00e676;
  border: 1px solid rgba(0,230,118,0.28);
  padding: 3px 9px; border-radius: 4px;
  font-size: 0.72em; font-weight: 700;
  font-family: 'DM Mono', monospace; letter-spacing: 0.03em;
}
.sig-watch {
  background: rgba(255,215,64,0.14); color: #ffd740;
  border: 1px solid rgba(255,215,64,0.28);
  padding: 3px 9px; border-radius: 4px;
  font-size: 0.72em; font-weight: 700;
  font-family: 'DM Mono', monospace;
}
.sig-neutral {
  background: rgba(255,152,0,0.14); color: #ff9800;
  border: 1px solid rgba(255,152,0,0.28);
  padding: 3px 9px; border-radius: 4px;
  font-size: 0.72em; font-weight: 700;
  font-family: 'DM Mono', monospace;
}
.sig-avoid {
  background: rgba(255,82,82,0.14); color: #ff5252;
  border: 1px solid rgba(255,82,82,0.28);
  padding: 3px 9px; border-radius: 4px;
  font-size: 0.72em; font-weight: 700;
  font-family: 'DM Mono', monospace;
}

/* ── Alert banner items ───────────────────────────────────────────────────── */
.alert-row {
  display: flex; align-items: center; gap: 12px;
  padding: 7px 12px; border-radius: 6px;
  margin-bottom: 5px;
  background: rgba(255,255,255,0.025);
  border: 1px solid rgba(255,255,255,0.05);
  font-size: 0.84em;
}
.alert-high { border-left: 3px solid #ff5252; }
.alert-med  { border-left: 3px solid #ffd740; }

/* ── Deep-dive container ──────────────────────────────────────────────────── */
.dd-wrap {
  background: #12121a;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 22px 24px;
  margin-top: 10px;
}
.dd-name {
  font-family: 'DM Serif Display', serif;
  font-size: 1.45em;
  line-height: 1.2;
}
.dd-ticker {
  font-family: 'DM Mono', monospace;
  font-size: 0.82em;
  color: rgba(255,255,255,0.38);
  margin-left: 6px;
}

/* ── FVS score block ──────────────────────────────────────────────────────── */
.fvs-block {
  padding: 12px 18px; border-radius: 8px;
  display: flex; align-items: center; gap: 14px;
  margin-bottom: 14px;
}
.fvs-num {
  font-size: 2.6em; font-weight: 900;
  font-family: 'DM Mono', monospace; line-height: 1;
}

/* ── 4 score cards ────────────────────────────────────────────────────────── */
.score-card {
  background: rgba(255,255,255,0.035);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 8px; padding: 13px 15px;
}
.score-lbl {
  font-size: 0.66em; color: rgba(255,255,255,0.38);
  text-transform: uppercase; letter-spacing: 0.07em;
  font-family: 'DM Mono', monospace; margin-bottom: 4px;
}
.score-val {
  font-size: 1.45em; font-weight: 700;
  font-family: 'DM Mono', monospace;
}
.bar-bg  { height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 7px; }
.bar-fill{ height: 4px; border-radius: 2px; }

/* ── Thesis box ───────────────────────────────────────────────────────────── */
.thesis-box {
  border-left: 3px solid #00e676;
  background: rgba(0,230,118,0.055);
  border-radius: 0 8px 8px 0;
  padding: 13px 16px; margin-bottom: 14px;
  font-size: 0.88em; line-height: 1.65;
}

/* ── Case cards ───────────────────────────────────────────────────────────── */
.case-card {
  background: rgba(255,255,255,0.025);
  border-radius: 8px; padding: 13px 15px;
  border: 1px solid rgba(255,255,255,0.06);
  font-size: 0.84em; line-height: 1.55;
}
.case-bull { border-top: 2px solid #00e676; }
.case-base { border-top: 2px solid #ffd740; }
.case-bear { border-top: 2px solid #ff5252; }
.case-hdr  { font-weight: 700; margin-bottom: 7px; font-size: 0.88em;
             text-transform: uppercase; letter-spacing: 0.05em; }

/* ── Analyse sub-tab header ───────────────────────────────────────────────── */
.analyse-hdr {
  font-family: 'DM Serif Display', serif;
  font-size: 1.3em;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: #0d0d14 !important;
  border-right: 1px solid rgba(255,255,255,0.055) !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p {
  font-size: 0.82em !important;
  color: rgba(255,255,255,0.65) !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid rgba(255,255,255,0.07) !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: rgba(255,255,255,0.38) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.9em !important;
  font-weight: 500 !important;
  padding: 10px 22px !important;
  border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
  color: #f0f0f0 !important;
  border-bottom: 2px solid #00e676 !important;
  background: transparent !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, #00e676, #00b34a) !important;
  color: #070a07 !important;
  border: none !important;
  font-weight: 700 !important;
  font-family: 'DM Sans', sans-serif !important;
  border-radius: 6px !important;
  letter-spacing: 0.02em !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #33eb91, #00cc55) !important;
  box-shadow: 0 4px 14px rgba(0,230,118,0.28) !important;
  transform: translateY(-1px) !important;
}
.stButton > button:disabled {
  background: rgba(255,255,255,0.08) !important;
  color: rgba(255,255,255,0.3) !important;
  cursor: not-allowed !important;
  transform: none !important;
  box-shadow: none !important;
}

/* ── st.metric override ───────────────────────────────────────────────────── */
[data-testid="metric-container"] {
  background: #12121a;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 8px;
  padding: 12px 14px;
}
[data-testid="stMetricLabel"] {
  font-size: 0.68em !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
  color: rgba(255,255,255,0.38) !important;
  font-family: 'DM Mono', monospace !important;
}
[data-testid="stMetricValue"] {
  font-family: 'DM Mono', monospace !important;
  font-size: 1.45em !important;
}

/* ── Dataframe ────────────────────────────────────────────────────────────── */
.stDataFrame  { border-radius: 8px; overflow: hidden; }
</style>
"""


def inject_styles() -> None:
    """Inject Google Fonts and global CSS into the Streamlit app."""
    st.markdown(_FONTS_HTML, unsafe_allow_html=True)
    st.markdown(_CSS, unsafe_allow_html=True)
