"""Picky dashboard theme — 60/30/10 dark design system."""

from __future__ import annotations

from pathlib import Path
from html import escape

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

/* Preview-inspired navigation rows: controls behave as buttons but read as links. */
.fx-brand { display:flex; align-items:center; gap:10px; margin:0 0 12px; padding: 0 0 8px; }
.fx-brand-icon { width:36px; height:36px; flex-shrink:0; border-radius:9px;
  background:var(--color-accent); display:flex; align-items:center; justify-content:center; }
.fx-brand-name { font-size:17px; font-weight:700; }
.fx-nav-divider { height:1px; background:var(--color-border); margin: 12px 0; }
.fx-utility-divider { margin-top:24px; }
section[data-testid="stSidebar"] [class*="st-key-nav_"] {
  margin-bottom: 3px;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button {
  display:flex !important; justify-content:flex-start !important; gap:12px !important;
  width:100%; min-height:42px !important; padding:9px 12px !important;
  border:0 !important; border-radius:8px !important; box-shadow:none !important;
  background:transparent !important; color:var(--color-text-secondary) !important;
  font-size:13px !important; font-weight:500 !important; text-align:left !important;
  transition:background-color .15s ease, color .15s ease;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover {
  background:var(--color-surface-hover) !important;
  color:var(--color-text-primary) !important;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:focus-visible {
  outline:2px solid var(--color-accent) !important; outline-offset:2px;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button [data-testid="stIconMaterial"] {
  color:var(--color-text-secondary) !important; font-size:18px !important;
}
@keyframes fx-page-in {
  from { opacity: .65; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
[class*="st-key-view_"] { animation: fx-page-in .2s ease-out both; }
@media (prefers-reduced-motion:reduce) {
  [class*="st-key-view_"] { animation:none !important; }
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

.fx-league-card {
  display: flex;
  align-items: center;
  gap: 10px 18px;
  flex-wrap: wrap;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  margin-bottom: 20px;
  color: var(--color-text-secondary);
  font-size: 13px;
}
.fx-league-card strong { color: var(--color-text-primary); font-size: 16px; }
.fx-league-card span:not(:last-child)::after {
  content: "·";
  margin-left: 18px;
  color: var(--color-text-muted);
}
.fx-rec-table { width: 100%; overflow-x: auto; }
.fx-rec-head, .fx-rec-row {
  display: grid;
  grid-template-columns: 36px minmax(140px, 2.1fr) minmax(90px, 1fr) minmax(72px, .8fr) minmax(130px, 1fr);
  gap: 12px;
  align-items: center;
}
.fx-rec-head {
  padding: 12px 14px;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  background: var(--color-surface-raised);
  color: var(--color-text-secondary);
  font-weight: 600;
  font-size: 12px;
}
.fx-rec-head > :last-child { text-align: right; }
.fx-rec-row {
  padding: 13px 14px;
  border-bottom: 1px solid var(--color-border);
}
.fx-rec-row:last-child { border-bottom: none; }
.fx-rec-row:hover { background: var(--color-surface-hover); }
.fx-rec-row.top { background: rgba(56, 185, 121, 0.07); }
.fx-rec-rank { color: var(--color-accent); font-weight: 700; font-size: 14px; }
.fx-rec-name { font-weight: 600; font-size: 14px; color: var(--color-text-primary); }
.fx-rec-team { font-size: 13px; color: var(--color-text-secondary); }
.fx-rec-score { font-size: 14px; font-weight: 700; color: var(--color-text-primary); text-align: right; font-variant-numeric: tabular-nums; }
.fx-pos {
  display: inline-block;
  background: var(--color-surface-raised);
  border-radius: 5px;
  color: var(--color-text-secondary);
  padding: 3px 7px;
  font-size: 12px;
}
@media (max-width: 640px) {
  .fx-rec-head, .fx-rec-row { grid-template-columns: 24px minmax(100px, 1fr) 64px 82px !important; gap: 6px; }
  .fx-rec-head > :nth-child(4), .fx-rec-row > :nth-child(4) { display: none !important; }
  .fx-rec-head, .fx-rec-row { padding-left: 8px; padding-right: 8px; }
  .fx-rec-score { font-size: 12px; }
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

/* Minimal sidebar header matching the selected reference composition. */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding-top: 18px !important;
}
section[data-testid="stSidebar"] .fx-wordmark {
  font-family: var(--font);
  color: var(--color-text-primary);
  font-weight: 700;
  font-size: 21px;
  line-height: 1.15;
  letter-spacing: -.03em;
}
section[data-testid="stSidebar"] [data-testid="stImage"] img {
  display: block;
  border-radius: 11px;
}
.fx-connection-mini {
  margin: 22px 0 22px;
  padding: 0 3px;
}
.fx-status-pill {
  width: fit-content;
  max-width: 100%;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  color: #58D995;
  background: rgba(56,185,121,.15);
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.25;
  border-radius: 999px;
}
.fx-status-dot { width: 8px; height: 8px; flex-shrink: 0; border-radius: 50%;
  background: var(--color-accent); }
.fx-mini-league {
  margin-top: 12px;
  color: var(--color-text-primary);
  font-size: 17px;
  line-height: 1.25;
  font-weight: 700;
  overflow-wrap: anywhere;
}
.fx-mini-helper {
  color: var(--color-text-secondary);
  font-size: 12px;
  line-height: 1.45;
  margin-top: 7px;
}
.fx-conn-offline .fx-status-pill { background: var(--color-surface-raised);
  color: var(--color-text-secondary); }
.fx-conn-offline .fx-status-dot { background: var(--color-text-muted); }
.fx-nav-divider { margin-top: 18px; margin-bottom: 16px; }
.fx-utility-divider { margin-top: 24px; }
section[data-testid="stSidebar"] [class*="st-key-nav_"] button {
  min-height: 44px !important;
}
hr { border-color: var(--color-border) !important; }

@media (max-width: 900px) {
  .block-container {
    padding-left: var(--space-4) !important;
    padding-right: var(--space-4) !important;
  }
  .fx-page-title { font-size: 22px !important; }
  .fx-rec-head, .fx-rec-row { grid-template-columns: 28px minmax(110px, 1fr) 84px 94px !important; }
  .fx-rec-head > :nth-child(4), .fx-rec-row > :nth-child(4) { display: none !important; }
  .fx-league-card { gap: 8px 14px; }

  div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 24px !important;
  }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    """Compact branded wordmark using the green dice tile from the reference."""
    # Native st.image renders SVG data directly; inline SVG in st.html can be
    # stripped by HTML sanitization and leave an empty green square.
    dice_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
      <rect width="48" height="48" rx="11" fill="#38B979"/>
      <g stroke="#0D2330" stroke-width="3" stroke-linejoin="round" fill="none">
        <rect x="19" y="8" width="21" height="21" rx="4" transform="rotate(-42 29.5 18.5)"/>
        <rect x="8" y="19" width="23" height="23" rx="4"/>
      </g>
      <g fill="#0D2330">
        <circle cx="15" cy="26" r="2.1"/><circle cx="24" cy="35" r="2.1"/>
        <circle cx="23.5" cy="13.5" r="1.9"/><circle cx="32.5" cy="20" r="1.9"/>
      </g>
    </svg>"""
    brand_logo, brand_name = st.columns([0.27, 0.73], gap="small", vertical_alignment="center")
    with brand_logo:
        st.image(dice_svg.encode("utf-8"), width=48)
    with brand_name:
        st.markdown(
            '<div class="fx-wordmark">Picky</div>',
            unsafe_allow_html=True,
        )


def render_connection_card(
    *,
    connected: bool,
    league_name: str = "",
    meta: str = "",
) -> None:
    """Compact status pill and league details, without a bulky card background."""
    cls = "fx-connection-mini" if connected else "fx-connection-mini fx-conn-offline"
    status = "Draft configured" if connected else "Not configured"
    league = league_name or ("Configured draft" if connected else "No draft selected")
    helper = meta or ("Manage under Settings" if connected else "Open Settings to connect")
    st.markdown(
        f"""
<div class="{cls}">
  <div class="fx-status-pill">
    <span class="fx-status-dot" aria-hidden="true"></span>
    <span>{escape(status)}</span>
  </div>
  <div class="fx-mini-league">{escape(league)}</div>
  <div class="fx-mini-helper">{escape(helper)}</div>
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
