import re
from html import escape as escape_html
from datetime import datetime, timezone
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st
import feedparser

from adp import ADP_URL, fetch_adp_rows, match_adp
from recommend import build_recommendations
from ai import openai_configured
from theme import (
    APP_NAME,
    APP_TAGLINE,
    ICON_PATH,
    NAV_PAGES,
    UTIL_PAGES,
    inject_css,
    render_connection_card,
    render_page_header,
    render_sidebar_brand,
)

API = "https://api.sleeper.app/v1"
_page_icon = str(ICON_PATH) if ICON_PATH.is_file() else "🏀"
st.set_page_config(
    page_title=f"{APP_NAME} · Draft Board",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

DEFAULT_DRAFT_ID = "1416933113287770112"
DEFAULT_DRAFT_URL = "https://sleeper.com/draft/nba/1416933113287770112?ftue=commish"

if "page" not in st.session_state:
    st.session_state.page = "overview"
if "cfg_draft_link" not in st.session_state:
    st.session_state.cfg_draft_link = DEFAULT_DRAFT_URL
if "cfg_league_id" not in st.session_state:
    st.session_state.cfg_league_id = ""
if "cfg_my_user" not in st.session_state:
    st.session_state.cfg_my_user = ""
if "cfg_refresh" not in st.session_state:
    st.session_state.cfg_refresh = 15
if "cfg_upside" not in st.session_state:
    st.session_state.cfg_upside = 35
if "cfg_safety" not in st.session_state:
    st.session_state.cfg_safety = 20
if "cfg_risk" not in st.session_state:
    st.session_state.cfg_risk = 15
if "cfg_fit" not in st.session_state:
    st.session_state.cfg_fit = 15


def draft_id_from_link(value):
    value = str(value or "").strip()
    m = re.search(r"(?:/draft/(?:nba/)?|^)(\d{12,22})(?:\b|$)", value)
    return m.group(1) if m else ""


@st.cache_data(ttl=25, show_spinner=False)
def api_get(path):
    r = requests.get(
        f"{API}/{path}",
        timeout=12,
        headers={"User-Agent": "SleeperNBADraftCopilot/1.0 personal use"},
    )
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=10, show_spinner=False)
def live_draft_snapshot(draft_id):
    """Refresh live draft endpoints without clearing unrelated cached data."""
    def fetch(path):
        response = requests.get(
            f"{API}/{path}",
            timeout=12,
            headers={"User-Agent": "SleeperNBADraftCopilot/1.0 personal use"},
        )
        response.raise_for_status()
        return response.json()

    safe_id = quote(str(draft_id), safe="")
    return (
        fetch(f"draft/{safe_id}/picks"),
        fetch(f"draft/{safe_id}"),
    )


@st.cache_data(ttl=86400, show_spinner=False)
def player_map():
    return api_get("players/nba")


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def cached_adp_rows():
    return fetch_adp_rows()


@st.cache_data(ttl=600, show_spinner=False)
def news_feed():
    entries = []
    for url, source in [
        ("https://www.espn.com/espn/rss/nba/news", "ESPN NBA"),
        (
            "https://news.google.com/rss/search?q=NBA%20fantasy%20basketball%20injury&hl=en-US&gl=US&ceid=US:en",
            "Google News search",
        ),
    ]:
        try:
            f = feedparser.parse(
                requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}).content
            )
            for e in f.entries[:35]:
                entries.append(
                    {
                        "title": e.get("title", ""),
                        "link": e.get("link", ""),
                        "source": source,
                        "published": e.get("published", ""),
                    }
                )
        except Exception:
            pass
    return entries


def normalize(s):
    return re.sub(r"[^a-z0-9 ]", "", str(s).lower()).strip()


def player_name(pid, players, picks):
    meta = players.get(str(pid), {})
    if meta:
        return (
            meta.get("full_name")
            or " ".join(filter(None, [meta.get("first_name"), meta.get("last_name")]))
            or str(pid)
        )
    for p in picks:
        if str(p.get("player_id")) == str(pid):
            m = p.get("metadata") or {}
            return (
                m.get("name")
                or " ".join(filter(None, [m.get("first_name"), m.get("last_name")]))
                or str(pid)
            )
    return str(pid)


