"""Small app-wide visual refinements shared by Picky's non-Scout pages.

No changes to Sleeper polling, draft state, API use, or Streamlit widgets.
Use only CSS and existing Streamlit markup so other pages stay fully usable.
"""
from __future__ import annotations

import streamlit as st


def inject_page_css():
    st.markdown(
        """
<style>
/* Shared color and radius tokens extend theme.py's existing dark palette. */
:root {
  --color-accent: #3ccc8d;
  --color-accent-hover: #5bdea4;
  --color-accent-subtle: rgba(51,185,126,.15);
  --color-border: #304447;
  --picky-border-green: rgba(63,176,119,.36);
  --picky-soft-glow: 0 9px 26px rgba(6,34,24,.17);
}
/* Dimensional but restrained shell, without the fixed-width desktop gaps. */
html, body, [data-testid="stAppViewContainer"], .stApp {
  background-color:#10151f!important;
}
section[data-testid="stSidebar"] {
  background:#101b25!important;
  border-right:1px solid rgba(75,132,115,.23)!important;
}
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
  background:#101b25!important;
}
section[data-testid="stSidebar"] .fx-connection-mini {
  background:linear-gradient(128deg,rgba(28,82,60,.62),rgba(20,48,48,.82))!important;
  border:1px solid rgba(69,188,117,.51)!important;
  box-shadow:inset 0 1px rgba(117,230,173,.07),0 10px 26px rgba(6,23,18,.16)!important;
}
section[data-testid="stSidebar"] .fx-conn-offline {
  background:#182532!important;
  border-color:#33454d!important;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button {
  border-radius:11px!important;transition:background-color .18s ease,border-color .18s ease!important;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover {
  background:rgba(47,179,121,.16)!important;
  color:#f1fff7!important;
}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:focus-visible {
  outline:2px solid #65e3aa!important;outline-offset:3px!important;
}
/* Headers communicate the current page without huge empty spacing. */
.fx-page-header {
  padding:4px 0 10px;
  margin-bottom:17px!important;
  border-bottom:1px solid rgba(80,123,116,.22);
}
.fx-page-title {
  font-size:clamp(23px,2vw,29px)!important;
  color:#f3fff9!important;letter-spacing:-.04em!important;
}
.fx-page-sub {color:#a8bdc5!important;line-height:1.55!important;}
.fx-live-pill {
  background:rgba(45,168,104,.18)!important;
  border:1px solid rgba(67,188,115,.22)!important;
  color:#7be6ac!important;
}
/* Shared cards across My Team, Draft Board, Rankings, Reports & Settings. */
[class*="st-key-view_"] div[data-testid="stMetric"] {
  background:linear-gradient(125deg,#1a2c32,#1c2636)!important;
  border:1px solid rgba(87,149,123,.30)!important;
  border-radius:14px!important;
  padding:clamp(13px,1.3vw,19px)!important;
  box-shadow:var(--picky-soft-glow)!important;
  min-height:92px!important;
}
[class*="st-key-view_"] div[data-testid="stMetric"] label {
  color:#a1cabb!important;font-weight:700!important;
}
[class*="st-key-view_"] div[data-testid="stMetricValue"] {
  color:#f1fff8!important;font-size:clamp(20px,2vw,29px)!important;
  letter-spacing:-.025em;
}
[class*="st-key-view_"] [data-testid="stVerticalBlockBorderWrapper"] {
  border-color:rgba(86,139,123,.32)!important;
  border-radius:14px!important;
  background:#17232e!important;
  box-shadow:0 6px 20px rgba(5,14,21,.11)!important;
}
/* Existing Scout cards have their own higher-priority visual system. */
[class*="st-key-view_"] [class*="st-key-ai_candidate_"]
  [data-testid="stVerticalBlockBorderWrapper"] {
  background:transparent!important;border:0!important;box-shadow:none!important;
}
.fx-league-card,.fx-team-panel {
  border:1px solid rgba(73,161,111,.32)!important;
  background:linear-gradient(130deg,#182f2c,#1b2932)!important;
  border-radius:14px!important;
}
.fx-team-panel {box-shadow:var(--picky-soft-glow);}
.fx-roster-player {
  background:linear-gradient(128deg,#1c2b35,#1c2735)!important;
  border-color:rgba(92,146,126,.33)!important;
  transition:border-color .18s ease,background .18s ease;
}
.fx-roster-player:hover {border-color:rgba(69,208,136,.58)!important;}
.fx-slot-row {
  background:#1c2a33!important;border-color:rgba(85,144,121,.25)!important;
  border-radius:11px!important;
}
/* Tables retain their native accessibility, controls and horizontal scroll. */
[data-testid="stDataFrame"],.stDataFrame {
  border:1px solid rgba(81,135,124,.35)!important;
  border-radius:13px!important;
  background:#151f2b!important;
  box-shadow:0 6px 19px rgba(4,15,20,.14);
}
/* News and help content have visual separation without adding extra text. */
[class*="st-key-view_"] [data-testid="stExpander"] {
  border:1px solid rgba(82,127,125,.3)!important;
  border-radius:11px!important;
  background:#182431!important;
  overflow:hidden;
}
[class*="st-key-view_"] [data-testid="stExpander"] summary:hover {
  background:rgba(64,156,108,.10)!important;
}
[class*="st-key-view_"] a {color:#9bd6f5;}
[class*="st-key-view_"] a:hover {color:#b9e8ff;}
/* Settings inputs, dropdowns and uploads remain native interactive widgets. */
[data-testid="stFileUploader"] {
  border-radius:11px!important;overflow:hidden;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stSelectbox"] [role="combobox"]:focus-visible {
  outline:2px solid rgba(92,221,156,.62)!important;
  outline-offset:1px;
}
.stDownloadButton > button {
  border-radius:10px!important;
  background:linear-gradient(130deg,#233643,#1c2938)!important;
  border:1px solid rgba(88,138,123,.36)!important;
  color:#deeee7!important;
}
.stDownloadButton > button:hover {
  background:#304a50!important;border-color:rgba(112,213,154,.5)!important;
}
/* Page density adapts by viewport size rather than fixed monitor widths. */
@media (max-width:960px) {
  .fx-page-title {font-size:24px!important;}
  [class*="st-key-view_"] div[data-testid="stMetric"] {
    min-height:78px!important;padding:12px!important;
  }
}
@media (max-width:640px) {
  .fx-page-header {gap:9px!important;flex-wrap:wrap;}
  .fx-page-title {font-size:22px!important;}
  .fx-page-sub {font-size:12px!important;}
  .fx-team-panel {padding:12px!important;}
  .fx-league-card {padding:13px!important;}
  [class*="st-key-view_"] div[data-testid="stMetricValue"] {
    font-size:23px!important;
  }
}
@media (prefers-reduced-motion:reduce) {
  .fx-roster-player,section[data-testid="stSidebar"] [class*="st-key-nav_"] button {
    transition:none!important;
  }
}
</style>
""",
        unsafe_allow_html=True,
    )
