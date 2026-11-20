"""Realized draft-survival evaluation from snapshots captured *before* picks.

This is not a historical point-scoring backtest: no unavailable archived
projection data or counterfactual 'what if I drafted X' results are invented.
Records are per Streamlit session and can be exported for later inspection.
"""
import csv
import io

MAX_SNAPSHOTS = 120


def record_snapshot(session, *, draft_id, upcoming_pick, following_pick,
                    current_pick, candidates, now=None):
    if not draft_id or not upcoming_pick or not candidates:
        return False
    key = f"{draft_id}:{upcoming_pick}"
    snapshots = session.setdefault("picky_eval_snapshots", {})
    if key in snapshots:
        return False
    if len(snapshots) >= MAX_SNAPSHOTS:
        return False
    snapshots[key] = {
        "draft_id": str(draft_id),
        "pick": int(upcoming_pick),
        "following_pick": int(following_pick) if following_pick else None,
        "observed_pick": int(current_pick),
        "candidates": [
            {"player_id": str(row.get("player_id") or ""),
             "name": str(row.get("player") or "")[:90],
             "adp": row.get("blend_adp"),
             "lockin_points": (row.get("lockin") or {}).get("points"),
             "rank": i + 1}
            for i, row in enumerate(candidates[:5]) if row.get("player_id")
        ],
    }
    return True


def evaluate_snapshots(snapshots, picks):
    chosen = {}
    observed_max = 0
    for pick in picks or ():
        try:
            number = int(pick.get("pick_no"))
        except (ValueError, TypeError, AttributeError):
            continue
        observed_max = max(observed_max, number)
        pid = str(pick.get("player_id") or "")
        if pid and pid not in chosen:
            chosen[pid] = number
    rows = []
    for snapshot in (snapshots or {}).values():
        after = snapshot.get("following_pick")
        current = snapshot.get("observed_pick")
        for player in snapshot.get("candidates", []):
            taken_at = chosen.get(player.get("player_id"))
            if after is None:
                state = "unknown"
            elif taken_at is not None and current <= taken_at < after:
                state = "taken before next pick"
            elif taken_at is not None and taken_at < current:
                state = "invalid snapshot"
            elif observed_max >= after - 1:
                state = "survived to next pick"
            else:
                state = "pending"
            rows.append({
                "draft": snapshot.get("draft_id"),
                "upcoming_pick": snapshot.get("pick"),
                "following_pick": after,
                "name": player.get("name"),
                "shortlist_rank": player.get("rank"),
                "adp": player.get("adp"),
                "lockin_points": player.get("lockin_points"),
                "actual_pick": taken_at,
                "outcome": state,
            })
    return rows


def evaluation_summary(rows):
    finished = [r for r in rows if r["outcome"] in (
        "taken before next pick", "survived to next pick"
    )]
    return {
        "reviewed": len(finished),
        "survived": sum(r["outcome"] == "survived to next pick" for r in finished),
        "taken": sum(r["outcome"] == "taken before next pick" for r in finished),
        "pending": sum(r["outcome"] == "pending" for r in rows),
        "unverifiable": sum(r["outcome"] in ("unknown", "invalid snapshot") for r in rows),
    }



def replay_adp_baseline(picks, adp_candidates, teams, *, max_scenarios=15):
    """Retrospective *current ADP* baseline, NOT an unbiased historical backtest.

    Select top-five still available at each sampled historic draft pick; observe
    how many were taken by the next round. Today's ADP may reflect hindsight,
    and this does not evaluate alternate draft outcomes or projected points.
    """
    try:
        teams = int(teams)
    except (TypeError, ValueError):
        return []
    if teams < 2:
        return []
    numbered = []
    for pick in picks or []:
        try:
            number = int(pick.get("pick_no"))
        except (AttributeError, ValueError, TypeError):
            continue
        if pick.get("player_id") is not None and number > 0:
            numbered.append((number, str(pick["player_id"])))
    numbered.sort()
    if len(numbered) < teams + 2:
        return []
    rostered = {pid: number for number, pid in numbered}
    sorted_baseline = sorted(
        (row for row in adp_candidates
         if row.get("player_id") and _valid_adp(row.get("blend_adp")) is not None),
        key=lambda row: float(row["blend_adp"]),
    )
    if not sorted_baseline:
        return []
    snapshots = {}
    for position in range(1, min(numbered[-1][0] - teams + 2,
                                 1 + teams * max_scenarios), teams):
        available = [
            row for row in sorted_baseline
            if rostered.get(str(row["player_id"]), float("inf")) >= position
        ][:5]
        if not available:
            continue
        snapshots[str(position)] = {
            "draft_id": "retrospective ADP proxy",
            "pick": position, "observed_pick": position,
            "following_pick": position + teams,
            "candidates": [{
                "player_id": str(row["player_id"]),
                "name": str(row.get("player") or row["player_id"]),
                "rank": rank + 1,
                "adp": row["blend_adp"], "lockin_points": None,
            } for rank, row in enumerate(available)],
        }
    return evaluate_snapshots(snapshots, picks)


def _valid_adp(value):
    try:
        number = float(value)
        return number if 0 < number < float("inf") else None
    except (ValueError, TypeError):
        return None


def rows_as_csv(rows):
    columns = ["draft", "upcoming_pick", "following_pick", "name",
               "shortlist_rank", "adp", "lockin_points", "actual_pick", "outcome"]
    file = io.StringIO()
    writer = csv.DictWriter(file, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return file.getvalue()