def normalize_rankings(df, players):
    cols = {normalize(c).replace(" ", "_"): c for c in df.columns}
    if "player_id" not in cols and "player" not in cols and "name" not in cols:
        raise ValueError("CSV must contain player_id OR player/name column.")
    if not any(c in cols for c in ("projected_points", "projected_fppg", "fppg", "rank")):
        raise ValueError(
            "CSV must contain projected_fppg, projected_points, fppg, or rank column."
        )
    if "player_id" in cols:
        df["player_id"] = (
            df[cols["player_id"]].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
        )
    else:
        name_col = cols.get("player", cols.get("name"))
        lookup = {
            normalize(
                v.get("full_name")
                or " ".join(filter(None, [v.get("first_name"), v.get("last_name")]))
            ): str(k)
            for k, v in players.items()
            if isinstance(v, dict)
        }
        df["player_id"] = df[name_col].map(lambda n: lookup.get(normalize(n), ""))
    stat_col = next((c for c in ("projected_fppg", "fppg", "projected_points") if c in cols), None)
    if stat_col:
        df["base"] = pd.to_numeric(df[cols[stat_col]], errors="coerce")
        df["metric_label"] = (
            "Projected fantasy points per game"
            if stat_col != "projected_points"
            else "Imported projected points (check units)"
        )
    else:
        rank = pd.to_numeric(df[cols["rank"]], errors="coerce")
        df["base"] = 1000 - rank
        df["metric_label"] = "Rank proxy (not points)"
    for name in ("upside_fppg", "floor_fppg", "games_per_week", "availability_pct"):
        df[name] = pd.to_numeric(df[cols[name]], errors="coerce") if name in cols else float("nan")
    return df[df.player_id.ne("") & df.base.notna()].drop_duplicates("player_id").copy()


def player_positions(meta):
    return meta.get("fantasy_positions") or ([meta.get("position")] if meta.get("position") else [])


def adp_line(row):
    if not row or row.get("blend_adp") is None:
        return ""
    parts = [f"Blend {row['blend_adp']:.1f}"]
    for label, key in (("ESPN", "espn_adp"), ("Yahoo", "yahoo_adp"), ("Fantrax", "fantrax_adp")):
        if row.get(key) is not None:
            parts.append(f"{label} {row[key]:.1f}")
    return " · ".join(parts)


def projection_value(row, origin):
    if origin == "adp" and row.get("blend_adp") is not None:
        return f"{row['blend_adp']:.1f}"
    if origin == "projection" and row.get("score") is not None:
        return f"{float(row['score']):.1f}"
    if row.get("baseline") is not None:
        return str(row["baseline"])
    return "—"


def render_references(row):
    for hit in (row.get("hits") or [])[:2]:
        if hit.get("link"):
            st.markdown(
                f'- [{hit["title"]}]({hit["link"]}) — {hit.get("source") or "News"} · {hit["tone"]}'
            )
    query = quote(f"{row['player']} NBA")
    st.markdown(f"- [ESPN search](https://www.espn.com/search/_/q/{query})")
    st.markdown(f"- [Google News](https://news.google.com/search?q={query}%20injury)")
    if row.get("adp_url"):
        st.markdown(f'- [Hashtag Basketball ADP page]({row["adp_url"]})')


