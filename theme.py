"""Fantasy draft themes — Washi & Sumi (light) / Midnight Shibuya (dark)."""

from __future__ import annotations

import streamlit as st

LIGHT = {
    "name": "Washi & Sumi",
    "bg": "#F4F1EA",
    "surface": "#E2DDD3",
    "surface_raised": "#FAF8F4",
    "ink": "#2B2B2B",
    "ink_muted": "#5C5852",
    "border": "#D4CFC4",
    "accent": "#D93829",
    "accent_soft": "rgba(217, 56, 41, 0.12)",
    "positive": "#2F6B52",
    "gold": "#B8860B",
    "sidebar": "#EDE8DF",
    "shadow": "0 10px 30px rgba(43, 43, 43, 0.08)",
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
    "shadow": "0 12px 36px rgba(0, 0, 0, 0.35)",
}


def init_theme() -> str:
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "light"
    return st.session_state.theme_mode


def set_theme(mode: str) -> None:
    st.session_state.theme_mode = "dark" if mode == "dark" else "light"


def palette(mode: str | None = None) -> dict[str, str]:
    mode = mode or st.session_state.get("theme_mode", "light")
    return DARK if mode == "dark" else LIGHT


def inject_css(mode: str | None = None) -> None:
    p = palette(mode)
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Sora:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

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
  --shadow: {p["shadow"]};
  --font-display: {"Fraunces" if (mode or st.session_state.get("theme_mode","light")) == "light" else "Sora"}, Georgia, serif;
  --font-body: {"IBM Plex Sans" if (mode or st.session_state.get("theme_mode","light")) == "light" else "Sora"}, system-ui, sans-serif;
}}

html, body, [data-testid="stAppViewContainer"], .stApp {{
  background: var(--bg) !important;
  color: var(--ink) !important;
  font-family: var(--font-body) !important;
}}

[data-testid="stHeader"] {{
  background: transparent !important;
}}

[data-testid="stSidebar"] {{
  background: var(--sidebar) !important;
  border-right: 1px solid var(--border) !important;
}}

[data-testid="stSidebar"] * {{
  color: var(--ink) !important;
}}

.block-container {{
  padding-top: 1.4rem !important;
  padding-bottom: 3rem !important;
  max-width: 1200px !important;
}}

h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
  font-family: var(--font-display) !important;
  color: var(--ink) !important;
  letter-spacing: -0.02em;
}}

p, span, label, .stCaption, [data-testid="stCaption"] {{
  color: var(--ink-muted) !important;
}}

.stMarkdown, .stText, .stDataFrame {{
  color: var(--ink) !important;
}}

div[data-testid="stMetric"] {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 0.85rem 1rem;
  box-shadow: var(--shadow);
}}

div[data-testid="stMetric"] label {{
  color: var(--ink-muted) !important;
}}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
  color: var(--ink) !important;
  font-family: var(--font-display) !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 18px !important;
  box-shadow: var(--shadow);
}}

.stTabs [data-baseweb="tab-list"] {{
  gap: 0.35rem;
  background: var(--surface);
  padding: 0.35rem;
  border-radius: 14px;
  border: 1px solid var(--border);
}}

.stTabs [data-baseweb="tab"] {{
  border-radius: 10px !important;
  color: var(--ink-muted) !important;
}}

.stTabs [aria-selected="true"] {{
  background: var(--accent-soft) !important;
  color: var(--ink) !important;
}}

.stButton > button {{
  background: var(--accent) !important;
  color: {"#F4F1EA" if (mode or st.session_state.get("theme_mode","light")) == "light" else "#121622"} !important;
  border: none !important;
  border-radius: 999px !important;
  font-weight: 600 !important;
  box-shadow: var(--shadow);
}}

.stButton > button:hover {{
  filter: brightness(1.05);
}}

.stDownloadButton > button {{
  background: var(--surface-raised) !important;
  color: var(--ink) !important;
  border: 1px solid var(--border) !important;
  border-radius: 999px !important;
}}

.stTextInput input, .stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div,
.stNumberInput input {{
  background: var(--surface-raised) !important;
  color: var(--ink) !important;
  border-radius: 12px !important;
  border-color: var(--border) !important;
}}

.stSlider [data-baseweb="slider"] div[role="slider"] {{
  background: var(--accent) !important;
}}

.stAlert {{
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
}}

.stDataFrame, [data-testid="stDataFrame"] {{
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  overflow: hidden;
}}

.fx-hero {{
  background:
    radial-gradient(1200px 280px at 10% -20%, var(--accent-soft), transparent 60%),
    linear-gradient(180deg, var(--surface-raised), var(--surface));
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 1.35rem 1.5rem 1.2rem;
  margin-bottom: 1.1rem;
  box-shadow: var(--shadow);
}}

.fx-kicker {{
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent) !important;
  margin-bottom: 0.45rem;
}}

.fx-hero h1 {{
  margin: 0 0 0.35rem 0 !important;
  font-size: clamp(1.7rem, 2.4vw, 2.35rem) !important;
  color: var(--ink) !important;
}}

.fx-hero p {{
  margin: 0 !important;
  color: var(--ink-muted) !important;
  max-width: 52rem;
}}

.fx-live {{
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: 0.9rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent) !important;
  font-size: 0.85rem;
  font-weight: 600;
}}

.fx-live-dot {{
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-soft);
  animation: pulse 1.6s ease-in-out infinite;
}}

@keyframes pulse {{
  0%, 100% {{ transform: scale(1); opacity: 1; }}
  50% {{ transform: scale(0.85); opacity: 0.7; }}
}}

.fx-rank {{
  display: inline-block;
  margin-left: 0.35rem;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--gold) 22%, transparent);
  color: var(--gold) !important;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}}

.fx-section-label {{
  font-family: var(--font-display);
  font-size: 1.15rem;
  margin: 0.4rem 0 0.75rem;
  color: var(--ink) !important;
}}

hr {{
  border-color: var(--border) !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_hero(*, title: str, subtitle: str, live: bool = False) -> None:
    live_html = (
        '<div class="fx-live"><span class="fx-live-dot"></span> Live draft feed</div>'
        if live
        else ""
    )
    st.markdown(
        f"""
<div class="fx-hero">
  <div class="fx-kicker">Fantasy draft board</div>
  <h1>{title}</h1>
  <p>{subtitle}</p>
  {live_html}
</div>
""",
        unsafe_allow_html=True,
    )
