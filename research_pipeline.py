"""Two-stage NBA fantasy expert scouting.

STAGE 1: a per-player Responses API web-search call gathers retrieved source
metadata and a short grounded search brief.
STAGE 2: a separate *no-web-tool* model call turns that brief, those sources,
and Picky's actual scoring/roster context into a concise draft assessment.

Web-retrieved URL is provenance, not proof that every model-generated claim is
true. Claims only get a linked source after the source ID was provided by stage 1.
"""
from __future__ import annotations

import json
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from expert_research import verified_expert_evidence, player_research_summary

MAX_SOURCE_ITEMS = 10
STAT_KEYS = ("projected_fppg", "upside_fppg", "floor_fppg",
             "stdev_fppg", "games_per_week", "availability_pct")


def read_field(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def normalized_source_url(url):
    """Strip only tracking/query fragments, never collapse to a publisher home."""
    if not isinstance(url, str):
        return ""
    try:
        parts = urlsplit(url.strip())
        host = (parts.hostname or "").lower()
        if (parts.scheme not in ("http", "https") or not host or
                host in ("localhost", "127.0.0.1", "::1")):
            return ""
        path = parts.path.rstrip("/") or "/"
        # Preserve content-identifying query keys, discard only tracking keys.
        # ?id=123 and ?id=456 must not match just because the path does.
        query = urlencode(sorted(
            (key, value) for key, value in parse_qsl(
                parts.query, keep_blank_values=True
            ) if not (key.lower().startswith("utm_") or key.lower() in
                      ("utm", "tracking", "fbclid", "gclid", "ref", "source", "mc_cid", "mc_eid"))
        ))
        return urlunsplit(("https", host.removeprefix("www."), path, query, ""))
    except ValueError:
        return ""


def extract_search_sources(response):
    """Read web_search action.sources and message url_citation annotations."""
    result, seen = [], {}
    for item in read_field(response, "output", []) or []:
        action = read_field(item, "action")
        candidates = []
        if read_field(item, "type") == "web_search_call":
            candidates.extend(read_field(action, "sources", []) or [])
        for part in read_field(item, "content", []) or []:
            candidates.extend(read_field(part, "annotations", []) or [])
        for source in candidates:
            raw = read_field(source, "url")
            key = normalized_source_url(raw)
            if not key:
                continue
            title = str(read_field(source, "title") or "Retrieved web page")[:180]
            if key in seen:
                existing = result[seen[key]]
                if (existing["title"] == "Retrieved web page"
                        and title != "Retrieved web page"):
                    existing["title"] = title
                continue
            seen[key] = len(result)
            result.append({
                "id": "S" + str(len(result) + 1),
                "url": str(raw), "title": title,
            })
    return result[:MAX_SOURCE_ITEMS]


def projection_snapshot(candidate):
    """Use actual numeric model input, never convert ADP to fantasy points."""
    snapshot = {}
    lockin = candidate.get("lockin") or {}
    if lockin.get("available"):
        snapshot["lockin_opportunity_points"] = lockin.get("points")
        snapshot["lockin_method"] = lockin.get("method")
    for key in STAT_KEYS:
        val = candidate.get(key)
        if isinstance(val, (float, int)) and val == val:
            snapshot[key] = val
    return snapshot


def stage1_search(client, name, *, model):
    prompt = (
        f"Research NBA fantasy basketball player {name!r} for a Sleeper fantasy "
        "points/Lock-In draft. Search recent player-specific ESPN NBA/fantasy, "
        "Yahoo Fantasy, NBA.com, official team news and other relevant sports "
        "analysis. Also look for 2026-27 ESPN or Yahoo points-league cheat "
        "sheets/rankings that explicitly discuss this player. In 180 words max, "
        "summarize ONLY verifiable recent role, playing time, health, fantasy "
        "projections or expert outlook. Distinguish dated preseason rankings "
        "from fresh updates and category-league from points-league claims. "
        "Supply inline citations to the articles you actually consulted. "
        "If no reliable player-specific findings are accessible, explicitly "
        "say so. Never invent URLs, expert ranks, injuries or fantasy points."
    )
    response = client.responses.create(
        model=model,
        input=prompt,
        tools=[{"type": "web_search", "search_context_size": "medium"}],
        tool_choice="required",
        include=["web_search_call.action.sources"],
        max_output_tokens=1050,
        store=False,
    )
    summary = str(read_field(response, "output_text") or "").strip()[:2800]
    sources = extract_search_sources(response)
    if not summary:
        status = read_field(response, "status") or "unknown"
        raise RuntimeError(f"Web research returned no summary (status={status}).")
    return {"brief": summary, "sources": sources}


def stage2_analyze(client, candidate, search_result, *,
                   context=None, open_slots=None, model):
    """Analysis never uses web tools and may cite only stage-1 source IDs."""
    name = str(candidate.get("player") or "")
    sources = search_result.get("sources") or []
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "summary": {"type": "string"},
            "role_outlook": {"type": "string"},
            "availability_risk": {"type": "string"},
            "draft_fit": {"type": "string"},
            "why_now": {"type": "string"},
            "expert_take": {"type": "string"},
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source_id": {"type": "string"},
                        "claim": {"type": "string"},
                        "reported_date": {"type": "string"},
                        "ranking_format": {"type": "string"},
                    },
                    "required": ["source_id", "claim", "reported_date",
                                 "ranking_format"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["name", "summary", "role_outlook", "availability_risk",
                     "draft_fit", "why_now", "expert_take", "findings"],
        "additionalProperties": False,
    }
    payload = {
        "player": {
            "name": name, "nba_team": candidate.get("team"),
            "eligible_positions": candidate.get("position"),
            "injury_tag": candidate.get("injury"),
            "rank_score_not_fantasy_points": candidate.get("score"),
            "blend_adp": candidate.get("blend_adp"),
            "sleeper_search_rank_not_fantasy_rank":
                candidate.get("sleeper_search_rank"),
            "roster_fit": candidate.get("roster"),
            "eligible_position_depth": candidate.get("eligible_depth"),
            "projection_data": projection_snapshot(candidate),
        },
        "league_format": "Sleeper NBA Lock-In fantasy points",
        "open_slots": list(open_slots or [])[:16],
        "eligible_roster_counts": (context or {}).get("roster_eligible_counts") or {},
        "current_pick": (context or {}).get("current_pick"),
        "following_pick": (context or {}).get("following_pick"),
        "search_brief_model_generated": search_result.get("brief") or "",
        "sources_retrieved_not_independently_fact_checked": sources,
    }
    response = client.responses.create(
        model=model,
        instructions=(
            "You are Picky AI Scout. Produce an accurate, helpful fantasy "
            "points draft explanation for ONE player. Use the supplied "
            "search brief plus source list and roster data. The brief is "
            "model-generated and may be wrong: do not assert claims not "
            "supported by it. In the summary describe 2-3 specific useful "
            "takeaways, or clearly state when no outside findings are known. "
            "Never describe ADP or a ranking score as fantasy points. "
            "Consider actual eligible roster counts, player production "
            "when supplied, opportunity, injury, and whether the player "
            "may be gone by the following pick. Do not invent projections, "
            "injuries, source dates, or numerical expert ranks. Only emit "
            "finding source_ids listed in sources; for uncited observations "
            "leave findings empty and label the summary as unverified. "
            "An article being retrieved does not prove it discusses "
            "the player. Only link it if the search brief explicitly "
            "attributes a player-specific finding to it. "
            "Keep fields concise. Name must match the supplied player."
        ),
        input=json.dumps(payload, ensure_ascii=False, default=str),
        text={"format": {"type": "json_schema", "name": "picky_player_analysis",
                         "strict": True, "schema": schema}},
        max_output_tokens=1300,
        store=False,
    )
    raw = str(read_field(response, "output_text") or "").strip()
    try:
        answer = json.loads(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Unable to parse player analysis response.") from exc
    if not isinstance(answer, dict) or answer.get("name") != name:
        raise RuntimeError("Analysis returned a different player than requested.")

    sources_by_id = {source["id"]: source for source in sources}
    evidence, expert_rankings = [], []
    seen = set()
    for item in answer.get("findings", [])[:5]:
        if not isinstance(item, dict):
            continue
        src = sources_by_id.get(item.get("source_id"))
        claim = str(item.get("claim") or "").strip()
        if not src or not claim or src["url"] in seen:
            continue
        seen.add(src["url"])
        # Match the claim to a retrieved ID, not to a model-invented URL.
        evidence.append({
            "claim": claim[:420],
            "source_title": src["title"],
            "source_url": src["url"],
            "reported_date": str(item.get("reported_date") or "Unverified")[:30],
        })
        category_text = (src["title"] + " " + src["url"]).lower()
        if any(term in category_text for term in (
            "ranking", "cheat sheet", "cheatsheet", "top 250", "draft kit"
        )):
            expert_rankings.append({
                **evidence[-1],
                "ranking_format": str(item.get("ranking_format") or "Unspecified")[:60],
            })
    player = {
        "name": name,
        "role_outlook": str(answer.get("role_outlook") or "")[:420],
        "recent_findings": str(answer.get("summary") or "")[:800],
        "availability_risk": str(answer.get("availability_risk") or "")[:360],
        "draft_fit": str(answer.get("draft_fit") or "")[:420],
        "why_now": str(answer.get("why_now") or "")[:360],
        "evidence_date": "Unverified",
        "expert_take": str(answer.get("expert_take") or "")[:500],
        "expert_rankings": expert_rankings,
        "evidence": evidence,
    }
    player["verified_expert_evidence"] = verified_expert_evidence(
        player, {source["url"] for source in sources}
    )
    return {"player": player,
            "sources": [{"title": src["title"], "url": src["url"]}
                        for src in sources],
            "source_status": player_research_summary(player),
            "search_brief": str(search_result.get("brief") or "")[:2800]}


def research_player(client, candidate, *, open_slots, context=None,
                    model="gpt-4.1-mini"):
    name = str(candidate.get("player") or "")
    if not name:
        raise ValueError("Cannot research an unnamed player.")
    search = stage1_search(client, name, model=model)
    return stage2_analyze(client, candidate, search, open_slots=open_slots,
                          context=context, model=model)
