"""Picky themes — one indigo family, light and dark variants."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

APP_NAME = "Picky"
APP_TAGLINE = "Fantasy draft board · Lock-In redraft copilot"
ICON_PATH = Path(__file__).resolve().parent / "assets" / "picky-icon.jpg"

# Shared across both modes
SHARED_ACCENT = "#78B159"
SHARED_GOLD = "#D4AF37"
SHARED_INK_DARK = "#121622"
SHARED_INK_LIGHT = "#E8ECF5"

DARK = {
    "bg": "#121622",
    "surface": "#1E2436",
    "surface_raised": "#2A3148",
    "ink": SHARED_INK_LIGHT,
    "ink_muted": "#A7B0C5",
    "border": "#6B7899",
    "accent": SHARED_ACCENT,
    "accent_soft": "rgba(120, 177, 89, 0.18)",
    "positive": SHARED_ACCENT,
    "gold": SHARED_GOLD,
    "sidebar": "#0F131F",
    "input_bg": "#1A2032",
    "shadow": "0 10px 28px rgba(0, 0, 0, 0.45)",
}

# Light = same indigo family, inverted values (not a separate cream palette)
LIGHT = {
    "bg": "#EEF1F8",
    "surface": "#E0E5F0",
    "surface_raised": "#FFFFFF",
    "ink": SHARED_INK_DARK,
    "ink_muted": "#4A5573",
    "border": "#A8B2C9",
    "accent": SHARED_ACCENT,
    "accent_soft": "rgba(120, 177, 89, 0.16)",
    "positive": "#2F6B3C",
    "gold": SHARED_GOLD,
    "sidebar": "#E4E9F4",
    "input_bg": "#FFFFFF",
    "shadow": "0 8px 24px rgba(18, 22, 34, 0.08)",
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
    btn_fg = SHARED_INK_DARK if mode == "dark" else SHARED_INK_LIGHT
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
  --theme-ease: background-color 0.45s ease, color 0.45s ease,
                 border-color 0.45s ease, box-shadow 0.45s ease,
                 fill 0.45s ease;
}}

html, body, [data-testid="stAppViewContainer"], .stApp {{
  background: var(--bg) !important;
  color: var(--ink) !important;
  font-family: var(--font) !important;
  transition: var(--theme-ease) !important;
}}

[data-testid="stHeader"] {{
  background: transparent !important;
  transition: var(--theme-ease) !important;
}}

/* Keep Material icon font intact (prevents ligature text leaks) */
[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"],
.material-icons,
.material-symbols-rounded,
.material-symbols-outlined {{
  font-family: "Material Symbols Rounded", "Material Symbols Outlined",
    "Material Icons", sans-serif !important;
  font-style: normal !important;
  letter-spacing: normal !important;
  text-transform: none !important;
}}

/* Overlay sidebar — does not shift main content */
section[data-testid="stSidebar"] {{
  position: fixed !important;
  left: 0 !important;
  top: 0 !important;
  height: 100vh !important;
  z-index: 1000 !important;
  background: var(--sidebar) !important;
  border-right: var(--border-w) solid var(--border) !important;
  box-shadow: 8px 0 28px rgba(0, 0, 0, 0.28);
  transition: var(--theme-ease), transform 0.25s ease !important;
}}

section[data-testid="stSidebar"] > div:first-child,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
  background: var(--sidebar) !important;
  transition: var(--theme-ease) !important;
}}

/* Keep main stage full-width whether sidebar is open or closed */
section.main,
[data-testid="stAppViewContainer"] > .main,
div[data-testid="stAppViewContainer"] section.main {{
  margin-left: 0 !important;
  width: 100% !important;
  max-width: 100% !important;
}}

[data-testid="stSidebarCollapsedControl"] {{
  z-index: 1001 !important;
}}

section[data-testid="stSidebar"] [data-testid="stAlert"] {{
  background: var(--surface) !important;
  color: var(--ink) !important;
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
  transition: var(--theme-ease) !important;
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

/*
  File uploader — do NOT set font-family on inner spans
  (that turns Material "upload" ligatures into the word "upload").
*/
[data-testid="stFileUploader"] {{
  width: 100%;
}}

[data-testid="stFileUploaderDropzone"] {{
  background-color: var(--input-bg) !important;
  border: var(--border-w) dashed var(--border) !important;
  border-radius: 12px !important;
  color: var(--ink-muted) !important;
  transition: var(--theme-ease) !important;
}}

[data-testid="stFileUploaderDropzone"] > div {{
  color: var(--ink-muted) !important;
}}

[data-testid="stFileUploaderDropzone"] small {{
  color: var(--ink-muted) !important;
  font-family: var(--font) !important;
}}

[data-testid="stFileUploaderDropzone"] button {{
  background: var(--surface-raised) !important;
  color: var(--ink) !important;
  border: var(--border-w) solid var(--border) !important;
  border-radius: 8px !important;
}}

[data-testid="stFileUploaderDropzone"] button [data-testid="stIconMaterial"],
[data-testid="stFileUploaderDropzone"] button .material-icons,
[data-testid="stFileUploaderDropzone"] button .material-symbols-rounded,
[data-testid="stFileUploaderDropzone"] button .material-symbols-outlined {{
  font-family: "Material Symbols Rounded", "Material Symbols Outlined",
    "Material Icons", sans-serif !important;
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
  transition: var(--theme-ease) !important;
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
  transition: var(--theme-ease) !important;
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
  transition: var(--theme-ease) !important;
}}

.stTabs [data-baseweb="tab-list"] {{
  gap: 0.3rem;
  background: var(--surface);
  padding: 0.35rem;
  border-radius: 12px;
  border: var(--border-w) solid var(--border);
  transition: var(--theme-ease) !important;
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
  transition: var(--theme-ease) !important;
}}

.stDownloadButton > button {{
  background: var(--surface-raised) !important;
  color: var(--ink) !important;
  border: var(--border-w) solid var(--border) !important;
  border-radius: 999px !important;
  font-family: var(--font) !important;
  transition: var(--theme-ease) !important;
}}

.stSlider [data-baseweb="slider"] div[role="slider"] {{
  background: var(--accent) !important;
}}

.stAlert {{
  border-radius: 12px !important;
  border: var(--border-w) solid var(--border) !important;
  background: var(--surface) !important;
  transition: var(--theme-ease) !important;
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
  transition: var(--theme-ease);
}}

/* Sidebar theme toggle — oversized, hard to miss */
.fx-theme-label {{
  font-family: var(--font);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent) !important;
  margin: 0 0 0.35rem 0;
}}

.fx-theme-hint {{
  font-family: var(--font);
  font-size: 0.8rem;
  color: var(--ink-muted) !important;
  margin: 0.45rem 0 0 0;
}}

section[data-testid="stSidebar"] div[data-testid="stToggle"] {{
  justify-content: stretch;
  width: 100%;
}}

section[data-testid="stSidebar"] label[data-baseweb="checkbox"] {{
  width: 100% !important;
  min-width: 100% !important;
  min-height: 56px !important;
  background: linear-gradient(90deg, #EEF1F8 0%, #78B159 35%, #121622 68%, #D4AF37 100%) !important;
  border: 2px solid var(--accent) !important;
  border-radius: 999px !important;
  padding: 7px !important;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.14), 0 8px 22px rgba(0,0,0,0.28);
}}

section[data-testid="stSidebar"] label[data-baseweb="checkbox"] > div:first-child {{
  background: #FFFFFF !important;
  width: 42px !important;
  height: 42px !important;
  box-shadow: 0 3px 12px rgba(0,0,0,0.35);
}}

section[data-testid="stSidebar"] div[data-testid="stToggle"] [data-testid="stWidgetLabel"] {{
  display: none !important;
}}

hr {{
  border-color: var(--border) !important;
  transition: var(--theme-ease) !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_sidebar_theme_toggle() -> None:
    """Oversized gradient swipe toggle at the top of the sidebar."""
    mode = st.session_state.get("theme_mode", "dark")
    hint = "Dark mode on" if mode == "dark" else "Light mode on"
    with st.container(border=True):
        st.markdown('<p class="fx-theme-label">Theme</p>', unsafe_allow_html=True)
        st.toggle(
            "Dark mode",
            value=mode == "dark",
            key="picky_theme_toggle",
            label_visibility="collapsed",
        )
        st.markdown(
            f'<p class="fx-theme-hint">{hint} · swipe to switch</p>',
            unsafe_allow_html=True,
        )


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
                st.image(str(ICON_PATH), width=58)
        with right:
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
