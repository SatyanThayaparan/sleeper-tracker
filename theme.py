"""Sors themes — Light / Dark with shared Sora styling."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

APP_NAME = "Sors"
APP_TAGLINE = "Fantasy draft board · Lock-In redraft copilot"
ICON_PATH = Path(__file__).resolve().parent / "assets" / "sors-icon.jpg"

LIGHT = {
    "bg": "#F4F1EA",
    "surface": "#E8E2D8",
    "surface_raised": "#FFFcf7",
    "ink": "#2B2B2B",
    "ink_muted": "#5A564F",
    "border": "#BDB5A8",
    "accent": "#D93829",
    "accent_soft": "rgba(217, 56, 41, 0.14)",
    "positive": "#2F6B52",
    "gold": "#A67C00",
    "sidebar": "#E8E2D8",
    "input_bg": "#FFFcf7",
    "shadow": "0 8px 24px rgba(43, 43, 43, 0.08)",
}

DARK = {
    "bg": "#121622",
    "surface": "#1E2436",
    "surface_raised": "#2A3148",
    "ink": "#E8ECF5",
    "ink_muted": "#A7B0C5",
    "border": "#4A5573",
    "accent": "#78B159",
    "accent_soft": "rgba(120, 177, 89, 0.18)",
    "positive": "#78B159",
    "gold": "#D4AF37",
    "sidebar": "#161B2A",
    "input_bg": "#1A2032",
    "shadow": "0 10px 28px rgba(0, 0, 0, 0.4)",
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
    border_w = "1.5px" if mode == "dark" else "1px"
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
  --border-w: {border_w};
}}

html, body, [data-testid="stAppViewContainer"], .stApp {{
  background: var(--bg) !important;
  color: var(--ink) !important;
  font-family: var(--font) !important;
}}

[data-testid="stHeader"] {{
  background: transparent !important;
}}

/* Keep Material icon font intact (prevents "keyboard_double_arrow" text leak) */
[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"],
.material-icons,
.material-symbols-rounded {{
  font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
  font-style: normal !important;
  letter-spacing: normal !important;
  text-transform: none !important;
}}

section[data-testid="stSidebar"] {{
  background: var(--sidebar) !important;
  border-right: var(--border-w) solid var(--border) !important;
}}

section[data-testid="stSidebar"] > div:first-child {{
  background: var(--sidebar) !important;
}}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
  color: var(--ink) !important;
  font-family: var(--font) !important;
}}

section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
  color: var(--ink-muted) !important;
}}

/* Text inputs */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {{
  background-color: var(--input-bg) !important;
  color: var(--ink) !important;
  -webkit-text-fill-color: var(--ink) !important;
  caret-color: var(--ink) !important;
  border: var(--border-w) solid var(--border) !important;
  border-radius: 10px !important;
  box-shadow: none !important;
}}

section[data-testid="stSidebar"] [data-baseweb="base-input"],
section[data-testid="stSidebar"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
  background-color: var(--input-bg) !important;
  border-color: var(--border) !important;
  border-radius: 10px !important;
}}

section[data-testid="stSidebar"] [data-baseweb="base-input"] input::placeholder {{
  color: var(--ink-muted) !important;
  -webkit-text-fill-color: var(--ink-muted) !important;
  opacity: 0.9;
}}

/* File uploader — light touch so Browse button stays intact */
[data-testid="stFileUploaderDropzone"] {{
  background-color: var(--input-bg) !important;
  border: var(--border-w) dashed var(--border) !important;
  border-radius: 12px !important;
  color: var(--ink-muted) !important;
}}

[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span {{
  color: var(--ink-muted) !important;
  font-family: var(--font) !important;
}}

[data-testid="stFileUploaderDropzone"] button {{
  background: var(--surface-raised) !important;
  color: var(--ink) !important;
  border: var(--border-w) solid var(--border) !important;
  border-radius: 8px !important;
  font-family: var(--font) !important;
}}

.block-container {{
  padding-top: 1rem !important;
  padding-bottom: 2rem !important;
  padding-left: 1.25rem !important;
  padding-right: 1.25rem !important;
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

/* Modular cards */
div[data-testid="stMetric"] {{
  background: var(--surface) !important;
  border: var(--border-w) solid var(--border) !important;
  border-radius: 14px;
  padding: 0.75rem 0.9rem;
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
  border: var(--border-w) solid var(--border) !important;
  border-radius: 16px !important;
  box-shadow: var(--shadow);
}}

.stTabs [data-baseweb="tab-list"] {{
  gap: 0.3rem;
  background: var(--surface);
  padding: 0.35rem;
  border-radius: 12px;
  border: var(--border-w) solid var(--border);
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
  border: var(--border-w) solid var(--border) !important;
  border-radius: 999px !important;
  font-family: var(--font) !important;
}}

.stSlider [data-baseweb="slider"] div[role="slider"] {{
  background: var(--accent) !important;
}}

.stAlert {{
  border-radius: 12px !important;
  border: var(--border-w) solid var(--border) !important;
  background: var(--surface) !important;
}}

.stDataFrame, [data-testid="stDataFrame"] {{
  border: var(--border-w) solid var(--border) !important;
  border-radius: 12px !important;
  overflow: hidden;
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

.fx-hero-copy h1 {{
  margin: 0 0 0.2rem 0 !important;
  font-size: clamp(1.45rem, 2vw, 1.9rem) !important;
  color: var(--ink) !important;
  font-family: var(--font) !important;
}}

.fx-hero-copy p {{
  margin: 0 !important;
  color: var(--ink-muted) !important;
  font-size: 0.92rem;
}}

.fx-live {{
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.55rem;
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

.fx-panel {{
  background: var(--surface);
  border: var(--border-w) solid var(--border);
  border-radius: 16px;
  padding: 0.85rem 1rem;
  box-shadow: var(--shadow);
  margin-bottom: 0.75rem;
}}

/* Banner theme toggle — large swipe with palette gradient */
.fx-theme-slot div[data-testid="stToggle"] {{
  justify-content: flex-end;
}}

.fx-theme-slot label[data-baseweb="checkbox"] {{
  min-width: 64px !important;
  min-height: 36px !important;
  background: linear-gradient(90deg, #F4F1EA 0%, #D93829 45%, #121622 70%, #78B159 100%) !important;
  border: var(--border-w) solid var(--border) !important;
  border-radius: 999px !important;
  padding: 4px !important;
  transform: scale(1.25);
  transform-origin: right center;
}}

.fx-theme-slot label[data-baseweb="checkbox"] > div:first-child {{
  background: #FFFcf7 !important;
  width: 28px !important;
  height: 28px !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}}

.fx-theme-slot [data-testid="stWidgetLabel"] {{
  display: none !important;
}}

hr {{
  border-color: var(--border) !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_banner_theme_toggle() -> None:
    """Large gradient swipe toggle for the page banner (top-right)."""
    st.markdown('<div class="fx-theme-slot">', unsafe_allow_html=True)
    st.toggle(
        "Dark mode",
        value=st.session_state.theme_mode == "dark",
        key="sors_theme_toggle",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_hero(*, title: str, subtitle: str, live: bool = False) -> None:
    live_html = (
        '<div class="fx-live"><span class="fx-live-dot"></span> Live draft feed</div>'
        if live
        else ""
    )
    with st.container(border=True):
        left, mid, right = st.columns([0.07, 0.78, 0.15], vertical_alignment="center")
        with left:
            if ICON_PATH.is_file():
                st.image(str(ICON_PATH), width=58)
        with mid:
            st.markdown(
                f"""
<div class="fx-hero-copy">
  <div class="fx-kicker">Fantasy draft board</div>
  <h1>{title}</h1>
  <p>{subtitle}</p>
  {live_html}
</div>
""",
                unsafe_allow_html=True,
            )
        with right:
            render_banner_theme_toggle()
