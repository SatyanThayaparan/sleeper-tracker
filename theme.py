"""Hanko themes — Washi & Sumi (light) / Midnight Shibuya (dark), shared Sora styling."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

APP_NAME = "Hanko"
APP_TAGLINE = "Fantasy draft board · Lock-In redraft copilot"
ICON_PATH = Path(__file__).resolve().parent / "assets" / "hanko-icon.jpg"

LIGHT = {
    "name": "Washi & Sumi",
    "bg": "#F4F1EA",
    "surface": "#E8E2D8",
    "surface_raised": "#FFFcf7",
    "ink": "#2B2B2B",
    "ink_muted": "#5A564F",
    "border": "#CFC8BC",
    "accent": "#D93829",
    "accent_soft": "rgba(217, 56, 41, 0.14)",
    "positive": "#2F6B52",
    "gold": "#A67C00",
    "sidebar": "#EDE7DC",
    "input_bg": "#FFFcf7",
    "shadow": "0 8px 24px rgba(43, 43, 43, 0.07)",
}

DARK = {
    "name": "Midnight Shibuya",
    "bg": "#121622",
    "surface": "#1E2436",
    "surface_raised": "#262D42",
    "ink": "#E8ECF5",
    "ink_muted": "#9AA3B8",
    "border": "#2F374F",
    "accent": "#78B159",
    "accent_soft": "rgba(120, 177, 89, 0.16)",
    "positive": "#78B159",
    "gold": "#D4AF37",
    "sidebar": "#161B2A",
    "input_bg": "#1A2032",
    "shadow": "0 10px 28px rgba(0, 0, 0, 0.35)",
}


def init_theme() -> str:
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
    return st.session_state.theme_mode


def set_theme(mode: str) -> None:
    st.session_state.theme_mode = "dark" if mode == "dark" else "light"


def palette(mode: str | None = None) -> dict[str, str]:
    mode = mode or st.session_state.get("theme_mode", "dark")
    return DARK if mode == "dark" else LIGHT


def inject_css(mode: str | None = None) -> None:
    mode = mode or st.session_state.get("theme_mode", "dark")
    p = palette(mode)
    btn_fg = "#121622" if mode == "dark" else "#F4F1EA"
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&display=swap');

:root {{
  --bg: {p["bg"]};
  --surface: {p["surface"]};
  --surface-raised: {p["surface_raised"]};
  --ink: {p["ink"]};
  --ink-muted: {p["ink_muted"]};
  --border: {p["border"]};
  --accent: {p["accent"]};
  --accent-soft: {p["accent_soft"]};
  --positive: {p["positive"]};
  --gold: {p["gold"]};
  --sidebar: {p["sidebar"]};
  --input-bg: {p["input_bg"]};
  --shadow: {p["shadow"]};
  --font: "Sora", system-ui, sans-serif;
}}

html, body, [data-testid="stAppViewContainer"], .stApp {{
  background: var(--bg) !important;
  color: var(--ink) !important;
  font-family: var(--font) !important;
}}

[data-testid="stHeader"] {{
  background: transparent !important;
}}

section[data-testid="stSidebar"] {{
  background: var(--sidebar) !important;
  border-right: 1px solid var(--border) !important;
}}

section[data-testid="stSidebar"] > div {{
  background: var(--sidebar) !important;
}}

section[data-testid="stSidebar"] * {{
  font-family: var(--font) !important;
}}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] .stMarkdown {{
  color: var(--ink) !important;
}}

/* Inputs — force readable ink on raised fields */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {{
  background-color: var(--input-bg) !important;
  color: var(--ink) !important;
  -webkit-text-fill-color: var(--ink) !important;
  caret-color: var(--ink) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}}

section[data-testid="stSidebar"] [data-baseweb="base-input"],
section[data-testid="stSidebar"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
  background-color: var(--input-bg) !important;
  color: var(--ink) !important;
  border-color: var(--border) !important;
  border-radius: 12px !important;
}}

section[data-testid="stSidebar"] [data-baseweb="base-input"] input,
section[data-testid="stSidebar"] [data-baseweb="select"] span {{
  color: var(--ink) !important;
  -webkit-text-fill-color: var(--ink) !important;
}}

section[data-testid="stSidebar"] [data-baseweb="base-input"] input::placeholder {{
  color: var(--ink-muted) !important;
  -webkit-text-fill-color: var(--ink-muted) !important;
  opacity: 0.85;
}}

/* File uploader */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
  background: var(--input-bg) !important;
  border: 1px dashed var(--border) !important;
  color: var(--ink) !important;
}}

section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {{
  color: var(--ink-muted) !important;
}}

.block-container {{
  padding-top: 1rem !important;
  padding-bottom: 2rem !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
  max-width: 1600px !important;
}}

h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
  font-family: var(--font) !important;
  color: var(--ink) !important;
  letter-spacing: -0.02em;
  font-weight: 600 !important;
}}

p, label, .stCaption, [data-testid="stCaptionContainer"] {{
  color: var(--ink-muted) !important;
  font-family: var(--font) !important;
}}

.stMarkdown, .stText {{
  color: var(--ink) !important;
}}

div[data-testid="stMetric"] {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 0.7rem 0.85rem;
  box-shadow: var(--shadow);
}}

div[data-testid="stMetric"] label {{
  color: var(--ink-muted) !important;
}}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
  color: var(--ink) !important;
  font-family: var(--font) !important;
  font-size: 1.35rem !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 16px !important;
  box-shadow: var(--shadow);
}}

.stTabs [data-baseweb="tab-list"] {{
  gap: 0.3rem;
  background: var(--surface);
  padding: 0.3rem;
  border-radius: 12px;
  border: 1px solid var(--border);
}}

.stTabs [data-baseweb="tab"] {{
  border-radius: 9px !important;
  color: var(--ink-muted) !important;
  font-family: var(--font) !important;
}}

.stTabs [aria-selected="true"] {{
  background: var(--accent-soft) !important;
  color: var(--ink) !important;
}}

.stButton > button {{
  background: var(--accent) !important;
  color: {btn_fg} !important;
  border: none !important;
  border-radius: 999px !important;
  font-weight: 600 !important;
  font-family: var(--font) !important;
  box-shadow: var(--shadow);
}}

.stDownloadButton > button {{
  background: var(--surface-raised) !important;
  color: var(--ink) !important;
  border: 1px solid var(--border) !important;
  border-radius: 999px !important;
  font-family: var(--font) !important;
}}

.stSlider [data-baseweb="slider"] div[role="slider"] {{
  background: var(--accent) !important;
}}

.stAlert {{
  border-radius: 12px !important;
  border: 1px solid var(--border) !important;
}}

.stDataFrame, [data-testid="stDataFrame"] {{
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  overflow: hidden;
}}

/* Brand hero */
.fx-hero {{
  background:
    radial-gradient(900px 220px at 8% -30%, var(--accent-soft), transparent 55%),
    linear-gradient(180deg, var(--surface-raised), var(--surface));
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1rem 1.25rem 0.95rem;
  margin-bottom: 0.85rem;
  box-shadow: var(--shadow);
  display: flex;
  gap: 1rem;
  align-items: center;
}}

.fx-hero-icon {{
  width: 56px;
  height: 56px;
  border-radius: 14px;
  object-fit: cover;
  border: 1px solid var(--border);
  flex-shrink: 0;
}}

.fx-hero-copy {{
  min-width: 0;
}}

.fx-kicker {{
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--accent) !important;
  margin-bottom: 0.25rem;
}}

.fx-hero h1 {{
  margin: 0 0 0.2rem 0 !important;
  font-size: clamp(1.45rem, 2vw, 1.9rem) !important;
  color: var(--ink) !important;
  font-family: var(--font) !important;
}}

.fx-hero p {{
  margin: 0 !important;
  color: var(--ink-muted) !important;
  font-size: 0.92rem;
}}

.fx-live {{
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.65rem;
  padding: 0.28rem 0.65rem;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent) !important;
  font-size: 0.78rem;
  font-weight: 600;
}}

.fx-live-dot {{
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}}

.fx-rank {{
  display: inline-block;
  margin-left: 0.3rem;
  padding: 0.08rem 0.4rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--gold) 24%, transparent);
  color: var(--gold) !important;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}}

.fx-section-label {{
  font-family: var(--font);
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0.2rem 0 0.55rem;
  color: var(--ink) !important;
}}

/* Theme swipe toggle */
.fx-theme-wrap {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.35rem;
}}

.fx-theme-label {{
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--ink) !important;
}}

div[data-testid="stSidebar"] div[data-testid="stToggle"] {{
  justify-content: flex-end;
}}

div[data-testid="stSidebar"] label[data-baseweb="checkbox"] {{
  background: var(--input-bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: 999px !important;
  padding: 0.15rem !important;
}}

div[data-testid="stSidebar"] label[data-baseweb="checkbox"] > div:first-child {{
  background: var(--accent) !important;
}}

hr {{
  border-color: var(--border) !important;
}}

/* Tighten vertical rhythm */
[data-testid="stVerticalBlock"] > div {{
  gap: 0.55rem;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_theme_toggle() -> None:
    """Swipe-style theme toggle: off = Washi light, on = Midnight dark."""
    dark = st.toggle(
        "Midnight Shibuya",
        value=st.session_state.theme_mode == "dark",
        help="Off = Washi & Sumi (light) · On = Midnight Shibuya (dark)",
        key="hanko_theme_toggle",
    )
    set_theme("dark" if dark else "light")
    st.caption("Washi ↔ Midnight")


def render_hero(*, title: str, subtitle: str, live: bool = False) -> None:
    live_html = (
        '<div class="fx-live"><span class="fx-live-dot"></span> Live draft feed</div>'
        if live
        else ""
    )
    with st.container(border=True):
        left, right = st.columns([0.08, 0.92], vertical_alignment="center")
        with left:
            if ICON_PATH.is_file():
                st.image(str(ICON_PATH), width=64)
        with right:
            st.markdown(
                f"""
<div class="fx-hero-copy">
  <div class="fx-kicker">{APP_NAME} · fantasy draft</div>
  <h1>{title}</h1>
  <p>{subtitle}</p>
  {live_html}
</div>
""",
                unsafe_allow_html=True,
            )
