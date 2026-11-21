import re
import time
from html import escape as escape_html
from datetime import datetime, timezone
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st
import feedparser

from adp import ADP_URL, fetch_adp_rows, match_adp
from recommend import build_recommendations
from roster import assign_lineup, chronological_roster, next_user_picks, top_five_for_pick
from ai import openai_configured, get_scout_access_code, scout_access_granted
from draft_strategy import evaluate_pick_timing
from recommend import role_counts
from copilot import ask_copilot, context_snapshot, compare_question
from evaluation import (record_snapshot, evaluate_snapshots, evaluation_summary,
                        replay_adp_baseline, rows_as_csv)
from opponent_draft import opponent_context_for_candidate
from nba_teams import roster_breakdown, FRANCHISES
from scout import (cache_entry, cached_report_matches, research_key,
                   research_allowed, recovery_allowed, use_scout,
                   turn_research_key, auto_research_due, record_auto_attempt,
                   CACHE_TTL_SECONDS)
from config import default_draft_url
from scout_design import (
    scout_hero_html, scout_candidate_html, details_header_html,
    insight_panel_html, source_heading_html,
)
from scout_style import inject_scout_css
from page_style import inject_page_css
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
    initial_sidebar_state="auto",
)
inject_css()
inject_page_css()
inject_scout_css()

# Base test draft lives in gitignored .env as PICKY_DEFAULT_DRAFT_URL (not hardcoded).
DEFAULT_DRAFT_URL = default_draft_url()

if "page" not in st.session_state:
    st.session_state.page = "overview"
if "cfg_draft_link" not in st.session_state:
    st.session_state.cfg_draft_link = DEFAULT_DRAFT_URL
if "cfg_league_id" not in st.session_state:
    st.session_state.cfg_league_id = ""
if "cfg_my_user" not in st.session_state:
    st.session_state.cfg_my_user = ""
# Keep durable copies separate from widget keys. Streamlit removes widget keys
# when their controls are not rendered (e.g. after leaving Settings).
for _field, _default in (
    ("cfg_draft_link", DEFAULT_DRAFT_URL),
    ("cfg_my_user", ""),
    ("cfg_league_id", ""),
):
    _saved_key = f"saved_{_field}"
    if _saved_key not in st.session_state:
        st.session_state[_saved_key] = st.session_state.get(_field, _default)
    st.session_state[_field] = st.session_state[_saved_key]
if "saved_team_id" not in st.session_state:
    st.session_state.saved_team_id = st.session_state.get("cfg_team_id", "")
st.session_state.cfg_team_id = st.session_state.saved_team_id


def draft_setting_changed(name):
    value = st.session_state[f"_edit_{name}"]
    st.session_state[f"saved_{name}"] = value
    st.session_state[name] = value


def draft_setting_input(label, name, **kwargs):
    widget_key = f"_edit_{name}"
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state[f"saved_{name}"]
    return st.text_input(label, key=widget_key, on_change=draft_setting_changed,
                         args=(name,), **kwargs)


if "cfg_refresh" not in st.session_state:
    st.session_state.cfg_refresh = 10
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


@st.cache_data(ttl=4, show_spinner=False)
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
    # Standardized optional Lock-In inputs: per-game mean/floor/upside and
    # availability. Stat means are scored with league settings when complete.
    from lockin import STATS
    for name in ("upside_fppg", "floor_fppg", "games_per_week",
                 "availability_pct", "stdev_fppg", *STATS):
        df[name] = pd.to_numeric(df[cols[name]], errors="coerce") if name in cols else float("nan")
    df["projected_fppg"] = (
        pd.to_numeric(df[cols[stat_col]], errors="coerce")
        if stat_col in ("projected_fppg", "fppg") else float("nan")
    )
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


def roster_player_card(item, players, picks):
    """HTML is escaped; one reusable compact card for starter/utility/bench."""
    pid = item.get("player_id")
    meta = players.get(str(pid), {}) if pid else {}
    name = player_name(pid, players, picks) if pid else "Open slot"
    eligible = ", ".join(player_positions(meta)) if pid else "Position available"
    nba_team = str(meta.get("team") or "Free agent") if pid else "—"
    slot = str(item.get("slot") or "BN")
    group = str(item.get("group") or "starter")
    designation = "Bench" if group == "bench" else (
        "Utility" if group == "utility" else "Starter"
    )
    no = item.get("pick_number")
    pick = f"#{no}" if no is not None else "Open"
    css_class = " fx-roster-empty" if not pid else ""
    return (
        f'<div class="fx-roster-player{css_class}">'
        f'<span class="fx-roster-slot">{escape_html(slot)}</span>'
        '<div class="fx-roster-player-info">'
        f'<strong>{escape_html(str(name))}</strong>'
        f'<small>{escape_html(str(eligible))} · '
        f'{escape_html(nba_team)}</small>'
        f'<small class="fx-roster-type">{escape_html(designation)}</small>'
        '</div>'
        f'<span class="fx-roster-pick">{escape_html(pick)}</span>'
        '</div>'
    )


def render_roster_grid(roster_state, players, picks):
    """Responsive 2-column top-eight plus 1-column utility/bench rail."""
    primary = "".join(roster_player_card(item, players, picks)
                      for item in roster_state["primary"])
    utility = "".join(roster_player_card(item, players, picks)
                      for item in roster_state["utility"])
    bench = "".join(roster_player_card(item, players, picks)
                    for item in roster_state["bench"])
    # st.markdown processes raw HTML as Markdown; complex block-level
    # markup can lose its div/section structure and flatten into plain text.
    # st.html renders this sanitized, escaped HTML as actual DOM elements.
    st.html(
        '<div class="fx-roster-layout">'
        '<section class="fx-roster-main">'
        '<div class="fx-roster-heading">Starting eight</div>'
        f'<div class="fx-roster-starters">{primary}</div>'
        '</section><section class="fx-roster-rail">'
        '<div class="fx-roster-heading">Utility & bench</div>'
        f'<div class="fx-roster-extras">{utility}{bench or "<div class=\'fx-roster-note\'>No bench picks yet</div>"}</div>'
        '</section></div>',
    )





