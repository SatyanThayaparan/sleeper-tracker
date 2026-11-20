"""Evidence processing for Picky research reports.

The model may summarize articles, but only URLs actually cited by the
provider web-search response can be shown as independently linked evidence.
A citation proves the URL was retrieved, not that every AI interpretation
or article publication date is accurate.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from urllib.parse import urlsplit


RANKING_TERMS = ("rankings", "cheat sheet", "cheatsheet", "draft kit", "top 150",
                 "top 250", "top 100", "tiers", "draft guide")
FANTASY_TERMS = ("fantasy", "points league", "draft kit", "cheat sheet",
                 "adp", "roto", "rankings")


def publisher(url):
    host = (urlsplit(str(url or "")).hostname or "").lower()
    if host == "espn.com" or host.endswith(".espn.com"):
        return "ESPN"
    if host == "yahoo.com" or host.endswith(".yahoo.com"):
        return "Yahoo Sports"
    if host == "nba.com" or host.endswith(".nba.com"):
        return "NBA.com"
    if host == "rotowire.com" or host.endswith(".rotowire.com"):
        return "RotoWire"
    if host == "fantasypros.com" or host.endswith(".fantasypros.com"):
        return "FantasyPros"
    if host == "cbssports.com" or host.endswith(".cbssports.com"):
        return "CBS Sports"
    return "Other publication"


def classify_evidence(title, url, claim=""):
    value = " ".join((str(title), str(url), str(claim))).lower()
    if any(term in value for term in RANKING_TERMS):
        return "Expert rankings / cheat sheet"
    if any(term in value for term in FANTASY_TERMS):
        return "Fantasy analysis"
    return "NBA news / player report"


def reported_age(reported_date, *, today=None):
    """Treat reported dates as AI-provided and unverified unless checked elsewhere."""
    today = today or datetime.now(timezone.utc).date()
    raw = str(reported_date or "").strip()
    try:
        reported = date.fromisoformat(raw)
    except ValueError:
        return None, "Date not verified"
    age = (today - reported).days
    if age < 0:
        return None, "Future / unverified date"
    if age <= 7:
        return age, "Recent · ≤7 days"
    if age <= 30:
        return age, "Within 30 days"
    return age, "Older research · verify current status"


def verified_expert_evidence(player, cited_urls, *, today=None):
    """Annotate and dedupe only model claims whose URLs were web-cited.

    Do NOT upgrade an expert source into a numerical ranking, injury proof or
    evidence that all outlets agree. Treat the model-reported date as provisional.
    """
    seen = set()
    output = []
    cited = set(cited_urls)
    for item in (player.get("expert_rankings") or []) + (player.get("evidence") or []):
        if not isinstance(item, dict):
            continue
        url = str(item.get("source_url") or "")
        if url not in cited or url in seen:
            continue
        title = str(item.get("source_title") or "")[:180]
        claim = str(item.get("claim") or "")[:500]
        if not title or not claim:
            continue
        age, fresh = reported_age(item.get("reported_date"), today=today)
        category = classify_evidence(title, url, claim)
        # A ranking claim must be linked to a ranking source, not a game recap.
        if item in (player.get("expert_rankings") or []) and category != "Expert rankings / cheat sheet":
            continue
        output.append({
            "claim": claim, "source_title": title, "source_url": url,
            "reported_date": str(item.get("reported_date") or "Unverified")[:30],
            "publisher": publisher(url), "kind": category,
            "freshness": fresh, "age_days": age,
            "ranking_format": str(item.get("ranking_format") or "Unspecified")[:65],
        })
        seen.add(url)
    return output


def player_research_summary(player):
    evidence = player.get("verified_expert_evidence") or []
    ranking = [row for row in evidence if row["kind"] == "Expert rankings / cheat sheet"]
    news = [row for row in evidence if row["kind"] != "Expert rankings / cheat sheet"]
    dates_known = [row for row in evidence if row["age_days"] is not None]
    current = [row for row in dates_known if row["age_days"] <= 30]
    return {
        "sources": len(evidence),
        "ranking_sources": len(ranking),
        "news_sources": len(news),
        "recent_sources": len(current),
        "dated_sources": len(dates_known),
        "publishers": sorted({row["publisher"] for row in evidence}),
        "research_status": (
            "No independently cited sources" if not evidence else
            "Sources linked; check article dates" if len(dates_known) < len(evidence) else
            "Older source context" if not current else
            "Recent source context available"
        ),
    }


def report_research_summary(report):
    by_player = {
        str(p.get("name")): player_research_summary(p)
        for p in report.get("players", []) if isinstance(p, dict)
    }
    return {
        "players": len(by_player),
        "players_with_sources": sum(v["sources"] > 0 for v in by_player.values()),
        "players_with_rankings": sum(v["ranking_sources"] > 0 for v in by_player.values()),
        "total_verified_links": sum(v["sources"] for v in by_player.values()),
        "by_player": by_player,
    }
