"""Roster-slot assignment for Picky's team view.

A maximum bipartite matching avoids misreporting positional needs when drafted
players qualify for multiple positions. Starter slots are treated as a
best-effort projection, not a claim about Sleeper's current lineup.
"""

from recommend import positions_of, slot_compatible

BENCH = {"BN", "BENCH", "IR", "IL", "TAXI", "RESERVE"}


def assign_lineup(roster_ids, players, slots):
    """Return assigned starter slots, remaining slots, and unassigned players.

    Each drafted player can fill at most one starter position. Narrow slots
    take priority over flexible slots, and all feasible assignments are
    considered through augmenting-path matching.
    """
    starter_slots = [str(slot).upper() for slot in slots
                     if str(slot).upper() not in BENCH]
    player_ids = [str(pid) for pid in roster_ids]
    unique = list(dict.fromkeys(player_ids))
    slot_order = sorted(range(len(starter_slots)), key=lambda i: (
        starter_slots[i] in ("UTIL", "UTILITY", "FLEX"),
        starter_slots[i] in ("G", "F"),
        i,
    ))
    matching = {}

    def visit(player_id, visited):
        for index in slot_order:
            if index in visited:
                continue
            if not slot_compatible(starter_slots[index],
                                   positions_of(players.get(player_id, {}))):
                continue
            visited.add(index)
            current = matching.get(index)
            if current is None or visit(current, visited):
                matching[index] = player_id
                return True
        return False

    # Least-flexible players first yields predictable tie-breaking.
    unique.sort(key=lambda pid: sum(
        slot_compatible(slot, positions_of(players.get(pid, {})))
        for slot in starter_slots
    ))
    for pid in unique:
        visit(pid, set())

    lineup = [{"slot": slot, "player_id": matching.get(index)}
              for index, slot in enumerate(starter_slots)]
    assigned = set(matching.values())
    return {
        "lineup": lineup,
        "open_slots": [item["slot"] for item in lineup if not item["player_id"]],
        "bench_ids": [pid for pid in player_ids if pid not in assigned],
        "filled": len(matching),
        "total": len(starter_slots),
    }


def next_user_picks(picks, draft, user_id, teams, rounds):
    """Calculate upcoming snake/linear picks for a selected draft account."""
    if not user_id or not teams or not rounds:
        return []
    order = draft.get("draft_order") or {}
    slot = order.get(str(user_id))
    try:
        slot = int(slot)
    except (ValueError, TypeError):
        return []
    if slot < 1 or slot > teams:
        return []
    made = {int(p["pick_no"]) for p in picks if p.get("pick_no") is not None}
    current = max(made, default=0) + 1
    upcoming = []
    for number in range(current, teams * rounds + 1):
        round_number = (number - 1) // teams + 1
        draft_slot = (number - 1) % teams + 1
        if draft.get("type") == "snake" and round_number % 2 == 0:
            draft_slot = teams + 1 - draft_slot
        if draft_slot == slot:
            upcoming.append(number)
    return upcoming


def top_five_for_pick(rows):
    """Five top scored eligible players; unlike variety picks, no role quota."""
    pool = [row for row in rows if not row.get("hard_negative")]
    if not pool:
        pool = rows
    return sorted(pool, key=lambda r: r.get("score", float("-inf")),
                  reverse=True)[:5]