def render_team_breakdown(roster_ids, players, roster_state):
    """Separately show core five coverage and each rostered NBA team's geography."""
    snapshot = roster_breakdown(roster_ids, players, roster_state)
    eligible_counts = snapshot["eligible_counts"]
    eligible_chips = "".join(
        '<span class="fx-team-pos '
        + ("fx-team-pos-filled" if eligible_counts[position] else "fx-team-pos-open")
        + '">'
        + f'{escape_html(position)} <small>×{eligible_counts[position]}</small></span>'
        for position in ("PG", "SG", "SF", "PF", "C")
    )
    teams = "".join(
        f'<span class="fx-team-chip" title="{escape_html(FRANCHISES.get(code, code), quote=True)}">'
        f'{escape_html(code)} <small>×{count}</small></span>'
        for code, count in sorted(snapshot["teams"].items())
    ) or '<span class="fx-team-empty">No NBA teams represented yet</span>'
    conferences = "".join(
        f'<div class="fx-team-stat"><strong>{escape_html(name)}</strong>'
        f'<span>{count} player{"s" if count != 1 else ""}</span></div>'
        for name, count in (("Eastern", snapshot["conferences"].get("Eastern", 0)),
                            ("Western", snapshot["conferences"].get("Western", 0)))
    )
    divisions = "".join(
        f'<span class="fx-team-division">{escape_html(name)} '
        f'<b>{count}</b></span>'
        for name, count in sorted(snapshot["divisions"].items()) if count
    ) or '<span class="fx-team-empty">No divisions represented yet</span>'
    unknown = snapshot["unknown"]
    st.html(
        '<div class="fx-team-breakdown">'
        '<section class="fx-team-panel">'
        '<span class="fx-team-eyebrow">Role coverage</span>'
        f'<strong class="fx-team-coverage">{snapshot["eligible_covered_count"]}<small> / 5 positions covered</small></strong>'
        f'<div class="fx-team-position-list">{eligible_chips}</div>'
        '<small class="fx-team-footnote">Counts show how many drafted players can play each position, including utility and bench players.</small>'
        '</section>'
        '<section class="fx-team-panel">'
        '<span class="fx-team-eyebrow">NBA teams represented</span>'
        f'<strong class="fx-team-coverage">{len(snapshot["teams"])}<small> / 30</small></strong>'
        f'<div class="fx-team-position-list">{teams}</div>'
        f'<small class="fx-team-footnote">{unknown} player(s) have no known NBA team</small>'
        '</section>'
        '<section class="fx-team-panel fx-team-panel-wide">'
        '<span class="fx-team-eyebrow">Conferences & divisions</span>'
        f'<div class="fx-team-conferences">{conferences}</div>'
        f'<div class="fx-team-position-list">{divisions}</div>'
        '</section></div>'
    )