def render_pick_card(title, row, empty_text, *, badge: str | None = None, badge_class="fx-badge-value"):
    with st.container(border=True):
        if badge:
            st.markdown(
                f'<div class="fx-settings-title">{title}'
                f'<span class="fx-badge {badge_class}">{badge}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f'<div class="fx-settings-title">{title}</div>', unsafe_allow_html=True)
        if not row:
            st.caption(empty_text)
            return
        position = row["position"] or "Position unavailable"
        team = row["team"] or "Free agent"
        st.markdown(f'**{row["player"]}**')
        st.caption(f"{position} · {team} · Injury: {row['injury']}")
        line = adp_line(row)
        if line:
            st.caption(line)
        for reason in (row.get("reasons") or [])[:3]:
            st.markdown(f"- {reason}")
        with st.expander("Links & reports", expanded=False):
            render_references(row)


def render_top_recommendations(options, origin):
    """Show the existing one-per-position suggestions in a readable grid."""
    with st.container(border=True):
        st.markdown(
            '<div class="fx-section-head"><h2 class="fx-section-title">'
            '✦ Recommendations</h2></div>',
            unsafe_allow_html=True,
        )
        if not options:
            st.caption("No best options yet.")
            return
        if any(row.get("role_have") for row in options):
            st.caption("One player per role, prioritizing positions you have filled least.")
        else:
            st.caption(
                "One player at each position for variety. "
                "Select your account in Settings for roster-aware order."
            )
        metric_heading = "Blend ADP (lower is earlier)" if origin == "adp" else (
            "Projection score" if origin == "projection" else "Baseline rank"
        )
        header = (
            '<div class="fx-rec-head" aria-hidden="true">'
            '<span>#</span><span>Player</span><span>Position</span>'
            '<span>Team</span><span>' + escape_html(metric_heading) + '</span></div>'
        )
        rows_html = []
        for index, row in enumerate(options, 1):
            position = escape_html(str(row.get("position") or "—"))
            team = escape_html(str(row.get("team") or "FA"))
            name = escape_html(str(row.get("player") or "Unknown player"))
            score = escape_html(str(projection_value(row, origin)))
            top = " top" if index == 1 else ""
            rows_html.append(
                f'<div class="fx-rec-row{top}">'
                f'<span class="fx-rec-rank">{index}</span>'
                f'<span class="fx-rec-name">{name}</span>'
                f'<span class="fx-rec-position"><span class="fx-pos">{position}</span></span>'
                f'<span class="fx-rec-team">{team}</span>'
                f'<span class="fx-rec-score">{score}</span>'
                '</div>'
            )
        st.markdown('<div class="fx-rec-table">' + header + "".join(rows_html) + '</div>',
                    unsafe_allow_html=True)


def render_settings_form(league_id_hint: str = ""):
    render_page_header(
        title="Settings & Connections",
        subtitle="Set up Picky in a few steps. Recommended defaults work for beginners.",
        live=False,
    )
    with st.container(border=True):
        st.markdown("### 1. Connect your Sleeper draft")
        st.caption("Paste your Sleeper draft link to load the league and picks. No password needed.")
        st.text_input("Sleeper draft link or ID", key="cfg_draft_link",
                      help="Copy your draft URL directly from Sleeper.")
        st.text_input("Sleeper username or user ID (optional)", key="cfg_my_user",
                      help="Helps Picky account for players already on your roster.")
        with st.expander("Additional connection options"):
            st.text_input("League ID override (usually automatic)", key="cfg_league_id",
                          placeholder="Optional override")
            st.select_slider("Check for picks every", options=[10, 15, 30, 60],
                             key="cfg_refresh", format_func=lambda x: f"{x} sec")
    with st.container(border=True):
        st.markdown("### 2. Choose your rankings source")
        st.caption("Picky uses an ADP blend automatically. Optionally upload your own projections.")
        with st.expander("Custom projections (optional)"):
            st.file_uploader("Player rankings or projections CSV", type=["csv"], key="cfg_upload")
            st.download_button(
                "Download Lock-In projection template",
                data="player,projected_fppg,upside_fppg,floor_fppg,games_per_week,availability_pct\\n",
                file_name="lockin_projection_template.csv", mime="text/csv",
            )
            st.caption("Optional columns: upside_fppg, floor_fppg, games_per_week, availability_pct.")
    with st.container(border=True):
        st.markdown("### 3. Recommendation preferences")
        st.caption("Balanced (recommended): keep the current default weighting for upside, "
                   "consistency, injury risk, and roster needs.")
        with st.expander("Advanced ranking preferences"):
            st.slider("Lock-In upside emphasis (%)", 0, 80, key="cfg_upside", step=5,
                      help="Increase to emphasize potential big scoring performances.")
            st.slider("Consistency / floor emphasis (%)", 0, 60, key="cfg_safety", step=5,
                      help="Increase to favor consistent results.")
            st.slider("Injury status penalty (%)", 0, 50, key="cfg_risk", step=5,
                      help="Increase to weigh injury concerns more heavily.")
            st.slider("Open lineup fit bonus (%)", 0, 25, key="cfg_fit", step=1,
                      help="Increase to prioritize players who fill open starting positions.")
        st.caption("An uploaded CSV replaces the ADP baseline.")
    with st.expander("Developer options: OpenAI"):
        if openai_configured():
            st.success("API key loaded from secrets.")
        else:
            st.info("Optional: add OPENAI_API_KEY in local or Streamlit Cloud secrets.")
        st.caption("Never commit an API key to Git.")
    return st.session_state.get("cfg_upload")


def render_help():
    render_page_header(
        title="Help & Getting Started",
        subtitle="Learn what Picky does and understand common fantasy draft terms.",
        live=False,
    )
    with st.container(border=True):
        st.markdown("### Get started in three steps")
        st.markdown(
            "**1. Connect your draft** — enter its Sleeper URL in Settings & Connections.\n\n"
            "**2. Choose your fantasy team** — add your Sleeper username to improve roster fit.\n\n"
            "**3. Explore recommendations** — check Overview, Rankings and Draft Board."
        )
        st.info("Picky is an advisory tool. Make your actual draft picks in Sleeper.")
    st.markdown("### Fantasy terms, explained")
    terms = [
        ("What is ADP?", "Average Draft Position: when a player is typically selected. Lower ADP means earlier."),
        ("What is Lock-In scoring?", "A Sleeper format where eligible game performances can be locked in under your league rules."),
        ("What is a sleeper pick?", "A player who may offer better value than their typical draft position suggests."),
        ("What is a fade?", "A player to approach with caution based on available ranking, injury or news information."),
        ("What is roster fit?", "How a player matches the starting positions your team still needs."),
        ("What are projections?", "Estimates of future production that can be imported to customize ranking."),
    ]
    for title, detail in terms:
        with st.expander(title):
            st.write(detail)
    with st.container(border=True):
        st.markdown("### What each page shows")
        st.markdown(
            "**Overview:** your draft snapshot and recommendations.\n\n"
            "**Draft Board:** recent selections and full pick history.\n\n"
            "**Player Rankings:** available players, ADP, projection values and filters.\n\n"
            "**Reports & News:** articles that may be relevant to fantasy decisions.\n\n"
            "**Settings:** draft connection and optional ranking preferences."
        )
        st.caption("Sources: Sleeper API, Hashtag Basketball ADP, ESPN and Google News.")


draft_link = st.session_state.cfg_draft_link
draft_id_override = draft_id_from_link(draft_link)
league_id = (st.session_state.cfg_league_id or "").strip()
my_user = (st.session_state.cfg_my_user or "").strip()
refresh = int(st.session_state.cfg_refresh)
upside_weight = int(st.session_state.cfg_upside)
safety_weight = int(st.session_state.cfg_safety)
risk_weight = int(st.session_state.cfg_risk)
fit_bonus = int(st.session_state.cfg_fit)
uploaded = st.session_state.get("cfg_upload")
_preview_connected = bool(draft_id_override or league_id)

# --- Sidebar shell ---
with st.sidebar:
    render_sidebar_brand()
    render_connection_card(
        connected=_preview_connected,
        league_name=st.session_state.get("sidebar_league_name", "Configured draft") if _preview_connected else "",
        meta="Manage under Settings" if _preview_connected else "Open Settings to connect",
    )
    nav_icons = {
        "overview": ":material/home:",
        "board": ":material/view_module:",
        "players": ":material/bar_chart:",
        "reports": ":material/article:",
        "settings": ":material/settings:",
        "help": ":material/help_outline:",
    }

    def select_page(destination):
        st.session_state.page = destination

    st.markdown('<div class="fx-nav-divider"></div>', unsafe_allow_html=True)
    for destination, label in NAV_PAGES:
        with st.container(key=f"nav_{destination}"):
            st.button(
                label, icon=nav_icons[destination],
                key=f"nav_button_{destination}", use_container_width=True,
                on_click=select_page, args=(destination,),
                type="secondary",
            )

    st.markdown('<div class="fx-nav-divider fx-utility-divider"></div>', unsafe_allow_html=True)
    for destination, label in UTIL_PAGES:
        with st.container(key=f"nav_{destination}"):
            st.button(
                label, icon=nav_icons[destination],
                key=f"nav_button_{destination}", use_container_width=True,
                on_click=select_page, args=(destination,),
                type="secondary",
            )
    active_page = st.session_state.page
    st.markdown(
        f'<style>section[data-testid="stSidebar"] .st-key-nav_{active_page} '
        'button {background: var(--color-accent-subtle) !important;'
        ' color: var(--color-text-primary) !important; font-weight: 600 !important;}'
        f' section[data-testid="stSidebar"] .st-key-nav_{active_page} '
        'button [data-testid="stIconMaterial"] {color: var(--color-accent) !important;}'
        '</style>',
        unsafe_allow_html=True,
    )

page = st.session_state.page

if page == "help":
    render_help()
    st.stop()

if page == "settings":
    uploaded = render_settings_form()

if not league_id and not draft_id_override:
    if page != "settings":
        render_page_header(title="Draft Overview", subtitle=APP_TAGLINE, live=False)
        st.info(
            "Connect a Sleeper draft in **Settings & Connections** to load live recommendations."
        )
    st.stop()

try:
    if draft_id_override:
        draft = api_get(f"draft/{quote(draft_id_override)}")
        draft_id = str(draft.get("draft_id") or draft_id_override)
        meta = draft.get("metadata") or {}
        discovered_league_id = str(draft.get("league_id") or meta.get("league_id") or "")
        league_id = discovered_league_id or league_id
        if not discovered_league_id and page == "settings":
            st.warning(
                "Draft loaded but league ID was not provided; some scoring/roster information may be unavailable."
            )
    else:
        drafts = api_get(f"league/{quote(league_id)}/drafts")
        if not drafts:
            st.error("No draft found for this league. Enter the draft link directly.")
            st.stop()
        draft_id = str(drafts[0]["draft_id"])
        draft = api_get(f"draft/{quote(draft_id)}")
    league = api_get(f"league/{quote(league_id)}") if league_id else {}
    if draft.get("sport") and draft["sport"] != "nba":
        st.error(f'This is a {draft["sport"]} draft, not an NBA draft.')
        st.stop()
except Exception as e:
    st.error(f"Cannot connect to Sleeper draft {draft_id_override or league_id}: {e}")
    st.info("Check that the draft is publicly accessible, then retry in Settings.")
    st.stop()

if page == "settings":
    st.success(f"Connected to draft `{draft_id}`.")
    with st.expander("Scoring rules from your Sleeper league"):
        st.json(
            {
                "scoring_settings": league.get("scoring_settings") or {},
                "roster_positions": league.get("roster_positions") or [],
                "draft_settings": draft.get("settings") or {},
            }
        )
    # Team picker lives in settings when league users are available
    if league_id and not my_user:
        try:
            users = api_get(f"league/{quote(league_id)}/users")
            options = {
                f"{u.get('display_name') or u.get('username') or u.get('user_id')} ({u.get('username') or u.get('user_id')})": str(
                    u["user_id"]
                )
                for u in users
                if u.get("user_id")
            }
            if options:
                selected = st.selectbox(
                    "Select your team / Sleeper account",
                    ["Not selected"] + list(options),
                    key="cfg_team_select",
                )
                st.session_state.cfg_team_id = options.get(selected, "")
        except Exception as e:
            st.caption(f"League user lookup unavailable: {e}")
    st.stop()

try:
    players = player_map()
    if not isinstance(players, dict):
        players = {}
except Exception as e:
    players = {}
    st.warning(
        f"NBA player directory unavailable: {e}. Pick names may still appear via draft metadata."
    )

try:
    if uploaded:
        ranking = normalize_rankings(pd.read_csv(uploaded), players)
        if page == "overview":
            st.caption(f"{len(ranking)} ranked players matched from your CSV.")
    else:
        ranking = pd.DataFrame()
except Exception as e:
    ranking = pd.DataFrame()
    st.error(f"Ranking file problem: {e}")

adp_frame = pd.DataFrame()
adp_updated = ""
if ranking.empty:
    try:
        adp_payload = cached_adp_rows()
        adp_frame = match_adp(adp_payload.get("players") or [], players)
        adp_updated = adp_payload.get("updated") or ""
    except Exception:
        adp_frame = pd.DataFrame()

my_user_id = st.session_state.get("cfg_team_id") or ""
if my_user:
    try:
        user = api_get(f"user/{quote(my_user)}")
        my_user_id = str(user["user_id"])
    except Exception as e:
        st.warning(f"Could not identify username: {e}")
elif not my_user_id and league_id:
    # Keep previously selected team if present
    my_user_id = st.session_state.get("cfg_team_id") or ""

try:
    draft = api_get(f"draft/{quote(draft_id)}")
except Exception as e:
    st.error(f"Cannot load draft {draft_id}: {e}")
    st.stop()

league_name = league.get("name") or "Connected Draft"
st.session_state.sidebar_league_name = league_name


@st.fragment(run_every=f"{refresh}s")
def live_dashboard(active_page: str):
    try:
        picks, fresh_draft = live_draft_snapshot(draft_id)
        picks = picks or []
        if not isinstance(picks, list):
            raise ValueError("Unexpected draft pick response")
    except Exception as e:
        st.error(f"Live picks unavailable: {e}")
        return

    picked_ids = {str(p.get("player_id")) for p in picks if p.get("player_id") is not None}
    picks = sorted(picks, key=lambda p: int(p.get("pick_no") or 0))
    teams = int(
        (fresh_draft.get("settings") or {}).get("teams") or (league.get("total_rosters") or 0)
    )
    rounds = int((fresh_draft.get("settings") or {}).get("rounds") or 0)
    next_pick = len(picks) + 1
    draft_status = fresh_draft.get("status", "unknown")

    roster_ids = []
    if my_user_id:
        for p in picks:
            if str(p.get("picked_by")) == my_user_id and p.get("player_id") is not None:
                roster_ids.append(str(p["player_id"]))

    my_slot = (fresh_draft.get("draft_order") or {}).get(my_user_id)
    if not my_slot and my_user_id:
        for k, v in (fresh_draft.get("draft_order") or {}).items():
            if str(k) == my_user_id:
                my_slot = v
    upcoming = []
    if my_slot and teams:
        for n in range(next_pick, teams * rounds + 1):
            rd = (n - 1) // teams + 1
            slot = (
                ((n - 1) % teams + 1)
                if fresh_draft.get("type") != "snake" or rd % 2
                else (teams - (n - 1) % teams)
            )
            if slot == int(my_slot):
                upcoming.append(n)

    articles = news_feed()
    active_positions = league.get("roster_positions") or [
        "PG",
        "SG",
        "SF",
        "PF",
        "C",
        "G",
        "F",
        "UTIL",
    ]
    slots = [s for s in active_positions if str(s).upper() not in ("BN", "BENCH", "IR", "IL", "TAXI")]
    board = build_recommendations(
        ranking,
        players,
        picked_ids,
        roster_ids,
        slots,
        articles,
        bool(my_user_id),
        upside_weight,
        safety_weight,
        risk_weight,
        fit_bonus,
        adp_frame,
        teams or 12,
    )

    if active_page == "overview":
        is_complete = draft_status in ("complete", "completed")
        render_page_header(
            title="Draft Overview",
            subtitle=APP_TAGLINE,
            live=not is_complete and draft_status in ("drafting", "in_progress"),
        )
        safe_league = escape_html(str(league_name))
        safe_draft = escape_html(str(draft_id))
        safe_league_id = escape_html(str(league_id or "n/a"))
        safe_status = escape_html(str(draft_status).replace("_", " ").title())
        st.markdown(
            '<div class="fx-league-card">'
            f'<strong>{safe_league}</strong>'
            f'<span>{teams or "—"} teams</span>'
            '<span>Lock-In scoring</span>'
            f'<span>Draft {safe_draft}</span>'
            f'<span>League {safe_league_id}</span>'
            f'<span>Status: {safe_status}</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        m1, m2, m3, m4 = st.columns(4, gap="medium")
        m1.metric("Picks completed", len(picks))
        m2.metric("Next overall pick", "—" if is_complete else next_pick)
        m3.metric("Draft teams", teams or "—")
        m4.metric("Draft status", safe_status)
        st.caption(
            "Last checked: "
            + datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
            + f" · Refreshing every {refresh}s"
        )
        if upcoming and not is_complete:
            st.caption(
                "Your upcoming picks (estimated): " + ", ".join(str(n) for n in upcoming[:5])
            )
        elif my_user_id and not is_complete:
            st.caption("No upcoming picks detected for your slot.")

        if my_user_id:
            names = [player_name(pid, players, picks) for pid in roster_ids]
            st.caption(
                "Your team: " + (", ".join(names) if names else "no players drafted yet")
            )
            if board.get("open_slots"):
                st.caption("Open starter slots: " + ", ".join(str(s) for s in board["open_slots"]))
        else:
            st.caption("Select your Sleeper account in Settings to include roster fit.")

        if board.get("reluctant"):
            st.warning(
                "Every close alternative also has an injury or a negative headline."
            )

        render_top_recommendations(board.get("options") or [], board.get("origin"))
        left, right = st.columns(2, gap="medium")
        with left:
            render_pick_card(
                "Sleeper pick",
                board.get("sleeper"),
                "No later ADP stands out in the next six rounds.",
                badge="VALUE",
                badge_class="fx-badge-value",
            )
        with right:
            render_pick_card(
                "Fade",
                board.get("fade"),
                "No high-ADP player is clearly ruled out by an injury tag or headline.",
                badge="CAUTION",
                badge_class="fx-badge-caution",
            )

    elif active_page == "board":
        completed = draft_status in ("complete", "completed")
        render_page_header(
            title="Draft Board",
            subtitle="Follow each selection and see how the draft is progressing.",
            live=not completed and draft_status in ("drafting", "in_progress"),
        )
        m1, m2, m3 = st.columns(3)
        m1.metric("Picks made", len(picks))
        m2.metric("Teams", teams or "—")
        m3.metric("Latest round", max((int(p.get("round") or 0) for p in picks), default=0) or "—")
        if completed:
            st.info("This draft is complete. You can review all picks below.")
        st.markdown("### Recent draft activity")
        st.caption("The latest selections appear first.")
        if picks:
            for pick in reversed(picks[-5:]):
                name = escape_html(player_name(pick.get("player_id"), players, picks))
                no = escape_html(str(pick.get("pick_no") or "—"))
                rd = escape_html(str(pick.get("round") or "—"))
                positions = ", ".join(player_positions(players.get(str(pick.get("player_id")), {})))
                st.markdown(
                    f'<div class="fx-activity-row"><span class="fx-activity-number">{no}</span>'
                    f'<div><strong>{name}</strong><small>Round {rd} · '
                    f'{escape_html(positions or "Position unavailable")}</small></div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No draft picks yet.")
        with st.container(border=True):
            st.markdown("### Complete pick history")
            rows = []
            for pick in reversed(picks):
                rows.append({
                    "Overall": pick.get("pick_no"),
                    "Round": pick.get("round"),
                    "Player": player_name(pick.get("player_id"), players, picks),
                    "User": pick.get("picked_by"),
                    "Roster": pick.get("roster_id"),
                    "Position": ", ".join(
                        player_positions(players.get(str(pick.get("player_id")), {}))
                    ),
                })
            if rows:
                search = st.text_input("Search drafted players", key="draft_search")
                frame = pd.DataFrame(rows)
                if search.strip():
                    frame = frame[frame["Player"].astype(str).str.contains(
                        search.strip(), case=False, regex=False, na=False
                    )]
                st.dataframe(frame, hide_index=True, width="stretch", height=430)
            if roster_ids:
                with st.expander("Players on your team"):
                    st.write(", ".join(player_name(pid, players, picks) for pid in roster_ids))


    elif active_page == "players":
        render_page_header(
            title="Player Rankings",
            subtitle="Available players ordered by your projections or ADP blend.",
            live=True,
        )
        if not board["rows"]:
            if board["origin"] == "projection":
                st.warning("No available players matched your rankings file.")
            else:
                st.warning(
                    "No available players could be ranked. Check the player directory or upload a CSV."
                )
        else:
            if board["origin"] == "adp":
                stamp = f" Updated {adp_updated}." if adp_updated else ""
                st.caption(
                    f"Order starts from the [Hashtag Basketball ADP blend]({ADP_URL}).{stamp}"
                )
            elif board["origin"] == "search_rank":
                st.caption("ADP did not load. Order starts from Sleeper search rank.")
            else:
                st.caption("Order uses your imported projections and roster/injury context.")

            r1, r2, r3 = st.columns(3)
            r1.metric("Ranked players", len(board["rows"]))
            r2.metric("Ranking method", {
                "adp": "ADP blend", "projection": "Custom projections",
            }.get(board["origin"], "Sleeper rank"))
            r3.metric("Roster aware", "Yes" if my_user_id else "No")
            if board["origin"] == "adp":
                st.info("ADP is Average Draft Position. Lower numbers mean a player "
                        "is typically selected earlier, not that they score fewer points.")
            if not my_user_id:
                st.caption("Add your Sleeper account under Settings to include roster fit.")
            st.markdown("### Available player rankings")
            shown = list(board["rows"][:75])
            labels = {}
            for role, key in (("Fade", "fade"), ("Sleeper", "sleeper")):
                pid = (board.get(key) or {}).get("player_id")
                if pid:
                    labels[pid] = role
            for index, row in enumerate(board.get("options") or [], 1):
                pid = row.get("player_id")
                if not pid:
                    continue
                option_label = f"Option {index}"
                labels[pid] = f"{labels[pid]} · {option_label}" if pid in labels else option_label
            extra = [
                row
                for row in (board.get("sleeper"), board.get("fade"), board.get("recommended"))
                if row and all(existing["player_id"] != row["player_id"] for existing in shown)
            ]
            shown = (extra + shown)[:75]
            records = []
            for rank_index, row in enumerate(shown, 1):
                record = {
                    "Rank": rank_index,
                    "Player": row["player"],
                    "Positions": row["position"],
                    "Team": row["team"],
                    "Injury": row["injury"],
                    "Pick tag": labels.get(row["player_id"], ""),
                }
                if board["origin"] == "adp":
                    record["Blend ADP"] = (
                        None if row.get("blend_adp") is None else round(row["blend_adp"], 1)
                    )
                elif board["origin"] == "projection":
                    record["Score"] = round(float(row["score"]), 2)
                else:
                    record["Baseline"] = row["baseline"]
                query = quote(f"{row['player']} NBA")
                record["ESPN"] = f"https://www.espn.com/search/_/q/{query}"
                records.append(record)
            positions = sorted(
                {
                    p.strip()
                    for row in shown
                    for p in str(row.get("position") or "").replace("/", ",").split(",")
                    if p.strip()
                }
            )
            filter_pos = st.selectbox(
                "Filter by position",
                ["All"] + positions,
                key="players_pos_filter",
            )
            frame = pd.DataFrame(records)
            if filter_pos != "All":
                frame = frame[frame["Positions"].astype(str).str.contains(filter_pos, na=False)]
            st.dataframe(
                frame, hide_index=True, width="stretch", height=450,
                column_config={"ESPN": st.column_config.LinkColumn(
                    "Player info", display_text="Open ESPN"
                )},
            )
            st.download_button(
                "Export available rankings",
                frame.to_csv(index=False),
                "best_available.csv",
                "text/csv",
                key="export_avail",
            )

    elif active_page == "reports":
        render_page_header(
            title="Reports & News",
            subtitle="Headlines that can move picks up, down, or onto the fade list.",
            live=True,
        )
        st.caption(
            "RSS: ESPN NBA and Google News. Verify injuries before drafting."
        )
        if not articles:
            st.warning("News feeds are unavailable right now.")
        else:
            grouped = {}
            for row in board["rows"][:80]:
                for hit in row.get("hits") or []:
                    bucket = grouped.setdefault(hit["title"], {"hit": hit, "names": []})
                    if row["player"] not in bucket["names"]:
                        bucket["names"].append(row["player"])
            relevant = list(grouped.values())
            if relevant:
                with st.container(border=True):
                    st.markdown("**Reports mentioning top available players**")
                    for item in relevant[:12]:
                        article = item["hit"]
                        st.markdown(
                            f'- [{article["title"]}]({article["link"]}) — {article["source"]} • '
                            f'{", ".join(item["names"])} · {article["tone"]}'
                        )
            with st.container(border=True):
                st.markdown("**Latest league-wide headlines**")
                for article in articles[:20]:
                    st.markdown(
                        f'- [{article["title"]}]({article["link"]}) — {article["source"]}'
                    )


if page in ("overview", "board", "players", "reports"):
    # Keyed page content remounts when navigation changes, enabling a brief
    # enter animation without altering the Sleeper data-refresh fragment.
    with st.container(key=f"view_{page}"):
        live_dashboard(page)
    st.caption(
        "Data: Sleeper API · Hashtag Basketball ADP · ESPN / Google News. Advisory only — pick in Sleeper."
    )
