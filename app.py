import re
from datetime import datetime, timezone
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st
import feedparser

from adp import ADP_URL, fetch_adp_rows, match_adp
from recommend import build_recommendations
from theme import (
    APP_NAME,
    APP_TAGLINE,
    ICON_PATH,
    inject_css,
    render_hero,
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


def value_or(metadata, key, default=""):
    return (metadata or {}).get(key) or default


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


def render_pick_card(title, row, empty_text, *, badge: str | None = None):
    with st.container(border=True):
        heading = title
        if badge:
            heading = f'{title} <span class="fx-rank">{badge}</span>'
            st.markdown(f"### {heading}", unsafe_allow_html=True)
        else:
            st.markdown(f"### {title}")
        if not row:
            st.caption(empty_text)
            return
        position = row["position"] or "Position unavailable"
        team = row["team"] or "Free agent"
        st.markdown(f'**{row["player"]}**')
        st.write(f'{position} · {team} · Injury: {row["injury"]}')
        line = adp_line(row)
        if line:
            st.caption(line)
        for reason in row.get("reasons") or []:
            st.markdown(f"- {reason}")
        render_references(row)


def option_note(row):
    notes = []
    role = row.get("variety_role")
    have = row.get("role_have") or {}
    if role and have:
        count = int(have.get(role, 0))
        lowest = min(int(value) for value in have.values())
        if count == 0:
            notes.append(f"You have no {role} yet")
        elif count == lowest:
            notes.append(f"You have {count} {role}, fewer than your other roles")
        else:
            notes.append(f"You already have {count} {role}")
    roster = row.get("roster") or ""
    if roster and not roster.startswith(("Select your Sleeper", "You have", "You already")):
        notes.append(roster.rstrip("."))
    tone = row.get("tone")
    if tone == "positive":
        notes.append("Positive headline")
    elif tone == "caution":
        notes.append("Caution headline")
    elif tone == "negative":
        notes.append("Negative headline")
    elif row.get("injury") not in (None, "", "—"):
        notes.append(f"Injury {row['injury']}")
    return " · ".join(notes)


def render_options(options):
    with st.container(border=True):
        st.markdown("### Best options")
        if not options:
            st.caption("No best options yet.")
            return
        if any(row.get("role_have") for row in options):
            st.caption(
                "One player for each role, starting with the positions you have filled least."
            )
        else:
            st.caption(
                "One player at each position, so the list is not all the same role. Select your account to put the roles you still need first."
            )
        for index, row in enumerate(options, 1):
            position = row["position"] or "Position unavailable"
            team = row["team"] or "Free agent"
            line = adp_line(row)
            query = quote(f"{row['player']} NBA")
            links = f"[ESPN](https://www.espn.com/search/_/q/{query}) · [News](https://news.google.com/search?q={query}%20injury)"
            if row.get("adp_url"):
                links += f" · [ADP]({row['adp_url']})"
            role = row.get("variety_role")
            detail = f"For {role} · {position} · {team}" if role else f"{position} · {team}"
            if line:
                detail += f" · {line}"
            note = option_note(row)
            rank = '<span class="fx-rank">S-RANK</span>' if index == 1 else ""
            st.markdown(
                f'{index}. **{row["player"]}**{rank} — {detail} · {links}',
                unsafe_allow_html=True,
            )
            if note:
                st.caption(note)
            for hit in (row.get("hits") or [])[:1]:
                if hit.get("link"):
                    st.markdown(
                        f'[{hit["title"]}]({hit["link"]}) — {hit.get("source") or "News"}'
                    )


def render_picks(board, roster_names, user_selected):
    if not board.get("options") and not board.get("rows"):
        st.warning(
            "No pick options yet. Connect the draft, and make sure the ADP list or a projection CSV is available."
        )
        return
    if user_selected:
        st.markdown(
            "**Your team:** "
            + (", ".join(roster_names) if roster_names else "no players drafted yet")
        )
        if board.get("open_slots"):
            st.markdown(
                "**Open starter slots:** "
                + ", ".join(str(slot) for slot in board["open_slots"])
            )
    else:
        st.caption("Select your Sleeper account in the sidebar to include your roster.")
    if board.get("reluctant"):
        st.warning(
            "Every close alternative also has an injury or a negative headline. These options still include that risk."
        )
    render_options(board.get("options") or [])
    sleeper_col, fade_col = st.columns(2)
    with sleeper_col:
        render_pick_card(
            "Sleeper pick",
            board.get("sleeper"),
            "No later ADP stands out in the next six rounds. A sleeper needs a positive headline, or Yahoo, ESPN, or Fantrax taking them at least 8 spots earlier than the blend.",
            badge="VALUE",
        )
    with fade_col:
        render_pick_card(
            "Fade",
            board.get("fade"),
            "No high-ADP player is clearly ruled out by an injury tag or headline.",
            badge="CAUTION",
        )


with st.sidebar:
    st.markdown("### Connect your draft")
    draft_link = st.text_input("Your Sleeper draft link or ID", value=DEFAULT_DRAFT_URL)
    draft_id_override = draft_id_from_link(draft_link)
    league_id = st.text_input(
        "League ID (automatically discovered from draft; optional)",
        placeholder="Optional override",
    )
    my_user = st.text_input("Your Sleeper username or user ID (optional)")
    refresh = st.select_slider(
        "Pick refresh interval",
        options=[10, 15, 30, 60],
        value=15,
        format_func=lambda x: f"{x} sec",
    )
    st.caption(
        "Auto-refresh is on when a league or draft ID is supplied. Source articles refresh every 10 minutes. No account password needed."
    )
    st.divider()
    st.markdown("### Rankings / projections")
    uploaded = st.file_uploader("Upload your player rankings or projections CSV", type=["csv"])
    st.download_button(
        "Download Lock-In projection template",
        data="player,projected_fppg,upside_fppg,floor_fppg,games_per_week,availability_pct\n",
        file_name="lockin_projection_template.csv",
        mime="text/csv",
    )
    upside_weight = st.slider("Lock-In upside emphasis (%)", 0, 80, 35, 5)
    safety_weight = st.slider("Consistency / floor emphasis (%)", 0, 60, 20, 5)
    st.caption(
        "Optional CSV columns: upside_fppg, floor_fppg, games_per_week, availability_pct (0–100). All fantasy point values should use league-specific scoring. Missing optional data receives no invented upside or floor bonus."
    )
    risk_weight = st.slider("Injury status penalty (%)", 0, 50, 15, 5)
    fit_bonus = st.slider("Open lineup fit bonus (%)", 0, 25, 15, 1)
    st.caption(
        "Baseline is Hashtag Basketball ADP across Yahoo, ESPN, and Fantrax. Headlines from ESPN and Google News move a player up, down, or onto the fade list. A projection CSV replaces the ADP baseline."
    )

render_hero(
    title=APP_NAME,
    subtitle=f"{APP_TAGLINE} · Hashtag Basketball ADP · roster fit · ESPN and news tone — advisory only; make picks in Sleeper.",
    live=bool(league_id or draft_id_override),
)

if not league_id and not draft_id_override:
    st.info(
        "Enter a Sleeper league ID (or draft ID) in the sidebar to connect. Upload rankings/projections to activate recommendations."
    )
    st.stop()

try:
    if not draft_id_override and not league_id:
        st.error("Enter a valid Sleeper draft URL or draft ID, or a league ID.")
        st.stop()
    if draft_id_override:
        draft = api_get(f"draft/{quote(draft_id_override)}")
        draft_id = str(draft.get("draft_id") or draft_id_override)
        meta = draft.get("metadata") or {}
        discovered_league_id = str(draft.get("league_id") or meta.get("league_id") or "")
        league_id = discovered_league_id or league_id
        if not discovered_league_id:
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
    st.info(
        "The provided draft ID is prefilled. Check that the draft is accessible publicly and try again."
    )
    st.stop()

try:
    players = player_map()
    if not isinstance(players, dict):
        players = {}
except Exception as e:
    players = {}
    st.warning(
        f"NBA player directory unavailable: {e}. Pick names may still appear via draft metadata; rankings matching by name may fail."
    )

try:
    if uploaded:
        ranking = normalize_rankings(pd.read_csv(uploaded), players)
        st.sidebar.success(f"{len(ranking)} ranked players matched")
    else:
        ranking = pd.DataFrame()
except Exception as e:
    ranking = pd.DataFrame()
    st.sidebar.error(f"Ranking file problem: {e}")

adp_frame = pd.DataFrame()
adp_updated = ""
if ranking.empty:
    try:
        adp_payload = cached_adp_rows()
        adp_frame = match_adp(adp_payload.get("players") or [], players)
        adp_updated = adp_payload.get("updated") or ""
        if adp_frame.empty:
            st.sidebar.warning(
                "Hashtag Basketball ADP did not match the Sleeper player list. Falling back to Sleeper search rank."
            )
        else:
            stamp = f" · updated {adp_updated}" if adp_updated else ""
            st.sidebar.caption(
                f"Hashtag Basketball ADP: {len(adp_frame)} players matched to Sleeper{stamp}."
            )
    except Exception as e:
        st.sidebar.warning(
            f"Hashtag Basketball ADP unavailable: {e}. Falling back to Sleeper search rank."
        )

my_user_id = ""
if not my_user and league_id:
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
            selected = st.sidebar.selectbox(
                "Select your team / Sleeper account", ["Not selected"] + list(options)
            )
            my_user_id = options.get(selected, "")
    except Exception as e:
        st.sidebar.caption(f"League user lookup unavailable: {e}")
if my_user:
    try:
        user = api_get(f"user/{quote(my_user)}")
        my_user_id = str(user["user_id"])
    except Exception as e:
        st.sidebar.warning(f"Could not identify username: {e}")

try:
    draft = api_get(f"draft/{quote(draft_id)}")
except Exception as e:
    st.error(f"Cannot load draft {draft_id}: {e}")
    st.stop()

with st.container(border=True):
    league_name = league.get("name") or "Connected Draft"
    st.markdown(f'<div class="fx-section-label">{league_name}</div>', unsafe_allow_html=True)
    st.caption(
        f'Draft ID: {draft_id} • League ID: {league_id or "unavailable"} • Draft status: {draft.get("status", "unknown")} • Scoring: Lock-In (user-selected)'
    )
    with st.expander("Scoring rules retrieved from your Sleeper league"):
        st.json(
            {
                "scoring_settings": league.get("scoring_settings") or {},
                "roster_positions": league.get("roster_positions") or [],
                "draft_settings": draft.get("settings") or {},
            }
        )
        st.caption(
            "Compare imported player projections with these exact scoring settings; the app does not automatically convert NBA box scores into your custom fantasy projections."
        )


@st.fragment(run_every=f"{refresh}s")
def live_dashboard():
    try:
        api_get.clear()
        picks = api_get(f"draft/{quote(draft_id)}/picks") or []
        if not isinstance(picks, list):
            raise ValueError("Unexpected draft pick response")
        fresh_draft = api_get(f"draft/{quote(draft_id)}")
    except Exception as e:
        st.error(f"Live picks unavailable: {e}")
        return
    picked_ids = {str(p.get("player_id")) for p in picks if p.get("player_id") is not None}
    picks = sorted(picks, key=lambda p: int(p.get("pick_no") or 0))
    teams = int((fresh_draft.get("settings") or {}).get("teams") or (league.get("total_rosters") or 0))
    rounds = int((fresh_draft.get("settings") or {}).get("rounds") or 0)
    next_pick = len(picks) + 1
    with st.container(border=True):
        st.markdown('<div class="fx-section-label">Draft pulse</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Picks completed", len(picks))
        c2.metric("Next overall pick", next_pick)
        c3.metric("Draft teams", teams or "—")
        c4.metric("Draft status", fresh_draft.get("status", "unknown"))
        st.caption(
            "Last checked: "
            + datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
            + " • Refreshing every "
            + str(refresh)
            + " sec"
        )

    roster_ids = []
    if my_user_id:
        for p in picks:
            if str(p.get("picked_by")) == my_user_id and p.get("player_id") is not None:
                roster_ids.append(str(p["player_id"]))
    elif my_user:
        st.warning("Could not resolve your roster; enter a valid Sleeper username.")
    my_slot = (fresh_draft.get("draft_order") or {}).get(my_user_id)
    if not my_slot and my_user_id:
        for k, v in (fresh_draft.get("draft_order") or {}).items():
            if str(k) == my_user_id:
                my_slot = v
    if my_slot and teams:
        left = []
        for n in range(next_pick, teams * rounds + 1):
            rd = (n - 1) // teams + 1
            slot = (
                ((n - 1) % teams + 1)
                if fresh_draft.get("type") != "snake" or rd % 2
                else (teams - (n - 1) % teams)
            )
            if slot == int(my_slot):
                left.append(n)
        st.info(
            "Your upcoming picks (estimated; traded picks/keepers can alter this): "
            + ", ".join(str(n) for n in left[:5])
            if left
            else "No upcoming picks detected."
        )

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
    render_picks(board, [player_name(pid, players, picks) for pid in roster_ids], bool(my_user_id))

    tab1, tab2, tab3 = st.tabs(
        ["Best available", "Draft board", "Reports & injury news"]
    )
    with tab1:
        if not board["rows"]:
            if board["origin"] == "projection":
                st.warning("No available players matched your rankings file.")
            else:
                st.warning(
                    "No available players could be ranked. The NBA player directory did not load, and no projection CSV is uploaded."
                )
        else:
            if board["origin"] == "adp":
                stamp = f" Updated {adp_updated}." if adp_updated else ""
                st.caption(
                    f"Order starts from the [Hashtag Basketball ADP blend]({ADP_URL}) of Yahoo, ESPN, and Fantrax.{stamp} Your open roster slots, Sleeper injury tags, and ESPN or Google headlines then choose the best pick, sleeper, and fade."
                )
            elif board["origin"] == "search_rank":
                st.caption(
                    "ADP did not load. Order starts from Sleeper search rank for players still available, then your open roster slots, Sleeper injury tags, and headline tone."
                )
            else:
                st.caption(
                    "Order uses your imported projections, your open roster slots, Sleeper injury tags, and headline tone. A player described as out is passed over when a healthier option is close in value."
                )
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
            shown = extra + shown
            shown = shown[:75]
            records = []
            for rank_index, row in enumerate(shown, 1):
                record = {
                    "#": rank_index,
                    "Player": row["player"],
                    "Position": row["position"],
                    "Team": row["team"],
                    "Injury status": row["injury"],
                    "Roster": row["roster"],
                    "Media": row["media"],
                    "Pick": labels.get(row["player_id"], ""),
                }
                if board["origin"] == "adp":
                    record["Blend ADP"] = (
                        None if row.get("blend_adp") is None else round(row["blend_adp"], 1)
                    )
                    record["ESPN ADP"] = (
                        None if row.get("espn_adp") is None else round(row["espn_adp"], 1)
                    )
                elif board["origin"] == "projection":
                    record["Adjusted score"] = round(float(row["score"]), 2)
                else:
                    record["Baseline"] = row["baseline"]
                records.append(record)
            st.dataframe(pd.DataFrame(records), hide_index=True, width="stretch")
            st.download_button(
                "Export available rankings",
                pd.DataFrame(records).to_csv(index=False),
                "best_available.csv",
                "text/csv",
                key="export_avail",
            )
    with tab2:
        rows = []
        for p in reversed(picks[-75:]):
            rows.append(
                {
                    "Overall": p.get("pick_no"),
                    "Round": p.get("round"),
                    "Player": player_name(p.get("player_id"), players, picks),
                    "User": p.get("picked_by"),
                    "Roster": p.get("roster_id"),
                    "Position": ", ".join(
                        player_positions(players.get(str(p.get("player_id")), {}))
                    ),
                }
            )
        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        else:
            st.info("No completed draft picks yet.")
        if roster_ids:
            st.markdown(
                "**Your drafted players**: "
                + ", ".join(player_name(pid, players, picks) for pid in roster_ids)
            )
    with tab3:
        st.caption(
            "RSS sources: ESPN NBA and Google News search. Stories are linked to originals, and may be stale or incomplete. Verify injuries and coaching decisions before drafting. Matching headlines also move the projected best pick."
        )
        if not articles:
            st.warning("News feeds are unavailable right now. Refresh later or consult primary sources.")
        else:
            grouped = {}
            for row in board["rows"][:80]:
                for hit in row.get("hits") or []:
                    bucket = grouped.setdefault(hit["title"], {"hit": hit, "names": []})
                    if row["player"] not in bucket["names"]:
                        bucket["names"].append(row["player"])
            relevant = list(grouped.values())
            if relevant:
                st.markdown("**Reports mentioning top available players**")
                for item in relevant[:12]:
                    article = item["hit"]
                    st.markdown(
                        f'- [{article["title"]}]({article["link"]}) — {article["source"]} • {", ".join(item["names"])} · {article["tone"]}'
                    )
            st.markdown("**Latest league-wide headlines**")
            for article in articles[:20]:
                st.markdown(
                    f'- [{article["title"]}]({article["link"]}) — {article["source"]}'
                )


live_dashboard()
st.divider()
st.caption(
    "Data attribution: Sleeper API and Hashtag Basketball ADP (Yahoo, ESPN, Fantrax). Headlines link to ESPN and Google News. Draft selections are always made in Sleeper; this dashboard is advisory only."
)