@st.dialog("Player scouting details", width="large")
def show_scout_player_details(candidate, player_ai, timing, source_list):
    """Styled, accessible NBA scouting panel; all dynamic links are real sources."""
    player_ai = player_ai or {}
    verified = player_ai.get("verified_expert_evidence") or []
    ranked = [item for item in verified
              if item.get("kind") == "Expert rankings / cheat sheet"]
    news = [item for item in verified
            if item.get("kind") != "Expert rankings / cheat sheet"]
    st.html(details_header_html(candidate, citations=len(verified)))

    overview_tab, sources_tab, context_tab = st.tabs(
        ["✦ Scouting overview", "↗ Reports & sources", "▤ Draft context"]
    )
    with overview_tab:
        a, b = st.columns(2, gap="medium")
        with a:
            st.html(insight_panel_html(
                "Why this player?",
                candidate.get("roster") or player_ai.get("draft_fit")
                or timing.get("position_note") or "Roster fit unavailable.",
                kind="green", icon="✓",
            ))
        with b:
            st.html(insight_panel_html(
                "Draft now or wait?", timing.get("reason") or "Timing unavailable.",
                kind="amber" if timing.get("risk") == "elevated" else "normal",
                icon="◷",
            ))
        st.markdown("##### Player outlook")
        role_col, injury_col = st.columns(2, gap="medium")
        with role_col:
            st.html(insight_panel_html(
                "Opportunity & role",
                player_ai.get("role_outlook") or
                "No player-specific opportunity report is available yet.",
                icon="↗",
            ))
        with injury_col:
            st.html(insight_panel_html(
                "Injury & availability",
                player_ai.get("availability_risk") or
                candidate.get("injury") or
                "Verify the latest status with the NBA team or your fantasy provider.",
                icon="♡",
            ))
        st.markdown("##### Recent findings")
        st.html(insight_panel_html(
            "Fantasy research summary",
            player_ai.get("recent_findings") or
            "Research has not been run for this candidate. "
            "Picky's original draft ranking is still available.",
            kind="green" if verified else "normal", icon="✦",
        ))
        if player_ai.get("expert_take"):
            st.html(insight_panel_html(
                "What fantasy experts say",
                player_ai["expert_take"], icon="▤",
            ))
        if not verified:
            st.caption("This player has no linked, player-specific source findings. "
                       "Any AI summary above is unverified; check original reporting.")

    with sources_tab:
        st.caption("Linked articles were retrieved during research; model summaries "
                   "and reported dates have not been independently fact-checked.")
        if ranked:
            st.markdown("##### Expert rankings & cheat sheets")
            for item in ranked:
                with st.container(border=True):
                    st.html(source_heading_html(
                        item.get("publisher") or "Expert ranking",
                        item.get("ranking_format") or "Cheat sheet",
                        item.get("freshness") or "Date unknown",
                    ))
                    st.write(item.get("claim") or "Read the original ranking.")
                    st.link_button("Read original ranking", item["source_url"])
        if news:
            st.markdown("##### NBA news & fantasy analysis")
            for item in news:
                with st.container(border=True):
                    st.html(source_heading_html(
                        item.get("publisher") or "NBA report",
                        item.get("kind") or "Fantasy analysis",
                        item.get("freshness") or "Date unknown",
                    ))
                    st.write(item.get("claim") or "Read the original article.")
                    st.link_button("Read original report", item["source_url"])
        if not verified:
            st.info("No player-specific source citations were verified. "
                    "That does not imply there are no articles about this player.")
        used_urls = {str(item.get("source_url") or "") for item in verified}
        extras = [src for src in (source_list or [])
                  if isinstance(src, dict) and src.get("url")
                  and src.get("url") not in used_urls]
        if extras:
            with st.expander("Other retrieved pages · not verified for this player's claims"):
                for article in extras[:8]:
                    st.link_button(str(article.get("title") or "Read retrieved page")[:100],
                                   article["url"])

    with context_tab:
        adp = candidate.get("blend_adp")
        search_rank = candidate.get("sleeper_search_rank")
        c1, c2, c3 = st.columns(3)
        c1.metric("Blended ADP", f"{float(adp):.1f}" if isinstance(adp, (float, int)) else "—")
        c2.metric("Sleeper search rank", f"#{search_rank}" if search_rank is not None else "—")
        c3.metric("Wait risk", str(timing.get("risk") or "Unknown").title())
        st.html(insight_panel_html(
            "Current roster fit",
            candidate.get("roster") or timing.get("position_note")
            or "No roster fit available.",
            kind="green", icon="✓",
        ))
        if player_ai.get("why_now"):
            st.html(insight_panel_html(
                "AI draft timing perspective", player_ai["why_now"], icon="◷",
            ))
        st.caption("Sleeper search rank is not a fantasy rank. "
                   "ADP is historical selection order, not projected points; "
                   "wait risk is not a calibrated probability.")
    if st.button("Close details", key="close_scout_dialog", use_container_width=True):
        st.rerun()


def render_scout_report(entry, candidates):
    """One compact report summary; card summaries live in the unified Top 5 list."""
    report = entry.get("report") or {}
    covered = len([p for p in report.get("players", []) if isinstance(p, dict)])
    sourced = len(entry.get("sourced_players") or [])
    linked = (entry.get("research_quality") or {}).get("total_verified_links", 0)
    st.caption(
        f"✦ Research updated · {covered}/{len(candidates)} candidate summaries "
        f"· {sourced} with cited findings · {linked} linked reports"
    )
    with st.expander("Research coverage & diagnostics"):
        st.caption("Research summaries and citation dates may contain AI errors. "
                   "Check the source articles before choosing a player.")
        for candidate in candidates:
            name = str(candidate.get("player") or "")
            player = next(
                (p for p in report.get("players", [])
                 if isinstance(p, dict) and p.get("name") == name),
                None,
            )
            count = len((player or {}).get("verified_expert_evidence") or [])
            st.write(f"{name}: {count} linked finding{'s' if count != 1 else ''}")
        errors = entry.get("research_failures") or []
        if errors:
            st.markdown("**Research diagnostics**")
            for item in errors:
                st.caption(f"{item.get('player') or 'Player'}: "
                           f"{item.get('error') or 'Report incomplete'}")
        if not linked:
            st.caption("No individually cited source findings were found in this report.")


