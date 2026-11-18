"""Picky dashboard theme — 60/30/10 dark design system."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

APP_NAME = "Picky"
APP_TAGLINE = "Live fantasy draft intelligence"
ICON_PATH = Path(__file__).resolve().parent / "assets" / "picky-icon.jpg"

NAV_PAGES = [
    ("overview", "Overview"),
    ("board", "Draft Board"),
    ("players", "Player Rankings"),
    ("reports", "Reports & News"),
]

UTIL_PAGES = [
    ("settings", "Settings & Connections"),
    ("help", "Help"),
]


def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --color-bg: #10151F;
  --color-surface: #1B2432;
  --color-surface-raised: #242E3D;
  --color-surface-hover: #2B3747;
  --color-accent: #38B979;
  --color-accent-hover: #2EA46B;
  --color-accent-subtle: #263C34;
  --color-text-primary: #F1F5F9;
  --color-text-secondary: #96A3B5;
  --color-text-muted: #8996A8;
  --color-border: #303B4D;
  --color-warning: #F4BC58;
  --color-danger: #EF7474;
  --color-info: #70A5F8;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 12px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --font: "Inter", system-ui, sans-serif;
  --sidebar-w: 248px;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
  }
}

html, body, [data-testid="stAppViewContainer"], .stApp {
  background: var(--color-bg) !important;
  color: var(--color-text-primary) !important;
  font-family: var(--font) !important;
}

[data-testid="stHeader"] {
  background: transparent !important;
}

[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"],
.material-icons,
.material-symbols-rounded,
.material-symbols-outlined {
  font-family: "Material Symbols Rounded", "Material Symbols Outlined",
    "Material Icons", sans-serif !important;
  font-style: normal !important;
  letter-spacing: normal !important;
  text-transform: none !important;
}

.block-container {
  padding-top: var(--space-6) !important;
  padding-bottom: var(--space-8) !important;
  padding-left: var(--space-6) !important;
  padding-right: var(--space-6) !important;
  max-width: 1440px !important;
}

/* Sidebar shell */
section[data-testid="stSidebar"] {
  width: var(--sidebar-w) !important;
  min-width: var(--sidebar-w) !important;
  max-width: var(--sidebar-w) !important;
  background: var(--color-bg) !important;
  border-right: 1px solid var(--color-border) !important;
  box-shadow: none !important;
  resize: none !important;
}

[data-testid="stSidebarResizeHandle"],
[data-testid="stSidebarResizer"] {
  display: none !important;
  pointer-events: none !important;
  width: 0 !important;
}

section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
  background: var(--color-bg) !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  max-height: calc(100vh - 3.5rem) !important;
  max-height: calc(100dvh - 3.5rem) !important;
  overflow-x: hidden !important;
  overflow-y: auto !important;
  overscroll-behavior: contain;
  padding-top: var(--space-4) !important;
  padding-bottom: var(--space-6) !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
  color: var(--color-text-primary) !important;
  font-family: var(--font) !important;
}

section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
  color: var(--color-text-muted) !important;
}

/* Brand */
.fx-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 16px 0;
  padding: 4px 2px 12px;
}
.fx-brand img {
  width: 40px !important;
  height: 40px !important;
  border-radius: 10px !important;
  object-fit: cover !important;
  display: block !important;
  pointer-events: none !important;
}
.fx-brand-name {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
  line-height: 1;
}

.fx-brand-wrap [data-testid="stImage"] img {
  width: 40px !important;
  height: 40px !important;
  min-width: 40px !important;
  border-radius: 10px !important;
  object-fit: cover !important;
  pointer-events: none !important;
}
.fx-brand-wrap [data-testid="stElementToolbar"],
.fx-brand-wrap [data-testid="stImage"] button {
  display: none !important;
}

/* Connection chip */
.fx-conn {
  background: var(--color-accent-subtle);
  border: 1px solid rgba(56, 185, 121, 0.28);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  margin: 0 0 18px 0;
}
.fx-conn-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-accent);
  margin: 0 0 4px 0;
}
.fx-conn-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(56, 185, 121, 0.22);
}
.fx-conn-dot.off {
  background: var(--color-text-muted);
  box-shadow: none;
}
.fx-conn-offline .fx-conn-status { color: var(--color-text-secondary); }
.fx-conn-league {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}
.fx-conn-meta {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--color-text-muted);
}

.fx-nav-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin: 8px 0 8px;
}

/* Nav radio as sidebar list */
section[data-testid="stSidebar"] div[role="radiogroup"] {
  gap: 4px !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label {
  min-height: 42px !important;
  border-radius: var(--radius-md) !important;
  padding: 8px 12px !important;
  border: none !important;
  background: transparent !important;
  color: var(--color-text-secondary) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
  background: var(--color-surface-hover) !important;
  color: var(--color-text-primary) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:focus-within {
  outline: 2px solid var(--color-accent) !important;
  outline-offset: 1px !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
  background: var(--color-accent-subtle) !important;
  color: var(--color-text-primary) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
  display: none !important;
}

/* Forms */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
  background-color: var(--color-surface-raised) !important;
  color: var(--color-text-primary) !important;
  -webkit-text-fill-color: var(--color-text-primary) !important;
  caret-color: var(--color-text-primary) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: none !important;
  min-height: 44px !important;
}
section[data-testid="stSidebar"] [data-baseweb="base-input"],
section[data-testid="stSidebar"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-baseweb="select"] > div {
  background-color: var(--color-surface-raised) !important;
  border-color: var(--color-border) !important;
  border-radius: var(--radius-md) !important;
}
input::placeholder {
  color: var(--color-text-muted) !important;
  -webkit-text-fill-color: var(--color-text-muted) !important;
}

[data-testid="stFileUploaderDropzone"] {
  background-color: var(--color-surface-raised) !important;
  border: 1px dashed var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--color-text-muted) !important;
}
[data-testid="stFileUploaderDropzone"] small {
  color: var(--color-text-muted) !important;
  font-family: var(--font) !important;
}
[data-testid="stFileUploaderDropzone"] button {
  background: var(--color-surface) !important;
  color: var(--color-text-primary) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-sm) !important;
  min-height: 40px !important;
}
[data-testid="stFileUploaderDropzone"] button [data-testid="stIconMaterial"],
[data-testid="stFileUploaderDropzone"] button .material-icons,
[data-testid="stFileUploaderDropzone"] button .material-symbols-rounded {
  font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
}

h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  font-family: var(--font) !important;
  color: var(--color-text-primary) !important;
  letter-spacing: -0.02em;
}
p, label, .stCaption, [data-testid="stCaptionContainer"] {
  color: var(--color-text-secondary) !important;
  font-family: var(--font) !important;
}
.stMarkdown, .stText { color: var(--color-text-primary) !important; }

/* Cards / metrics */
div[data-testid="stMetric"] {
  background: var(--color-surface) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 20px !important;
  box-shadow: none !important;
}
div[data-testid="stMetric"] label {
  color: var(--color-text-muted) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
  color: var(--color-text-primary) !important;
  font-family: var(--font) !important;
  font-size: 30px !important;
  font-weight: 700 !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--color-surface) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: none !important;
  margin-bottom: var(--space-4) !important;
}
[data-testid="stVerticalBlockBorderWrapper"] > div {
  background: transparent !important;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  background: var(--color-surface);
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}
.stTabs [data-baseweb="tab"] {
  border-radius: var(--radius-sm) !important;
  color: var(--color-text-secondary) !important;
  font-family: var(--font) !important;
  min-height: 40px !important;
}
.stTabs [aria-selected="true"] {
  background: var(--color-accent-subtle) !important;
  color: var(--color-text-primary) !important;
}

.stButton > button {
  background: var(--color-accent) !important;
  color: #0B1510 !important;
  border: none !important;
  border-radius: var(--radius-md) !important;
  font-weight: 600 !important;
  font-family: var(--font) !important;
  min-height: 40px !important;
}
.stButton > button:hover {
  background: var(--color-accent-hover) !important;
}
.stButton > button:focus-visible {
  outline: 2px solid var(--color-accent) !important;
  outline-offset: 2px !important;
}
.stDownloadButton > button {
  background: var(--color-surface-raised) !important;
  color: var(--color-text-primary) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  font-family: var(--font) !important;
  min-height: 40px !important;
}
.stSlider [data-baseweb="slider"] div[role="slider"] {
  background: var(--color-accent) !important;
}
.stAlert {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--color-border) !important;
  background: var(--color-surface) !important;
}
.stDataFrame, [data-testid="stDataFrame"] {
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  overflow: hidden;
}

/* Page chrome */
.fx-page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin: 0 0 20px 0;
}
.fx-page-title {
  margin: 0 !important;
  font-size: 26px !important;
  font-weight: 700 !important;
  color: var(--color-text-primary) !important;
  letter-spacing: -0.03em;
  line-height: 1.2;
}
.fx-page-sub {
  margin: 6px 0 0 !important;
  font-size: 14px !important;
  color: var(--color-text-secondary) !important;
}
.fx-live-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--color-accent-subtle);
  color: var(--color-accent) !important;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}
.fx-live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(56, 185, 121, 0.22);
}

.fx-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 4px 0 12px;
}
.fx-section-title {
  margin: 0 !important;
  font-size: 18px !important;
  font-weight: 600 !important;
  color: var(--color-text-primary) !important;
}
.fx-section-link {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-accent) !important;
  text-decoration: none;
}

.fx-league-strip {
  color: var(--color-text-muted);
  font-size: 13px;
  margin: 0 0 16px 0;
}

.fx-badge {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.fx-badge-value {
  background: rgba(56, 185, 121, 0.18);
  color: var(--color-accent) !important;
}
.fx-badge-caution {
  background: rgba(244, 188, 88, 0.18);
  color: var(--color-warning) !important;
}

.fx-rec-row {
  display: grid;
  grid-template-columns: 36px 1fr auto;
  gap: 12px;
  align-items: center;
  padding: 12px 4px;
  border-bottom: 1px solid var(--color-border);
}
.fx-rec-row:last-child { border-bottom: none; }
.fx-rec-row.top {
  background: rgba(56, 185, 121, 0.06);
  border-radius: var(--radius-sm);
  padding-left: 8px;
  padding-right: 8px;
}
.fx-rec-rank {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-accent);
}
.fx-rec-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}
.fx-rec-meta {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 2px;
}
.fx-rec-score {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  text-align: right;
}
.fx-pos {
  display: inline-block;
  margin-right: 6px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--color-surface-raised);
  color: var(--color-text-secondary);
  font-size: 11px;
  font-weight: 500;
}

.fx-settings-group {
  margin-bottom: 8px;
}
.fx-settings-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 8px;
}

hr { border-color: var(--color-border) !important; }

@media (max-width: 900px) {
  .block-container {
    padding-left: var(--space-4) !important;
    padding-right: var(--space-4) !important;
  }
  .fx-page-title { font-size: 22px !important; }
  div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 24px !important;
  }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    if ICON_PATH.is_file():
        c1, c2 = st.columns([0.28, 0.72], vertical_alignment="center")
        with c1:
            st.markdown('<div class="fx-brand-wrap">', unsafe_allow_html=True)
            st.image(str(ICON_PATH), width=40)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown(
                f'<div class="fx-brand-name">{APP_NAME}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f'<div class="fx-brand"><span class="fx-brand-name">{APP_NAME}</span></div>',
            unsafe_allow_html=True,
        )


def render_connection_card(
    *,
    connected: bool,
    league_name: str = "",
    meta: str = "",
) -> None:
    cls = "fx-conn" if connected else "fx-conn fx-conn-offline"
    status = "Draft connected" if connected else "Not connected"
    dot = "fx-conn-dot" if connected else "fx-conn-dot off"
    league = league_name or ("Open Settings to connect" if not connected else "Connected Draft")
    meta_html = f'<p class="fx-conn-meta">{meta}</p>' if meta else ""
    st.markdown(
        f"""
<div class="{cls}">
  <div class="fx-conn-status"><span class="{dot}"></span>{status}</div>
  <p class="fx-conn-league">{league}</p>
  {meta_html}
</div>
""",
        unsafe_allow_html=True,
    )


def render_page_header(*, title: str, subtitle: str, live: bool = False) -> None:
    live_html = (
        '<div class="fx-live-pill"><span class="fx-live-dot"></span>Live</div>'
        if live
        else ""
    )
    st.markdown(
        f"""
<div class="fx-page-header">
  <div>
    <h1 class="fx-page-title">{title}</h1>
    <p class="fx-page-sub">{subtitle}</p>
  </div>
  {live_html}
</div>
""",
        unsafe_allow_html=True,
    )
