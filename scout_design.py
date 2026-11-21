"""Presentation-only components for the Picky AI Scout redesign.

No HTTP requests, model calls, or draft mutations live here. Every dynamic
HTML value is escaped; CDN URLs are assembled only from numeric Sleeper IDs.
"""
from __future__ import annotations

import re
from html import escape


PHOTO_CDN = "https://sleepercdn.com/content/nba/players/thumb/"


def player_photo_url(player_id):
    """Sleeper NBA thumbnail CDN, no network calls and no guessed NBA ID."""
    identifier = str(player_id or "").strip()
    if not re.fullmatch(r"[0-9]{1,10}", identifier):
        return ""
    return f"{PHOTO_CDN}{identifier}"


def initials_for(name):
    parts = re.findall(r"[A-Za-zÀ-ÿ0-9]+", str(name or ""))
    return "".join(p[:1].upper() for p in parts[:2]) or "NBA"


def photo_html(name, player_id=None, *, size="sm"):
    """Lazy-loaded headshot over a visible initials fallback.

    A missing CDN image must not crash Streamlit or leave a blank region.
    'src' is safe because player_photo_url accepts digits only.
    """
    name_safe = escape(str(name or "NBA player"), quote=True)
    initials = escape(initials_for(name))
    url = player_photo_url(player_id)
    photo = (
        f'<img src="{url}" alt="" loading="lazy" decoding="async" '
        'referrerpolicy="no-referrer">'
        if url else ""
    )
    size = size if size in {"sm", "hero", "modal"} else "sm"
    return (
        f'<span class="picky-photo picky-photo--{size}" '
        f'role="img" aria-label="Portrait of {name_safe}">'
        f'<span class="picky-photo-fallback" aria-hidden="true">{initials}</span>'
        f'{photo}</span>'
    )


def _chip(text, kind="muted"):
    allowed = kind if kind in {"muted", "green", "amber", "blue"} else "muted"
    return f'<span class="picky-chip picky-chip--{allowed}">{escape(str(text))}</span>'


def _text(value, max_length=230):
    raw = str(value or "").strip()
    return escape(raw[:max_length] + ("…" if len(raw) > max_length else ""))


def scout_hero_html(candidate, *, summary="", risk="unknown", following_pick=None,
                    cited_count=0, researched=False, status=""):
    name = str(candidate.get("player") or "Player")
    positions = str(candidate.get("position") or "Position unknown")
    team = str(candidate.get("team") or "NBA")
    adp = candidate.get("blend_adp")
    adp_label = f"ADP {float(adp):.1f}" if isinstance(adp, (int, float)) else "ADP unavailable"
    risk_label = str(risk or "unknown").capitalize()
    pick_label = f"Next pick #{following_pick}" if following_pick else "Next pick unknown"
    notes = summary or candidate.get("roster") or "Highest ranked available option."
    source_chip = (
        _chip(f"{cited_count} cited findings", "green")
        if cited_count else _chip("Ranking preview" if not researched else "Research unverified")
    )
    return (
        '<section class="picky-hero" aria-label="Top draft recommendation">'
        '<div class="picky-hero-topline">'
        '<span class="picky-hero-eyebrow">✦ Picky AI Scout</span>'
        '<span class="picky-hero-status">Top available recommendation</span></div>'
        '<div class="picky-hero-body">'
        f'{photo_html(name, candidate.get("player_id"), size="hero")}'
        '<div class="picky-hero-info">'
        '<div class="picky-hero-kicker">YOUR DRAFT BOARD · #1 AVAILABLE</div>'
        f'<h3>{escape(name)}</h3>'
        f'<p class="picky-hero-meta">{escape(team)} · {escape(positions)} · {escape(adp_label)}</p>'
        f'<p class="picky-hero-summary">{_text(notes, 290)}</p>'
        '<div class="picky-hero-chips">'
        f'{source_chip}'
        f'{_chip(pick_label, "blue")}'
        f'{_chip(f"Wait risk: {risk_label}", "amber" if risk == "elevated" else "muted")}'
        '</div></div></div></section>'
    )