def render_settings_form(league_id_hint: str = ""):
    render_page_header(
        title="Settings & Connections",
        subtitle="Set up Picky in a few steps. Recommended defaults work for beginners.",
        live=False,
    )
    with st.container(border=True):
        st.markdown("### 1. Connect your Sleeper draft")
        st.caption("Paste your Sleeper draft link to load the league and picks. No password needed.")
        draft_setting_input("Sleeper draft link or ID", "cfg_draft_link",
                      help="Copy your draft URL directly from Sleeper.")
        draft_setting_input("Sleeper username or user ID (optional)", "cfg_my_user",
                      help="Helps Picky account for players already on your roster.")
        with st.expander("Additional connection options"):
            draft_setting_input("League ID override (usually automatic)", "cfg_league_id",
                          placeholder="Optional override")
            st.select_slider("Check for picks every", options=[5, 10, 15, 30, 60],
                             key="cfg_refresh", format_func=lambda x: f"{x} sec",
                             help="5 seconds is the fastest option. API response times can delay updates.")
    with st.container(border=True):
        st.markdown("### 2. Choose your rankings source")
        st.caption("Picky uses an ADP blend automatically. Optionally upload your own projections.")
        with st.expander("Custom projections (optional)"):
            st.file_uploader("Player rankings or projections CSV", type=["csv"], key="cfg_upload")
            st.download_button(
                "Download Lock-In projection template",
                data="player,projected_fppg,upside_fppg,floor_fppg,stdev_fppg,games_per_week,availability_pct\\n",
                file_name="lockin_projection_template.csv", mime="text/csv",
            )
            st.caption("For a calibrated-input Lock-In opportunity estimate, include projected_fppg, stdev_fppg (or floor/upside), games_per_week and availability_pct. Picky never invents missing values.")
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
        meta=(
            f'Team: {st.session_state.get("_edit_team_select")}'
            if st.session_state.get("_edit_team_select") not in (None, "", "Not selected")
            else (f'Team: {st.session_state.get("cfg_my_user")}'
                  if st.session_state.get("cfg_my_user") else "Manage under Settings")
        ) if _preview_connected else "Open Settings to connect",
    )
    nav_icons = {
        "overview": ":material/home:",
        "team": ":material/groups:",
        "board": ":material/view_module:",
        "players": ":material/bar_chart:",
        "reports": ":material/article:",
        "lab": ":material/science:",
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
    # The keyed parent identifies the active menu row, including first load.
    # Use stronger selector specificity than the standard sidebar button rules.
    st.markdown(
        f'<style>section[data-testid="stSidebar"] div.st-key-nav_{active_page} '
        'button[kind="secondary"], '
        f'section[data-testid="stSidebar"] .st-key-nav_{active_page} button {{'
        'background:var(--color-accent-subtle) !important;'
        'color:var(--color-text-primary) !important;font-weight:700 !important;'
        'border-left:3px solid var(--color-accent) !important;}'
        f'section[data-testid="stSidebar"] .st-key-nav_{active_page} '
        '[data-testid="stIconMaterial"] {color:var(--color-accent) !important;}'
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
                saved_team = st.session_state.get("saved_team_id", "")
                labels = ["Not selected"] + list(options)
                preferred = next((label for label, user_id in options.items()
                                  if user_id == saved_team), "Not selected")
                if st.session_state.get("_edit_team_select") not in labels:
                    st.session_state["_edit_team_select"] = preferred

                def save_team_choice():
                    chosen = options.get(st.session_state["_edit_team_select"], "")
                    st.session_state.saved_team_id = chosen
                    st.session_state.cfg_team_id = chosen

                st.selectbox(
                    "Select your team / Sleeper account",
                    labels,
                    key="_edit_team_select",
                    on_change=save_team_choice,
                    help="Your selection is kept while navigating between Picky pages.",
                )
                st.session_state.cfg_team_id = st.session_state.saved_team_id
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

    # Prefer the actual Sleeper roster assignment (handles picks made for a
    # roster by a different user). Fall back to picked_by if mapping is absent.
    owned_roster_ids = set()
    if my_user_id and league_id:
        try:
            for team_roster in api_get(f"league/{quote(league_id)}/rosters") or []:
                if str(team_roster.get("owner_id")) == str(my_user_id):
                    owned_roster_ids.add(str(team_roster.get("roster_id")))
        except Exception:
            pass
    roster_ids = []
    roster_pick_numbers = []
    if my_user_id:
        for p in picks:
            belongs = (
                str(p.get("roster_id")) in owned_roster_ids
                if owned_roster_ids and p.get("roster_id") is not None
                else str(p.get("picked_by")) == str(my_user_id)
            )
            if belongs and p.get("player_id") is not None:
                roster_ids.append(str(p["player_id"]))
                roster_pick_numbers.append(p.get("pick_no"))

    upcoming = next_user_picks(picks, fresh_draft, my_user_id, teams, rounds)

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
    roster_state = chronological_roster(
        roster_ids, players, slots, pick_numbers=roster_pick_numbers,
    ) if my_user_id else None
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
        scoring_settings=league.get("scoring_settings") or {},
    )

    if active_page == "lab":
        render_page_header(
            title="AI Lab",
            subtitle="Measure draft decisions and test the ADP baseline using observed Sleeper selections.",
            live=False,
        )
        st.info("Evaluation uses actual Sleeper picks, not fabricated player outcomes. "
                "Live shortlist snapshots are saved only in this browser session. "
                "Historical replay uses today's ADP and is a retrospective proxy, not an unbiased backtest.")
        all_snapshots = st.session_state.get("picky_eval_snapshots", {})
        snapshots = {key: value for key, value in all_snapshots.items()
                     if value.get("draft_id") == str(draft_id)}
        rows_eval = evaluate_snapshots(snapshots, picks)
        summary = evaluation_summary(rows_eval)
        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Outcomes assessed", summary["reviewed"])
        q2.metric("Survived until next turn", summary["survived"])
        q3.metric("Taken before next turn", summary["taken"])
        q4.metric("Pending / unverified", summary["pending"] + summary["unverifiable"])
        if rows_eval:
            st.dataframe(pd.DataFrame(rows_eval), hide_index=True, use_container_width=True)
            st.download_button(
                "Export observed decisions CSV", data=rows_as_csv(rows_eval),
                file_name="picky_observed_decisions.csv", mime="text/csv",
                key="export_live_evaluation",
            )
        else:
            st.caption("No on-clock shortlist snapshots recorded in this browser session yet. "
                       "Keep Overview open during a draft turn to begin collecting decisions.")
        st.markdown("### Retrospective ADP replay")
        st.caption("Replays the current ADP order against picks already made in this draft. "
                   "It cannot reconstruct historically available projections, news or Lock-In values.")
        replay = replay_adp_baseline(
            picks,
            adp_frame.to_dict("records") if not adp_frame.empty else [],
            teams,
        )
        if replay:
            totals = evaluation_summary(replay)
            st.write(
                f"Reviewing {totals['reviewed']} resolved candidate-pick observations: "
                f"{totals['survived']} survived to the next round, "
                f"{totals['taken']} were selected earlier."
            )
            st.dataframe(pd.DataFrame(replay), hide_index=True, use_container_width=True)
            st.download_button(
                "Export retrospective replay CSV", data=rows_as_csv(replay),
                file_name="picky_adp_replay.csv", mime="text/csv",
                key="export_replay",
            )
        else:
            st.caption("Retrospective replay becomes available after enough draft picks "
                       "and with the Hashtag ADP source loaded.")
        st.markdown("### Interpreting results")
        st.caption("These checks measure shortlist availability, not whether the player "
                   "would have scored more fantasy points. No price or paid AI requests "
                   "are made to run these diagnostics.")
        return

    if active_page == "team":
        render_page_header(
            title="My Team",
            subtitle="See your drafted players, projected starting lineup, and open slots.",
            live=False,
        )
        if not my_user_id:
            st.info("Select your Sleeper account in Settings & Connections to see your team.")
            return
        t1, t2, t3 = st.columns(3)
        t1.metric("Players drafted", len(roster_ids))
        t2.metric("Starter slots filled", f"{roster_state['filled']} / {roster_state['total']}")
        t3.metric("Open starter slots", len(roster_state["open_slots"]))
        if upcoming and draft_status not in ("complete", "completed"):
            st.caption(f"Next estimated pick: #{upcoming[0]} ({upcoming[0] - next_pick} picks away)")
        st.markdown("### My roster")
        st.caption("Earlier picks fill eligible slots first; the right column holds utility and bench selections.")
        render_roster_grid(roster_state, players, picks)
        st.markdown("#### Roster coverage & NBA distribution")
        render_team_breakdown(roster_ids, players, roster_state)
        st.caption("Roster placement is an illustration of draft order, not your submitted Sleeper lineup.")
        st.markdown("### Your remaining needs")
        if roster_state["open_slots"]:
            st.markdown(
                '<div class="fx-pick-needs">' +
                "".join(f'<span>{escape_html(slot)}</span>' for slot in roster_state["open_slots"]) +
                '</div>', unsafe_allow_html=True,
            )
        else:
            st.success("All starting slots can be filled by your drafted players.")
        st.caption("Bench and reserve slots are not considered open starting positions.")

    elif active_page == "overview":
        is_complete = draft_status in ("complete", "completed")
        draft_active = draft_status in ("drafting", "in_progress")
        on_clock = bool(
            my_user_id and upcoming and upcoming[0] == next_pick
            and draft_active and not is_complete
        )
        render_page_header(
            title="Draft Overview",
            subtitle="Your roster, draft recommendations, and real-time pick intelligence.",
            live=draft_active,
        )

        # 1. Compact draft summary: useful context without a giant hero card.
        with st.container(border=True):
            heading, status_col = st.columns([4, 1])
            with heading:
                st.markdown(f"**{league_name}**")
                st.caption(f"Draft {draft_id} · {teams or '—'} teams · "
                           f"Status: {str(draft_status).replace('_', ' ').title()}")
            with status_col:
                if on_clock:
                    st.markdown(":green[**YOUR PICK**]")
                elif is_complete:
                    st.caption("Draft complete")
                else:
                    st.caption("Draft tracker")
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Picks made", len(picks))
            d2.metric("Current pick", "—" if is_complete else f"#{next_pick}")
            d3.metric("Your next pick", f"#{upcoming[0]}" if upcoming and not is_complete else "—")
            d4.metric("Until your turn", max(upcoming[0] - next_pick, 0)
                      if upcoming and not is_complete else "—")
            st.caption(
                "Last synced " + datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
                + f" · Updating every {refresh}s"
            )

        # 2. Show filled slots and needs before any recommendations.
        st.markdown("### My Team")
        if my_user_id and roster_state:
            st.caption(
                f"{roster_state['filled']} / {roster_state['total']} starter and utility slots filled "
                f"· {len(roster_ids)} drafted"
            )
            render_roster_grid(roster_state, players, picks)
            st.markdown("#### Roster coverage & NBA distribution")
            render_team_breakdown(roster_ids, players, roster_state)
            if roster_state["open_slots"]:
                st.markdown(
                    '<div class="fx-pick-needs">'
                    + "".join(f'<span>{escape_html(str(position))}</span>'
                              for position in roster_state["open_slots"])
                    + "</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.caption("All starting positions can currently be filled.")
        else:
            st.info("Select your Sleeper account in Settings to show your roster.")

        # 3. AI Scout: unlocked once in this session, auto-runs ONCE when
        # Sleeper confirms this is your turn. Does not call OpenAI on other refreshes.
        st.html(
            '<div class="fx-scout-heading">'
            '<span class="fx-scout-mark">✦</span>'
            '<div><strong>Picky AI Scout</strong>'
            '<small>NBA research · Roster fit · Next-turn draft intelligence</small>'
            '</div></div>',
        )
        if is_complete:
            st.info("Draft complete. Your live scouting reports are no longer active.")
        else:
            top_five = top_five_for_pick(board.get("rows") or [])
            # Pass factual search rank into AI research *before* its request.
            for candidate in top_five:
                candidate["sleeper_search_rank"] = (
                    players.get(str(candidate.get("player_id")), {}).get("search_rank")
                )
            following_pick = upcoming[1] if len(upcoming) > 1 else None
            if on_clock and following_pick and top_five:
                record_snapshot(
                    st.session_state, draft_id=draft_id,
                    upcoming_pick=upcoming[0], following_pick=following_pick,
                    current_pick=next_pick, candidates=top_five,
                )
            # Sleeper reports current traded-pick ownership separately from
            # original snake order. Cache it briefly; do not guess if missing.
            traded_pick_data = None
            if following_pick and owned_roster_ids and draft_status in ("drafting", "in_progress", "pre_draft", "predraft"):
                try:
                    traded_pick_data = api_get(
                        f"draft/{quote(str(draft_id), safe='')}/traded_picks"
                    )
                    if not isinstance(traded_pick_data, list):
                        traded_pick_data = None
                except Exception:
                    traded_pick_data = None
            opponent_by_player = {}
            if top_five:
                opponent_by_player = {
                    str(candidate.get("player")): opponent_context_for_candidate(
                        candidate, picks=picks, draft=fresh_draft,
                        players=players, slots=slots, current_pick=next_pick,
                        following_pick=following_pick, teams=teams,
                        my_roster_ids=owned_roster_ids,
                        traded_picks=traded_pick_data,
                    )
                    for candidate in top_five
                }
            if not top_five:
                st.info("Waiting for available player rankings before scouting.")
            elif not my_user_id:
                st.info("Select your Sleeper account to enable turn-based AI scouting.")
            elif not openai_configured():
                st.info("Add OPENAI_API_KEY in Streamlit Secrets to enable AI research.")
            elif not get_scout_access_code():
                st.info("Set PICKY_AI_SCOUT_ACCESS_CODE in Streamlit Secrets to protect paid AI requests.")
            else:
                if not st.session_state.get("scout_unlocked", False):
                    code = st.text_input(
                        "AI Scout access code", type="password",
                        key="scout_access_input",
                        help="Unlock manually triggered player research. "
                             "No research runs automatically.",
                    )
                    if code and scout_access_granted(code):
                        st.session_state.scout_unlocked = True
                        st.rerun(scope="fragment")
                    else:
                        st.caption("Unlock AI Scout to research your current players.")
                if st.session_state.get("scout_unlocked", False):
                    next_owned_pick = upcoming[0] if upcoming else None
                    turn_key = (
                        turn_research_key(draft_id, my_user_id, next_owned_pick)
                        if next_owned_pick is not None else None
                    )
                    cached = cache_entry(st.session_state, turn_key) if turn_key else None
                    if cached and not cached_report_matches(cached, top_five):
                        cached = None
                    if cached:
                        render_scout_report(cached, top_five)
                    st.caption(
                        "Research is optional. One click researches each of your Top 5 "
                        "separately (up to five web-search calls and five analysis calls). "
                        "No local usage caps; spending is controlled in your OpenAI account."
                    )
                    if st.button(
                        "Research Top 5 with AI" if not cached else "Refresh AI research",
                        type="primary", icon=":material/travel_explore:",
                        disabled=not bool(turn_key and top_five),
                        key="run_manual_ai_scout",
                        use_container_width=True,
                    ):
                        with st.status("Researching each player and collecting sources…",
                                       expanded=True) as progress:
                            try:
                                use_scout(
                                    st.session_state, turn_key, top_five,
                                    open_slots=roster_state["open_slots"],
                                    context={
                                        "upcoming_pick": next_owned_pick,
                                        "following_pick": following_pick,
                                        "current_pick": next_pick,
                                        "league_teams": teams,
                                        "opponent_by_player": opponent_by_player,
                                        "roster_eligible_counts": role_counts(roster_ids, players),
                                    },
                                )
                            except Exception as exc:
                                st.session_state.setdefault(
                                    "ai_scout_turn_errors", {}
                                )[turn_key] = str(exc)[:500]
                                progress.update(
                                    label="Research request incomplete",
                                    state="error", expanded=False,
                                )
                                st.error("AI research failed: " + str(exc)[:300])
                            else:
                                st.session_state.get(
                                    "ai_scout_turn_errors", {}
                                ).pop(turn_key, None)
                                progress.update(
                                    label="AI research response saved",
                                    state="complete", expanded=False,
                                )
                                st.rerun(scope="fragment")
                    error = st.session_state.get("ai_scout_turn_errors", {}).get(turn_key)
                    if error:
                        with st.expander("Research error details"):
                            st.code(error)
            # The hero and the list use the SAME five candidates. Research
            # summaries augment their cards; no duplicate takeaway list.
            current_entry = None
            if (my_user_id and upcoming and
                    st.session_state.get("scout_unlocked", False)):
                active_key = turn_research_key(draft_id, my_user_id, upcoming[0])
                possible_entry = cache_entry(st.session_state, active_key)
                if cached_report_matches(possible_entry, top_five):
                    current_entry = possible_entry
            ai_report = (current_entry or {}).get("report") or {}
            ai_players = {
                row.get("name"): row
                for row in ai_report.get("players", [])
                if isinstance(row, dict)
            }
            if top_five:
                featured = top_five[0]
                featured_name = str(featured.get("player") or "Player")
                featured_wait = evaluate_pick_timing(
                    featured, current_pick=next_pick,
                    following_pick=following_pick,
                    open_slots=roster_state["open_slots"] if roster_state else [],
                    opponent=opponent_by_player.get(featured_name),
                )
                featured_meta = players.get(str(featured.get("player_id") or ""), {})
                featured_display = dict(featured)
                if featured_meta.get("fantasy_positions"):
                    featured_display["position"] = ", ".join(
                        str(pos) for pos in featured_meta["fantasy_positions"]
                    )
                featured_display["team"] = (
                    featured.get("team") or featured_meta.get("team") or "NBA"
                )
                leader_ai = ai_players.get(featured_name) or {}
                leader_sources = len(leader_ai.get("verified_expert_evidence") or [])
                # The featured choice is Picky's deterministic top-ranked
                # player, NOT an uncalibrated AI confidence judgment.
                st.html(scout_hero_html(
                    featured_display,
                    summary=(leader_ai.get("recent_findings") if leader_sources else
                             featured.get("roster") or featured_wait["position_note"]),
                    risk=featured_wait["risk"],
                    following_pick=following_pick,
                    cited_count=leader_sources,
                    researched=bool(current_entry),
                ))

            st.markdown("#### Top 5 available options")
            if top_five:
                selected_detail = None
                for rank_no, candidate in enumerate(top_five, 1):
                    candidate_name = str(candidate.get("player") or "Player")
                    player_id = str(candidate.get("player_id") or "")
                    meta = players.get(player_id, {})
                    display_candidate = dict(candidate)
                    if meta.get("fantasy_positions"):
                        display_candidate["position"] = ", ".join(
                            str(pos) for pos in meta["fantasy_positions"]
                        )
                    display_candidate["team"] = (
                        candidate.get("team") or meta.get("team") or "NBA"
                    )
                    player_ai = ai_players.get(candidate_name) or {}
                    timing = evaluate_pick_timing(
                        candidate, current_pick=next_pick,
                        following_pick=following_pick,
                        open_slots=roster_state["open_slots"] if roster_state else [],
                        opponent=opponent_by_player.get(candidate_name),
                    )
                    citations = len(player_ai.get("verified_expert_evidence") or [])
                    summary = str(player_ai.get("recent_findings") or "").strip()
                    if not summary:
                        summary = str(
                            candidate.get("roster") or timing.get("position_note")
                            or "Review roster fit and draft timing."
                        )
                    research_state = (
                        "search_only" if candidate_name in
                        ((current_entry or {}).get("retrieval_only_players") or []) else
                        "researched" if player_ai else "ranking"
                    )
                    source_list = (
                        (current_entry or {}).get("per_player_sources", {}).get(
                            candidate_name, []
                        )
                    )
                    with st.container(key=f"ai_candidate_{rank_no}"):
                        info_col, action_col = st.columns(
                            [5.25, 1.18], vertical_alignment="center",
                            gap="medium",
                        )
                        with info_col:
                            st.html(scout_candidate_html(
                                display_candidate, rank_no,
                                summary=summary, risk=timing["risk"],
                                cited_count=citations, research_state=research_state,
                            ))
                        with action_col:
                            if st.button(
                                "View details",
                                key=f"scout_detail_{rank_no}_{player_id}",
                                icon=":material/open_in_full:",
                                use_container_width=True,
                            ):
                                selected_detail = (
                                    display_candidate, player_ai, timing,
                                    source_list,
                                )
                if selected_detail is not None:
                    show_scout_player_details(*selected_detail)
                st.caption(
                    "Picky's ranking engine selects the five available options. "
                    "AI research is optional and may be imperfect; compare source "
                    "articles before drafting in Sleeper."
                )

        # Phase 3: show quantitative Lock-In value only with verified inputs.
        if not is_complete:
            if board.get("origin") == "projection":
                with st.expander("Lock-In opportunity model · inputs and limitations"):
                    st.caption(
                        "An exploratory expected best-game model, not guaranteed "
                        "locked fantasy points. The model uses your league's "
                        "scoring settings when complete stat projections exist; "
                        "otherwise your imported league-scored FPPG."
                    )
                    coverage = board.get("lockin_available", 0)
                    total = len(board.get("rows") or [])
                    st.write(f"Usable Lock-In distributions: {coverage} / {total} projected players.")
                    st.write(
                        "Ranking impact: " +
                        ("Enabled — all compared players have distributions."
                         if board.get("lockin_ranked") else
                         "Not enabled — some players lack comparable distributions.")
                    )
                    lock_rows = [
                        {"Player": player.get("player"),
                         "Opportunity pts": player["lockin"]["points"],
                         "Expected per-game": player["lockin"]["mean"],
                         "Games/week": player["lockin"]["scheduled_games"],
                         "Chance of zero games": player["lockin"]["no_game_prob"]}
                        for player in (board.get("rows") or [])[:25]
                        if (player.get("lockin") or {}).get("available")
                    ]
                    if lock_rows:
                        st.dataframe(pd.DataFrame(lock_rows), hide_index=True,
                                     use_container_width=True)
                    else:
                        st.caption("Upload an enriched projection CSV to enable the model.")
            else:
                st.caption("Lock-In points model inactive: ADP is draft-order "
                           "information, not a projected weekly fantasy score.")

            # Phase 4: paid follow-ups are manual, never part of auto-refresh.
            if (top_five and my_user_id and upcoming and
                    st.session_state.get("scout_unlocked", False) and
                    openai_configured()):
                with st.expander("Ask Picky · AI Copilot and player comparisons"):
                    question_key = turn_research_key(
                        draft_id, my_user_id, upcoming[0]
                    )
                    saved_report = cache_entry(st.session_state, question_key)
                    context = context_snapshot(
                        top_five,
                        role_counts=role_counts(roster_ids, players),
                        next_pick=next_pick,
                        report=(saved_report or {}).get("report"),
                    )
                    history = st.session_state.get("picky_copilot_history", {}).get(
                        question_key, []
                    )
                    st.caption("Questions only run when clicked, using cached research "
                               "without another web search. Model tokens are billed.")
                    options = [
                        str(row.get("player")) for row in top_five if row.get("player")
                    ]
                    if len(options) >= 2:
                        c1, c2 = st.columns(2)
                        with c1:
                            first = st.selectbox("First candidate", options,
                                                 key="copilot_compare_a")
                        with c2:
                            second = st.selectbox(
                                "Second candidate", options,
                                index=1, key="copilot_compare_b",
                            )
                        if st.button("Compare these players", key="copilot_compare_button"):
                            try:
                                query = compare_question(first, second, context)
                                ask_copilot(st.session_state, key=question_key,
                                            context=context, question=query)
                                st.rerun(scope="fragment")
                            except Exception as exc:
                                st.error(f"Comparison unavailable: {str(exc)[:180]}")
                    question = st.text_area(
                        "Ask about this pick",
                        key="picky_copilot_question",
                        placeholder="Why would I take another SG when C is thinner?",
                        max_chars=500, height=80,
                    )
                    if st.button("Ask Picky", key="picky_ask_copilot",
                                 disabled=len(question.strip()) < 3):
                        try:
                            ask_copilot(st.session_state, key=question_key,
                                        context=context, question=question)
                            st.rerun(scope="fragment")
                        except Exception as exc:
                            st.error(f"AI follow-up unavailable: {str(exc)[:180]}")
                    for turn in reversed(history[-4:]):
                        st.markdown("**You:** " + escape_html(turn["question"]))
                        st.write(turn["answer"])
            elif not is_complete:
                st.caption("Unlock AI Scout with your passkey to enable optional "
                           "follow-up questions and comparisons.")

        # 4. Recent draft selections and *actual* lowest ADP players.
        st.markdown("### Draft board & ADP leaders")
        recent_col, adp_col = st.columns(2, gap="large")
        with recent_col:
            with st.container(border=True):
                st.markdown("**Latest picks**")
                if picks:
                    for pick in reversed(picks[-5:]):
                        name = player_name(pick.get("player_id"), players, picks)
                        st.markdown(
                            f"**#{pick.get('pick_no') or '—'}** · "
                            f"{escape_html(str(name))}"
                        )
                else:
                    st.caption("No players have been drafted yet.")
                st.caption("Open Draft Board for the full selection history.")
        with adp_col:
            with st.container(border=True):
                st.markdown("**Top 5 available by ADP**")
                with_adp = [p for p in board.get("rows") or []
                            if p.get("blend_adp") is not None]
                with_adp.sort(key=lambda p: float(p["blend_adp"]))
                if with_adp:
                    for player in with_adp[:5]:
                        st.markdown(
                            f"**{escape_html(str(player.get('player') or 'Player'))}**"
                            f" · ADP {float(player['blend_adp']):.1f}"
                        )
                    st.caption("Lower ADP means players typically get selected earlier.")
                else:
                    st.caption("No blended ADP data is currently available.")
        # 5. Important caveats and optional advanced links remain accessible.
        with st.expander("More draft context & player research"):
            st.caption(f"League ID: {league_id or 'Unavailable'} · "
                       f"Draft ID: {draft_id} · Draft format: {fresh_draft.get('type') or 'Unknown'}")
            st.caption("Your next pick is estimated from Sleeper's draft order. "
                       "Traded picks can differ from the original order.")
            st.caption("AI findings, ADP, and injury information may change. "
                       "Always confirm the actual player is available in Sleeper.")

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
            subtitle="NBA headlines to help you spot updates worth checking before a pick.",
            live=False,
        )
        n1, n2, n3 = st.columns(3)
        n1.metric("Headlines loaded", len(articles))
        n2.metric("News feeds", len({a.get("source") for a in articles if a.get("source")}))
        n3.metric("Players reviewed", min(len(board.get("rows") or []), 80))
        st.caption("News is informational, not a verified injury diagnosis. "
                   "Always confirm updates before drafting.")
        if not articles:
            st.warning("News feeds are unavailable right now.")
        else:
            grouped = {}
            for row in board["rows"][:80]:
                for hit in row.get("hits") or []:
                    headline = hit.get("title")
                    if not headline:
                        continue
                    bucket = grouped.setdefault(headline, {"hit": hit, "names": []})
                    if row["player"] not in bucket["names"]:
                        bucket["names"].append(row["player"])
            if grouped:
                st.markdown("### Reports mentioning available players")
                for item in list(grouped.values())[:8]:
                    hit = item["hit"]
                    with st.container(border=True):
                        if hit.get("link"):
                            st.markdown(f'**[{hit["title"]}]({hit["link"]})**')
                        else:
                            st.markdown(f'**{hit.get("title") or "News report"}**')
                        st.caption(f'{hit.get("source") or "News"} · Players mentioned: '
                                   + ", ".join(item["names"][:4]))
            st.markdown("### Latest league-wide headlines")
            sources = sorted({str(item.get("source") or "Unknown") for item in articles})
            source = st.selectbox("Filter by source", ["All sources"] + sources,
                                  key="news_source_filter")
            visible = [a for a in articles if source == "All sources"
                       or str(a.get("source") or "Unknown") == source]
            for article in visible[:20]:
                with st.container(border=True):
                    title = article.get("title") or "Read story"
                    url = article.get("link")
                    if url:
                        st.markdown(f"**[{title}]({url})**")
                    else:
                        st.markdown(f"**{title}**")
                    details = " · ".join(filter(None, [article.get("source"),
                                                      article.get("published")]))
                    if details:
                        st.caption(details)


if page in ("overview", "team", "board", "players", "reports", "lab"):
    # Keyed page content remounts when navigation changes, enabling a brief
    # enter animation without altering the Sleeper data-refresh fragment.
    with st.container(key=f"view_{page}"):
        live_dashboard(page)
    st.caption(
        "Data: Sleeper API · Hashtag Basketball ADP · ESPN / Google News. Advisory only — pick in Sleeper."
    )
