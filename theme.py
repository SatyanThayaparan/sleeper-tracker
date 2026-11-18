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

# Light = same indigo family; white surfaces on cooler ground so modules read clearly
LIGHT = {
    "bg": "#D8DEEC",
    "surface": "#FFFFFF",
    "surface_raised": "#F7F9FD",
    "ink": SHARED_INK_DARK,
    "ink_muted": "#3F4A66",
    "border": "#6E7C99",
    "accent": SHARED_ACCENT,
    "accent_soft": "rgba(120, 177, 89, 0.18)",
    "positive": "#2F6B3C",
    "gold": SHARED_GOLD,
    "sidebar": "#CDD5E8",
    "input_bg": "#FFFFFF",
    "shadow": "0 10px 28px rgba(18, 22, 34, 0.14)",
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
    border_w = "1.5px" if mode == "dark" else "2px"
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
  margin-bottom: 0.65rem !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] > div {{
  background: transparent !important;
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

/*
  Custom sun/moon theme pill (2×) in the first bordered sidebar module.
  Matches main-page container borders; left-aligned at the top.
*/
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.picky-theme-anchor) {{
  width: fit-content !important;
  max-width: 100% !important;
  margin: 0 0 0.85rem 0 !important;
  padding: 0.65rem 0.75rem !important;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.picky-theme-anchor) [data-testid="stMarkdown"] {{
  display: none !important;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.picky-theme-anchor) button {{
  position: relative !important;
  display: block !important;
  width: 152px !important;
  min-width: 152px !important;
  max-width: 152px !important;
  height: 64px !important;
  min-height: 64px !important;
  margin: 0 !important;
  padding: 0 !important;
  border-radius: 999px !important;
  border: none !important;
  box-shadow: none !important;
  font-size: 0 !important;
  color: transparent !important;
  overflow: hidden !important;
  transition: var(--theme-ease) !important;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.picky-theme-anchor.theme-light) button {{
  background: #E8ECF5 !important;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.picky-theme-anchor.theme-dark) button {{
  background: #0B0E16 !important;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.picky-theme-anchor) button::after {{
  content: "" !important;
  position: absolute !important;
  top: 6px !important;
  width: 70px !important;
  height: 52px !important;
  border-radius: 999px !important;
  transition: left 0.35s ease, right 0.35s ease, background-color 0.45s ease !important;
  z-index: 1 !important;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.picky-theme-anchor.theme-light) button::after {{
  left: 6px !important;
  right: auto !important;
  background: #B7C0D4 !important;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.picky-theme-anchor.theme-dark) button::after {{
  left: auto !important;
  right: 6px !important;
  background: #2A3148 !important;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.picky-theme-anchor) button::before {{
  content: "" !important;
  position: absolute !important;
  inset: 0 !important;
  z-index: 2 !important;
  pointer-events: none !important;
  background-repeat: no-repeat !important;
  background-position: 18px center, calc(100% - 18px) center !important;
  background-size: 26px 26px, 24px 24px !important;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.picky-theme-anchor.theme-light) button::before {{
  background-image:
    url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23121622' stroke-width='2' stroke-linecap='round'><circle cx='12' cy='12' r='4'/><path d='M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4'/></svg>"),
    url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%239AA3B8' stroke-width='2' stroke-linecap='round'><path d='M21 14.5A8.5 8.5 0 0 1 9.5 3 7 7 0 1 0 21 14.5z'/></svg>") !important;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.picky-theme-anchor.theme-dark) button::before {{
  background-image:
    url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236B7899' stroke-width='2' stroke-linecap='round'><circle cx='12' cy='12' r='4'/><path d='M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4'/></svg>"),
    url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23E8ECF5' stroke-width='2' stroke-linecap='round'><path d='M21 14.5A8.5 8.5 0 0 1 9.5 3 7 7 0 1 0 21 14.5z'/></svg>") !important;
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
    """2× sun/moon pill in a bordered module at the top-left of the sidebar."""
    mode = st.session_state.get("theme_mode", "dark")
    is_dark = mode == "dark"
    with st.container(border=True):
        st.markdown(
            f'<div class="picky-theme-anchor {"theme-dark" if is_dark else "theme-light"}" aria-hidden="true"></div>',
            unsafe_allow_html=True,
        )
        if st.button(
            "theme",
            key="picky_theme_btn",
            help="Switch light / dark theme",
            type="secondary",
        ):
            set_theme("light" if is_dark else "dark")
            st.rerun()


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