def scout_candidate_html(candidate, rank, *, summary="", risk="unknown",
                         cited_count=0, research_state="ranking"):
    name = str(candidate.get("player") or "Player")
    team = str(candidate.get("team") or "NBA")
    positions = str(candidate.get("position") or "—")
    adp = candidate.get("blend_adp")
    adp_label = f"ADP {float(adp):.1f}" if isinstance(adp, (float, int)) else "ADP n/a"
    rank_value = candidate.get("sleeper_search_rank")
    sleeper_label = f"Sleeper search #{rank_value}" if rank_value is not None else "Sleeper search n/a"
    reason = summary or candidate.get("roster") or "Review this candidate's roster fit."
    source_label = (f"{cited_count} cited findings" if cited_count else
                    "AI summary · unverified" if research_state in {"researched", "search_only"} else
                    "Ranking preview")
    risk_label = f"Wait risk: {str(risk or 'unknown').capitalize()}"
    return (
        '<div class="picky-player-row">'
        '<span class="picky-player-rank" aria-label="Picky rank">'
        f'#{rank}</span>'
        f'{photo_html(name, candidate.get("player_id"))}'
        '<div class="picky-player-content">'
        '<div class="picky-player-title-line">'
        f'<strong>{escape(name)}</strong>'
        f'<span class="picky-player-team">{escape(team)} · {escape(positions)}</span>'
        '</div>'
        f'<p class="picky-player-summary">{_text(reason, 275)}</p>'
        '<div class="picky-player-metrics">'
        f'{_chip(adp_label)}'
        f'{_chip(sleeper_label)}'
        f'{_chip(source_label, "green" if cited_count else "muted")}'
        f'{_chip(risk_label, "amber" if risk == "elevated" else "muted")}'
        '</div></div></div>'
    )


def details_header_html(candidate, *, citations=0):
    name = str(candidate.get("player") or "Player")
    team = str(candidate.get("team") or "NBA")
    positions = str(candidate.get("position") or "Position unknown")
    adp = candidate.get("blend_adp")
    adp_label = f"ADP {float(adp):.1f}" if isinstance(adp, (int, float)) else "ADP unavailable"
    sleeper_rank = candidate.get("sleeper_search_rank")
    rank_label = f"Sleeper search #{sleeper_rank}" if sleeper_rank is not None else "Search rank unavailable"
    return (
        '<div class="picky-modal-hero">'
        f'{photo_html(name, candidate.get("player_id"), size="modal")}'
        '<div class="picky-modal-identity">'
        '<div class="picky-modal-eyebrow">✦ PLAYER SCOUTING REPORT</div>'
        f'<h3>{escape(name)}</h3>'
        f'<p>{escape(team)} · {escape(positions)}</p>'
        '<div class="picky-hero-chips">'
        f'{_chip(adp_label)}{_chip(rank_label)}'
        f'{_chip(f"{citations} cited findings", "green" if citations else "muted")}'
        '</div></div></div>'
    )


def insight_panel_html(title, body, *, kind="normal", icon="✦"):
    kind = kind if kind in {"normal", "green", "amber"} else "normal"
    text = _text(body or "No additional details available.", 950)
    return (
        f'<section class="picky-insight picky-insight--{kind}">'
        f'<div class="picky-insight-title"><span aria-hidden="true">{escape(icon)}</span>'
        f'<strong>{escape(str(title))}</strong></div>'
        f'<p>{text}</p></section>'
    )


def source_heading_html(publisher, kind, freshness):
    return (
        '<div class="picky-source-heading">'
        '<div class="picky-source-icon" aria-hidden="true">↗</div>'
        '<div>'
        f'<strong>{_text(publisher, 75)}</strong>'
        f'<small>{_text(kind, 85)} · {_text(freshness, 80)}</small>'
        '</div></div>'
    )
