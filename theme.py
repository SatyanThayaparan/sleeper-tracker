"""Picky dashboard theme — 60/30/10 dark design system."""

from __future__ import annotations

from pathlib import Path
from html import escape

import streamlit as st

APP_NAME = "Picky"
APP_TAGLINE = "Live fantasy draft intelligence"
ICON_PATH = Path(__file__).resolve().parent / "assets" / "picky-logo.png"

NAV_PAGES = [
    ("overview", "Overview"),
    ("team", "My Team"),
    ("board", "Draft Board"),
    ("players", "Player Rankings"),
    ("reports", "Reports & News"),
    ("lab", "AI Lab"),
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
  --sidebar-w: 336px;
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
  max-width: 1600px !important;
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

/* Structured draft activity rows */
.fx-activity-row {
  display:flex; align-items:center; gap:14px;
  padding:13px 16px; margin:8px 0;
  border-radius:12px; border:1px solid var(--color-border);
  background:var(--color-surface); color:var(--color-text-primary);
}
.fx-activity-number {
  display:flex; align-items:center; justify-content:center;
  width:42px; min-width:42px; height:40px; border-radius:10px;
  font-weight:700; font-variant-numeric:tabular-nums;
  background:var(--color-surface-raised); color:var(--color-accent);
}
.fx-activity-row strong { display:block; font-size:14px; }
.fx-activity-row small { display:block; color:var(--color-text-secondary);
  font-size:12px; margin-top:4px; }

/* Unified roster and pick shortlist styling. */
.fx-slot-row { display:flex; justify-content:space-between; align-items:center;
  gap:12px; background:var(--color-surface-raised); border:1px solid var(--color-border);
  padding:12px 16px; margin-bottom:7px; border-radius:10px; }
.fx-slot-name { display:inline-block; min-width:53px; border-radius:7px;
  padding:5px 8px; background:var(--color-accent-subtle);
  color:var(--color-accent); font-weight:700; font-size:12px; }
.fx-slot-player { flex:1; color:var(--color-text-primary); font-weight:500; font-size:14px; }
.fx-slot-empty { color:var(--color-accent); }
.fx-pick-needs { display:flex; flex-wrap:wrap; gap:7px; margin:8px 0 16px; }
.fx-pick-needs span { background:var(--color-accent-subtle); color:var(--color-accent);
  border-radius:999px; padding:6px 11px; font-size:12px; font-weight:600; }

/* AI Scout: one unmistakable call to action, scoped to its keyed Streamlit button. */
[class*="st-key-scout_research_"] button,
[class*="st-key-scout_research_"] button[kind="primary"] {
  width: 100% !important;
  min-height: 60px !important;
  padding: 16px 24px !important;
  justify-content: center !important;
  background: linear-gradient(110deg, #38B979 0%, #45D69A 65%, #29AA83 100%) !important;
  color: #071A14 !important;
  border: 1px solid #6EE7B7 !important;
  border-radius: 14px !important;
  font-size: 17px !important;
  font-weight: 800 !important;
  letter-spacing: .01em;
  box-shadow: 0 0 0 1px rgba(56,185,121,.16), 0 8px 26px rgba(56,185,121,.2) !important;
  transition: filter .18s ease, transform .18s ease, box-shadow .18s ease;
}
[class*="st-key-scout_research_"] button:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
  box-shadow: 0 9px 30px rgba(56,185,121,.36) !important;
}
[class*="st-key-scout_research_"] button:focus-visible {
  outline: 3px solid #C2F7DC !important;
  outline-offset: 3px;
}
[class*="st-key-scout_research_"] button [data-testid="stIconMaterial"],
[class*="st-key-scout_research_"] button p {
  color: #071A14 !important;
  font-weight: 800 !important;
}
.fx-scout-complete {
  margin: 10px 0 16px;
  padding: 13px 17px;
  border: 1px solid #45C98A;
  border-radius: 12px;
  background: rgba(56,185,121,.14);
  color: #A3F5CE;
  font-size: 14px;
  font-weight: 650;
  animation: fx-scout-dismiss 8s forwards;
}
@keyframes fx-scout-dismiss {
  0%, 78% { opacity: 1; max-height: 90px; padding-top: 13px; padding-bottom: 13px; margin-bottom: 16px; }
  100% { opacity: 0; max-height: 0; padding-top: 0; padding-bottom: 0; margin-bottom: 0; border-width: 0; overflow: hidden; visibility: hidden; }
}
@media (prefers-reduced-motion: reduce) {
  .fx-scout-complete { animation: none; }
}

/* Overview: compact summary and non-expiring AI Scout completion state. */
.fx-scout-finished {
  margin: 10px 0 14px;
  padding: 13px 16px;
  border: 1px solid rgba(56, 185, 121, .5);
  border-radius: 12px;
  background: rgba(56, 185, 121, .12);
  color: #A3F5CE;
  font-weight: 650;
  font-size: 14px;
}
.fx-overview-note {
  border-radius: 10px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 10px 14px;
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
/* Reference sidebar — wide, deliberately spacious product navigation.
   Maintain native Streamlit collapse control rather than a fake HTML button. */
section[data-testid="stSidebar"] {
  background: #0E1624 !important;
}
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
  background: #0E1624 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding: 28px 22px 32px !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] [data-testid="stImage"] img {
  width: 64px !important;
  height: 64px !important;
  object-fit: contain;
  border-radius: 14px;
}
section[data-testid="stSidebar"] .fx-wordmark {
  font-size: 26px;
  font-weight: 750;
  letter-spacing: -0.04em;
  line-height: 1.1;
}
section[data-testid="stSidebar"] .fx-connection-mini {
  background: rgba(37, 102, 76, .29);
  border: 1px solid rgba(67, 176, 122, .48);
  border-radius: 16px;
  margin: 22px 0 22px;
  padding: 18px 20px 19px;
}
section[data-testid="stSidebar"] .fx-status-pill {
  padding: 0;
  border-radius: 0;
  background: transparent;
  font-size: 13px;
  line-height: 1.4;
  color: #51D98E;
}
section[data-testid="stSidebar"] .fx-status-dot {
  width: 11px;
  height: 11px;
}
section[data-testid="stSidebar"] .fx-mini-league {
  margin-top: 12px;
  font-size: 20px;
  line-height: 1.25;
  font-weight: 700;
}
section[data-testid="stSidebar"] .fx-mini-helper {
  font-size: 13px;
  line-height: 1.5;
  margin-top: 6px;
  color: #ADB8C7;
}
section[data-testid="stSidebar"] .fx-conn-offline {
  border-color: var(--color-border);
  background: var(--color-surface);
}
section[data-testid="stSidebar"] .fx-nav-divider {
  margin: 22px 0 19px;
  background: #3A4759;
}
section[data-testid="stSidebar"] .fx-utility-divider {
  margin-top: 24px;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] {
  margin-bottom: 7px;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button {
  min-height: 50px !important;
  padding: 12px 17px !important;
  gap: 14px !important;
  font-size: 15px !important;
  border-radius: 11px !important;
  font-weight: 500 !important;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button [data-testid="stIconMaterial"] {
  font-size: 21px !important;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover {
  background: rgba(56, 185, 121, .11) !important;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:focus-visible {
  outline: 2px solid var(--color-accent) !important;
}
@media (max-width: 900px) {
  :root { --sidebar-w: min(336px, 88vw); }
  section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding: 22px 16px 26px !important;
  }
  section[data-testid="stSidebar"] [class*="st-key-nav_"] button {
    min-height: 46px !important;
    font-size: 14px !important;
  }
}

/* Verified expert coverage is separate from deterministic draft ranking. */
.fx-scout-expert-line {
  display: block;
  margin-top: 3px;
  font-size: 11px;
  line-height: 1.5;
  color: #79DDA7;
  font-weight: 650;
}

/* Stable stack for player text: avoids Streamlit caption/name overlap. */
[class*="st-key-ai_candidate_"] .fx-scout-copy {
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-start !important;
  justify-content: center !important;
  width: 100%;
  min-width: 0;
  gap: 5px !important;
  padding: 4px 1px !important;
  line-height: normal !important;
}
[class*="st-key-ai_candidate_"] .fx-scout-title-line {
  display: flex; align-items: baseline; flex-wrap: wrap; gap: 6px 10px;
  min-height: 22px; width: 100%; min-width: 0;
}
[class*="st-key-ai_candidate_"] .fx-scout-player-name {
  display: inline-block; color: #F1F9F5; font-size: 15px;
  font-weight: 760; line-height: 1.45; overflow-wrap: anywhere;
}
[class*="st-key-ai_candidate_"] .fx-scout-ai-label {
  color: #73E4AB; font-size: 10px; font-weight: 800; white-space: nowrap;
}
[class*="st-key-ai_candidate_"] .fx-scout-meta {
  display: block; color: #AFC0CD; font-size: 12px;
  line-height: 1.45; overflow-wrap: anywhere;
}
[class*="st-key-ai_candidate_"] .fx-scout-copy .fx-scout-one-liner {
  display: block; margin: 1px 0 0 !important; color: #E4F0E9;
  font-size: 12px; line-height: 1.5;
}
[class*="st-key-ai_candidate_"] .fx-scout-copy .fx-scout-bottom-line {
  display: flex; align-items: center; flex-wrap: wrap;
  gap: 6px 9px; margin: 1px 0 0 !important; line-height: 1.45;
}
[class*="st-key-ai_candidate_"] .fx-scout-wait-explanation {
  display: inline; color: #AFC0CD; font-size: 11px; line-height: 1.45;
}
@media (max-width: 760px) {
  [class*="st-key-ai_candidate_"] .fx-scout-copy { gap: 4px !important; }
  [class*="st-key-ai_candidate_"] .fx-scout-player-name { font-size: 13px; }
  [class*="st-key-ai_candidate_"] .fx-scout-meta { font-size: 11px; }
}

/* Center the monogram in its entire column and increase visual weight. */
.fx-scout-avatar-wrap {
  display: flex;
  width: 100%;
  min-height: 66px;
  justify-content: center;
  align-items: center;
}
.fx-scout-avatar-wrap .fx-scout-photo-fallback {
  width: 62px;
  height: 62px;
  border-radius: 15px;
  border: 1px solid rgba(102, 238, 164, .42);
  background: linear-gradient(145deg, #2D7351, #1D4F40);
  color: #B9FFDB;
  font-size: 21px;
  font-weight: 800;
  line-height: 1;
  box-shadow: 0 4px 14px rgba(10, 45, 28, .24);
}
/* Scope button style to the player modal triggers, leaving other buttons intact. */
[class*="st-key-scout_detail_"] button,
[class*="st-key-scout_detail_"] button[kind="secondary"] {
  width: 100% !important;
  min-height: 43px !important;
  padding: 9px 13px !important;
  border-radius: 11px !important;
  background: #39C889 !important;
  border: 1px solid #69E9AF !important;
  color: #09291D !important;
  font-weight: 800 !important;
  font-size: 13px !important;
  box-shadow: 0 3px 10px rgba(29, 137, 83, .16);
  transition: background .15s ease, box-shadow .15s ease, transform .15s ease;
}
[class*="st-key-scout_detail_"] button p,
[class*="st-key-scout_detail_"] button span,
[class*="st-key-scout_detail_"] button svg,
[class*="st-key-scout_detail_"] button [data-testid="stIconMaterial"] {
  color: #09291D !important;
  fill: none;
  font-weight: 800 !important;
  opacity: 1 !important;
}
[class*="st-key-scout_detail_"] button:hover {
  background: #66E5AA !important;
  border-color: #B0F6CE !important;
  box-shadow: 0 5px 16px rgba(29, 137, 83, .28) !important;
  transform: translateY(-1px);
}
[class*="st-key-scout_detail_"] button:focus-visible {
  outline: 3px solid #A7F3D0 !important;
  outline-offset: 3px;
}
@media (max-width: 760px) {
  .fx-scout-avatar-wrap { min-height: 50px; }
  .fx-scout-avatar-wrap .fx-scout-photo-fallback {
    width: 47px; height: 47px; font-size: 16px; border-radius: 11px;
  }
  [class*="st-key-scout_detail_"] button {
    min-height: 42px !important;
    padding: 7px 9px !important;
    font-size: 12px !important;
  }
}
@media (prefers-reduced-motion: reduce) {
  [class*="st-key-scout_detail_"] button { transition: none; }
}

/* Slightly roomier candidate comparisons, reliable monogram and responsive actions. */
[class*="st-key-ai_candidate_"] [data-testid="stVerticalBlockBorderWrapper"] {
  padding: 13px 14px !important;
}
[class*="st-key-ai_candidate_"] [data-testid="stCaptionContainer"] p {
  color: #AFC6D1 !important;
  font-size: 12px !important;
  line-height: 1.45 !important;
}
.fx-scout-photo-fallback {
  width: 52px; height: 52px; border-radius: 13px;
  border: 1px solid rgba(80,215,151,.25);
  background: linear-gradient(145deg,#245940,#193F36);
  color: #A4F3CD; font-size: 16px; letter-spacing: .03em;
  font-weight: 800; display: grid; place-items: center;
}
.fx-scout-one-liner { font-size: 13px; line-height: 1.4; margin: 4px 0 5px; }
.fx-scout-bottom-line { font-size: 12px; line-height: 1.4; gap: 9px; }
[class*="st-key-ai_candidate_"] button { min-height: 39px !important; font-weight: 650 !important; }
.fx-team-breakdown {
  display: grid; grid-template-columns: repeat(3,minmax(0,1fr));
  gap: 10px; width: 100%; margin: 12px 0 16px;
}
.fx-team-panel {
  background: #182B29; border: 1px solid rgba(60,166,108,.32);
  border-radius: 13px; padding: 14px; min-width: 0;
}
.fx-team-eyebrow {
  display: block; font-size: 11px; text-transform: uppercase;
  letter-spacing: .06em; color: #A0D7B7; font-weight: 750;
}
.fx-team-coverage {
  display: block; color: #EAFBF1; font-size: 27px; font-weight: 780;
  margin: 5px 0 11px; line-height: 1.1;
}
.fx-team-coverage small { font-size: 13px; color: #91AE9F; }
.fx-team-position-list {
  display: flex; flex-wrap: wrap; gap: 5px;
  align-items: center;
}
.fx-team-pos, .fx-team-chip, .fx-team-division {
  display: inline-flex; gap: 5px; align-items: center;
  padding: 5px 8px; border-radius: 8px; font-size: 11px;
  background: #24373A; color: #D3E3E1; border: 1px solid #37504A;
}
.fx-team-pos-filled { background: #25533A; border-color: #398B5A; color: #A2F2C7; }
.fx-team-pos-open { background: #273438; color: #AEB7C2; }
.fx-team-chip small, .fx-team-pos small { color: #77DFAA; font-weight: 700; }
.fx-team-footnote, .fx-team-empty {
  display: block; margin-top: 9px; font-size: 10px;
  line-height: 1.4; color: #9CACB4;
}
.fx-team-conferences { display: flex; gap: 8px; margin: 13px 0 11px; flex-wrap: wrap; }
.fx-team-stat {
  display: flex; gap: 5px; align-items: center; flex-wrap: wrap;
  background: #213A35; border-radius: 9px; padding: 7px 9px;
  font-size: 11px; color: #A4D9BF;
}
.fx-team-stat strong { color: #E9FCF3; }
.fx-team-division { padding: 4px 7px; }
.fx-team-division b { color: #7AE5AC; }
@media (max-width: 1150px) {
  .fx-team-breakdown { grid-template-columns: repeat(2,minmax(0,1fr)); }
  .fx-team-panel-wide { grid-column: 1 / -1; }
}
@media (max-width: 700px) {
  .fx-team-breakdown { grid-template-columns: minmax(0,1fr); }
  .fx-team-panel-wide { grid-column: auto; }
  .fx-scout-photo-fallback { width: 40px; height: 40px; font-size: 13px; }
  .fx-scout-one-liner { font-size: 12px; }
}

/* Compact AI Scout comparison: five rows visible without long page scrolling. */
[class*="st-key-ai_candidate_"] [data-testid="stVerticalBlockBorderWrapper"] {
  padding: 8px 12px !important;
  border-radius: 12px !important;
}
[class*="st-key-ai_candidate_"] [data-testid="stVerticalBlock"] {
  gap: 2px !important;
}
[class*="st-key-ai_candidate_"] [data-testid="stMarkdownContainer"] p,
[class*="st-key-ai_candidate_"] [data-testid="stCaptionContainer"] {
  margin: 0 !important;
  line-height: 1.25 !important;
}
[class*="st-key-ai_candidate_"] [data-testid="stCaptionContainer"] p {
  font-size: 11px !important;
}
[class*="st-key-ai_candidate_"] button {
  min-height: 36px !important;
  border-radius: 9px !important;
  font-size: 12px !important;
  padding: 6px 10px !important;
  white-space: nowrap;
}
.fx-scout-one-liner {
  font-size: 12px;
  line-height: 1.3;
  color: #E1EDE5;
  margin: 2px 0 3px;
  overflow-wrap: anywhere;
}
.fx-scout-bottom-line {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 7px;
  font-size: 11px;
  line-height: 1.3;
  color: #A1B3C1;
  margin-top: 4px;
}
.fx-scout-bottom-line .fx-wait-badge {
  font-size: 9px;
  line-height: 1.1;
  padding: 4px 7px;
  white-space: nowrap;
}
.fx-scout-photo {
  display: block;
  width: 45px;
  height: 45px;
  border-radius: 10px;
  object-fit: cover;
  background: #263B35;
  color: #7DE4AD;
  flex-shrink: 0;
}
.fx-scout-photo-fallback {
  display: grid;
  place-items: center;
  font-size: 20px;
}
div[data-testid="stDialog"] [role="dialog"] {
  animation: fx-scout-modal-enter 180ms ease-out both;
}
@keyframes fx-scout-modal-enter {
  from { opacity: 0; transform: translateY(10px) scale(.985); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@media (prefers-reduced-motion: reduce) {
  div[data-testid="stDialog"] [role="dialog"] { animation: none; }
}
@media (max-width: 760px) {
  [class*="st-key-ai_candidate_"] [data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
  }
  [class*="st-key-ai_candidate_"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex: 1 1 auto !important;
    width: auto !important;
    min-width: 0 !important;
  }
  [class*="st-key-ai_candidate_"] [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child {
    flex: 0 0 39px !important;
  }
  [class*="st-key-ai_candidate_"] [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child {
    flex: 0 0 100px !important;
  }
  .fx-scout-photo { width: 37px; height: 37px; }
  .fx-scout-one-liner { font-size: 11px; }
  .fx-scout-bottom-line { font-size: 10px; }
}

/* Picky AI Scout — highlighted recommendation and evidence-first decision cards. */
[class*="st-key-scout_recommended_preview"] [data-testid="stVerticalBlockBorderWrapper"],
[class*="st-key-scout_recommended"] [data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid rgba(56,185,121,.68) !important;
  border-radius: 15px !important;
  background: linear-gradient(125deg,rgba(29,78,55,.45),rgba(24,36,49,.76)) !important;
  box-shadow:0 10px 30px rgba(8,30,21,.16);
}
.fx-recommend-banner { display:flex; gap:10px; align-items:center; flex-wrap:wrap;
  color:#77E4A8; font-size:11px; font-weight:800; letter-spacing:.08em;
  text-transform:uppercase; margin:4px 0 6px; }
.fx-recommend-banner span { border-radius:7px; padding:5px 9px;
  color:#0B2418; background:#4CDB99; }
.fx-scout-signals {display:flex;align-items:center;flex-wrap:wrap;
  gap:12px;margin:10px 0 8px;}
.fx-wait-badge {font-size:10px;font-weight:800;letter-spacing:.045em;
  border:1px solid rgba(139,161,179,.4);border-radius:999px;padding:5px 9px;
  color:#BDC8D9;background:rgba(103,118,142,.14);}
.fx-wait-elevated {color:#FFD394;background:rgba(194,116,22,.16);border-color:rgba(217,149,63,.45)}
.fx-wait-moderate {color:#EBD09A;background:rgba(160,134,51,.13);border-color:rgba(202,168,78,.3)}
.fx-wait-lower {color:#87E5B3;background:rgba(29,130,82,.18);border-color:rgba(52,189,115,.37)}
.fx-wait-unknown {color:#B8C5D5}
@media (max-width: 760px) {
 .fx-recommend-banner,.fx-scout-signals {gap:7px}
 .fx-scout-heading {padding:12px}
 .fx-scout-heading strong {font-size:16px}
}

/* AI Scout high-contrast research identity and candidate explanation cards. */
.fx-scout-heading {
  display:flex; align-items:center; gap:13px;
  margin:24px 0 12px; padding:15px 19px; border-radius:14px;
  border:1px solid rgba(63,192,125,.63);
  background:linear-gradient(112deg,rgba(23,96,71,.52),rgba(20,41,40,.9));
  box-shadow:0 5px 26px rgba(12,42,32,.2);
}
.fx-scout-mark { display:grid; place-items:center; width:38px; height:38px;
  border-radius:10px; background:#37C985; color:#061A12; font-size:25px; font-weight:900; }
.fx-scout-heading > div { display:flex; flex-direction:column; min-width:0; gap:3px; }
.fx-scout-heading strong { color:#F1F5F9; font-size:18px; line-height:1.2; }
.fx-scout-heading small { font-size:11px; color:#A5EBC7; }
[class*="st-key-ai_candidate_"] {
  border:1px solid rgba(70,173,120,.34); border-radius:12px;
  background:rgba(24,44,39,.22);
}
[class*="st-key-ai_candidate_"] [data-testid="stVerticalBlockBorderWrapper"] {
  border-color:rgba(70,173,120,.3) !important;
}
[class*="st-key-ai_candidate_"]:hover {
  background:rgba(39,93,66,.25);
}
[class*="st-key-ai_candidate_"] [data-testid="stMarkdownContainer"] strong {
  color:#E6F8ED;
}

/* Fluid page geometry: works on smaller monitors, ultrawides and phones. */
:root { --sidebar-w: clamp(252px, 19vw, 326px); }
.block-container {
  width: min(100%, 1640px) !important;
  max-width: 1640px !important;
  padding-left: clamp(12px, 2.4vw, 36px) !important;
  padding-right: clamp(12px, 2.4vw, 36px) !important;
  margin-inline: auto !important;
  overflow-wrap: anywhere;
}
.fx-roster-layout {
  display:grid;
  grid-template-columns: minmax(0,2fr) minmax(244px,1fr);
  align-items:start;
  gap: clamp(12px, 1.3vw, 20px);
  width:100%;
  margin: 8px 0 12px;
}
.fx-roster-layout > section { min-width:0; }
.fx-roster-heading {
  color:#60DBA4; text-transform:uppercase; letter-spacing:.065em;
  font-size:11px; font-weight:750; margin-bottom:10px;
}
.fx-roster-starters {
  display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
  gap:8px;
}
.fx-roster-extras { display:grid; grid-template-columns:minmax(0,1fr); gap:8px; }
.fx-roster-player {
  min-width:0; display:flex; gap:10px; align-items:center;
  padding:10px 11px; min-height:70px;
  border-radius:11px; border:1px solid rgba(66,91,110,.55);
  background:#1C2533; color:#F1F5F9;
}
.fx-roster-player:hover { border-color:rgba(72,185,131,.48); }
.fx-roster-slot {
  display:grid; place-items:center; flex:0 0 auto;
  min-width:42px; min-height:40px; border-radius:8px;
  background:#263F36; color:#70E0A8; font-weight:700; font-size:12px;
}
.fx-roster-player-info { min-width:0; flex:1; display:flex; flex-direction:column; gap:2px; }
.fx-roster-player-info strong { font-size:clamp(12px, .87vw, 14px); line-height:1.35; font-weight:650; }
.fx-roster-player-info small {
  color:#A3B2C5; font-size:11px; line-height:1.4;
  overflow-wrap:anywhere;
}
.fx-roster-player-info .fx-roster-type { color:#60D39C; font-size:10px; letter-spacing:.04em; }
.fx-roster-pick { font-size:11px; color:#A8B5C6; white-space:nowrap; align-self:center; }
.fx-roster-empty { opacity:.75; background:#17202D; }
.fx-roster-empty .fx-roster-slot { background:#25313E; color:#B6C3CF; }
.fx-roster-note {
  background:#1C2533; padding:11px; font-size:12px; color:#A6B4C5;
  border-radius:10px; border:1px dashed #394558;
}
.fx-overview-scout [data-testid="stVerticalBlockBorderWrapper"] { min-width:0; }
.fx-scout-reason { color:#D0EADD; font-size:13px; line-height:1.48; }
.fx-scout-reason-label { color:#56D49A; font-weight:800; font-size:11px; text-transform:uppercase; letter-spacing:.07em; }
@media (max-width: 1250px) {
  .fx-roster-layout { grid-template-columns: minmax(0,1fr); }
  .fx-roster-extras { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
@media (max-width: 760px) {
  :root { --sidebar-w: min(300px, 86vw); }
  .block-container { padding-top:14px !important; padding-bottom:48px !important; }
  .fx-roster-layout { gap:12px; }
  .fx-roster-starters, .fx-roster-extras { grid-template-columns:1fr; }
  .fx-roster-player { min-height:60px; padding:8px 10px; gap:9px; }
  .fx-roster-slot { min-width:38px; min-height:38px; }
  .fx-roster-player-info strong { font-size:13px; }
  section[data-testid="stSidebar"] {
    min-width: min(300px,86vw) !important;
    max-width: min(300px,86vw) !important;
  }
  [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; }
  [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex:1 1 100% !important; width:100% !important; min-width:0 !important;
  }
  .stDataFrame, [data-testid="stDataFrame"] { width:100% !important; max-width:100%; overflow-x:auto; }
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
    """Display the shipped PNG icon; avoid Streamlit/Pillow SVG parsing."""
    logo_path = ICON_PATH
    brand_logo, brand_name = st.columns([0.24, 0.76], gap="small", vertical_alignment="center")
    with brand_logo:
        if logo_path.is_file():
            st.image(str(logo_path), width=64)
        else:
            # Keep navigation usable even if the image asset is missing.
            st.markdown("🎲")
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
