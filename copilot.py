"""Paid, opt-in AI follow-up conversation using already researched draft context.

No web-search tool is passed to this workflow. Context is scoped to the current
draft turn and excludes account IDs and private settings.
"""
import json

from ai import chat_complete

MAX_FOLLOWUPS = 8


def context_snapshot(candidates, *, role_counts, next_pick, report=None):
    short = [{
        "name": str(row.get("player") or "")[:90],
        "team": str(row.get("team") or "")[:12],
        "positions": str(row.get("position") or "")[:40],
        "adp": row.get("blend_adp"),
        "lockin": row.get("lockin") if row.get("lockin", {}).get("available") else None,
        "fit_note": str(row.get("roster") or "")[:260],
        "injury": str(row.get("injury") or "")[:30],
    } for row in candidates[:5]]
    names = {row["name"] for row in short}
    evidence = {}
    if isinstance(report, dict):
        for row in report.get("players", []):
            if isinstance(row, dict) and row.get("name") in names:
                evidence[row["name"]] = {
                    "findings": str(row.get("recent_findings") or "")[:380],
                    "injury": str(row.get("availability_risk") or "")[:170],
                    "evidence": [{
                        "claim": str(item.get("claim") or "")[:260],
                        "url": str(item.get("source_url") or "")[:360],
                        "reported_date": str(item.get("reported_date") or "")[:25],
                    } for item in (row.get("evidence") or [])[:2] if isinstance(item, dict)]
                }
    return {
        "available_candidates": short,
        "eligible_role_counts": {key: int(role_counts.get(key, 0))
                                 for key in ("PG", "SG", "SF", "PF", "C")},
        "current_pick": next_pick,
        "verified_report_findings": evidence,
    }


def compare_question(first, second, context):
    names = {row["name"] for row in context.get("available_candidates", [])}
    if first == second or first not in names or second not in names:
        raise ValueError("Choose two different available shortlisted players.")
    return ("Compare " + first + " versus " + second +
            " for my roster. Discuss Lock-In evidence if available, "
            "points value, injury, depth, ADP and risk of waiting; "
            "tell me what cannot be verified.")


def ask_copilot(session, *, key, context, question, completion_fn=chat_complete):
    if not key or not isinstance(context, dict):
        raise ValueError("An active draft-turn context is required.")
    question = str(question or "").strip()
    if not 3 <= len(question) <= 500:
        raise ValueError("Question must contain 3–500 characters.")
    history = session.setdefault("picky_copilot_history", {})
    turns = history.setdefault(key, [])
    if len(turns) >= MAX_FOLLOWUPS:
        raise RuntimeError("AI Copilot's per-turn question limit has been reached.")
    # Request is manual. No browsing/web-search tools are exposed here.
    system = (
        "You are Picky, a concise Sleeper NBA Lock-In draft advisor. "
        "Use only the provided current draft context and previously verified "
        "web evidence; you have NO live web or API access in this request. "
        "Never invent stats, current injuries, sources, player availability "
        "odds or Lock-In projections. A missing lineup slot does not mean "
        "the team lacks eligible players. Distinguish projected lock-in "
        "scores from ADP and ranking proxies. Assess upside, score, roster "
        "depth, lineup flexibility, injury risk, and why draft now vs wait. "
        "Explicitly acknowledge missing data and explain trade-offs. "
        "Do not suggest drafting players outside the shortlist."
    )
    recent = turns[-3:]
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Public draft context: " +
         json.dumps(context, ensure_ascii=False, default=str)[:12000]},
    ]
    for turn in recent:
        messages.extend([
            {"role": "user", "content": turn["question"]},
            {"role": "assistant", "content": turn["answer"]},
        ])
    messages.append({"role": "user", "content": question})
    response = completion_fn(messages, model="gpt-4.1-mini",
                             temperature=0.2, max_tokens=650)
    answer = str(response or "").strip()
    if not answer:
        raise RuntimeError("Picky returned an empty response. No question was saved.")
    turns.append({"question": question, "answer": answer[:4500]})
    return answer
