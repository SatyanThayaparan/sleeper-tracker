"""Opponent-aware draft context for Picky's NBA draft copilot.

Uses public Sleeper picks, order, original roster mapping and traded-pick
ownership when supplied. Signals indicate exposed roster needs and draft
opportunity, NOT calibrated selection probabilities or user intentions.
"""
from __future__ import annotations

from collections import Counter, defaultdict

from recommend import positions_of

CORE = ("PG", "SG", "SF", "PF", "C")
SLOT_ALIASES = {"PG", "SG", "SF", "PF", "C"}


def _positive_int(value):
    try:
        number = int(value)
        return number if number > 0 else None
    except (TypeError, ValueError):
        return None


def _slot_for_pick(number, *, teams, snake):
    round_number = (number - 1) // teams + 1
    slot = (number - 1) % teams + 1
    if snake and round_number % 2 == 0:
        slot = teams + 1 - slot
    return slot, round_number


def _roster_by_slot(draft):
    raw = draft.get("slot_to_roster_id") or {}
    return {str(k): str(v) for k, v in raw.items() if v is not None}


def opponent_picks_before_next_turn(
    picks, draft, *, current_pick, following_pick, teams,
    my_roster_ids=(), traded_picks=()
):
    """Return the next selections' *current* roster owners when verifiable.

    Only assert ownership for roster IDs provided by Sleeper's
    slot_to_roster_id. If missing, omit predictions rather than guessing
    based on an unrelated user ID. Handle traded picks by original owner
    and round; the API's owner_id identifies the receiving roster.
    """
    team_count = _positive_int(teams)
    start = _positive_int(current_pick)
    end = _positive_int(following_pick)
    if not (team_count and start and end and end > start):
        return []
    if traded_picks is None or not set(str(value) for value in my_roster_ids):
        # Unknown trade records or user identity -> avoid false owner claims.
        return []
    roster_for_slot = _roster_by_slot(draft)
    if not roster_for_slot:
        return []
    trades = {}
    for trade in traded_picks or ():
        if not isinstance(trade, dict):
            continue
        rnd, original = _positive_int(trade.get("round")), _positive_int(trade.get("roster_id"))
        recipient = _positive_int(trade.get("owner_id"))
        if rnd and original and recipient:
            trades[(rnd, original)] = str(recipient)

    mine = {str(roster) for roster in my_roster_ids}
    made = {_positive_int(p.get("pick_no")) for p in picks if isinstance(p, dict)}
    results = []
    for number in range(start, end):
        if number in made:
            continue
        slot, rnd = _slot_for_pick(
            number, teams=team_count, snake=draft.get("type") == "snake"
        )
        original = roster_for_slot.get(str(slot))
        owner = trades.get((rnd, _positive_int(original)), original)
        if owner and owner not in mine:
            results.append({"pick_no": number, "roster_id": str(owner)})
    return results


def opponent_need_summary(
    upcoming_opponent_picks, picks, players, slots, *, candidate_positions=()
):
    """Count opponent roster gaps, without guessing what they'll draft.

    A 'need' means the roster hasn't yet selected as many players eligible
    for the core position as it has starting slots of that type. Players
    eligible at multiple slots can therefore be counted for multiple
    positions. This is conservative directional context, not exact lineup fit.
    """
    required = Counter(str(s).upper() for s in slots if str(s).upper() in SLOT_ALIASES)
    known_owners = {str(item["roster_id"]) for item in upcoming_opponent_picks}
    roster_players = defaultdict(set)
    for pick in picks:
        if not isinstance(pick, dict) or pick.get("player_id") is None:
            continue
        owner = pick.get("roster_id")
        if owner is not None and str(owner) in known_owners:
            roster_players[str(owner)].add(str(pick["player_id"]))
    by_owner = {}
    for owner in known_owners:
        eligible = Counter()
        for pid in roster_players[owner]:
            for position in set(positions_of(players.get(pid, {}))):
                if position in CORE:
                    eligible[position] += 1
        by_owner[owner] = {
            pos for pos in CORE
            if required[pos] > 0 and eligible[pos] < required[pos]
        }

    target = set(str(s).upper() for s in candidate_positions if str(s).upper() in CORE)
    matching_picks = [p for p in upcoming_opponent_picks
                      if by_owner.get(str(p["roster_id"]), set()) & target]
    matching_teams = {str(item["roster_id"]) for item in matching_picks}
    return {
        "known_picks": len(upcoming_opponent_picks),
        "teams_picking": len(known_owners),
        "matching_picks": len(matching_picks),
        "matching_teams": len(matching_teams),
        "candidate_positions": sorted(target),
        "has_roster_context": bool(known_owners and required),
    }


def opponent_context_for_candidate(
    candidate, *, picks, draft, players, slots,
    current_pick, following_pick, teams, my_roster_ids=(),
    traded_picks=(),
):
    upcoming = opponent_picks_before_next_turn(
        picks, draft, current_pick=current_pick, following_pick=following_pick,
        teams=teams, my_roster_ids=my_roster_ids, traded_picks=traded_picks
    )
    raw = str(candidate.get("position") or "").replace("/", ",")
    candidate_positions = [x.strip() for x in raw.split(",")]
    result = opponent_need_summary(
        upcoming, picks, players, slots, candidate_positions=candidate_positions
    )
    if not result["has_roster_context"]:
        result["explanation"] = (
            "Opponent draft-slot ownership or starting-position data is incomplete; "
            "Picky cannot assess other teams' positional needs."
        )
    elif result["matching_picks"] == 0:
        result["explanation"] = (
            f"{result['known_picks']} known opponent selections before your next "
            "turn; no opponent has a documented unfilled matching core position. "
            "They may still draft this player for depth or value."
        )
    else:
        result["explanation"] = (
            f"{result['matching_teams']} opponent team(s) with an unfilled matching "
            f"core position have {result['matching_picks']} pick(s) before your "
            "next turn. This indicates competition, not a predicted selection."
        )
    return result
