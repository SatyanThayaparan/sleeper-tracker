"""Explainable, deterministic draft-timing and position-fit signals.

ADP measures historical draft order, not the probability of being taken.
No unsourced availability percentages are produced here.
"""
from __future__ import annotations

import math
from recommend import slot_compatible


def _adp(value):
    try:
        number = float(value)
        return number if math.isfinite(number) and number > 0 else None
    except (TypeError, ValueError):
        return None


def evaluate_pick_timing(candidate, *, current_pick=None, following_pick=None,
                         open_slots=(), opponent=None):
    """Assess whether postponing a candidate to a later pick seems risky.

    Returns source-labeled deterministic observations, *not* calibrated odds.
    Pick estimates may be wrong if draft picks have been traded.
    """
    eligible = [x.strip().upper() for x in str(candidate.get("position") or "").split(",") if x.strip()]
    fills = [str(slot).upper() for slot in open_slots
             if slot_compatible(str(slot).upper(), eligible)]
    adp = _adp(candidate.get("blend_adp"))
    try:
        next_pick = int(following_pick)
    except (TypeError, ValueError):
        next_pick = None
    try:
        now = int(current_pick)
    except (TypeError, ValueError):
        now = None
    if next_pick is not None and (next_pick < 1 or (now is not None and next_pick <= now)):
        next_pick = None

    if adp is None:
        level = "unknown"
        reason = "No reliable blended ADP is available for this player."
    elif next_pick is None:
        level = "unknown"
        reason = "Your following selection is not known, so waiting risk cannot be assessed."
    elif adp <= next_pick:
        level = "elevated"
        reason = (f"Blended ADP {adp:.1f} is earlier than your following estimated "
                  f"pick #{next_pick}. Waiting could be risky.")
    elif adp <= next_pick + max(4, (next_pick - (now or next_pick)) * .5):
        level = "moderate"
        reason = (f"Blended ADP {adp:.1f} is close to your following estimated "
                  f"pick #{next_pick}; other managers might draft sooner.")
    else:
        level = "lower"
        reason = (f"Blended ADP {adp:.1f} is later than your following estimated "
                  f"pick #{next_pick}, but availability is not guaranteed.")
    # Layer observed opposing roster needs on top of the ADP assessment.
    # Other teams can choose anyone: don't claim exact probabilities.
    opponent = opponent if isinstance(opponent, dict) else {}
    contest = int(opponent.get("matching_picks") or 0)
    separate_teams = int(opponent.get("matching_teams") or 0)
    if opponent.get("has_roster_context") and contest >= 2 and separate_teams >= 2:
        if level == "moderate":
            level = "elevated"
            reason += " Several opponents have open eligible positions before your next pick."
        elif level == "lower":
            level = "moderate"
            reason += " Opposing roster needs suggest competition despite later ADP."
    elif opponent.get("has_roster_context") and contest >= 1 and level != "unknown":
        reason += " At least one opponent could target the same position."
    return {
        "risk": level,
        "reason": reason,
        "adp": adp,
        "next_pick": next_pick,
        "fills": fills,
        "position_note": (f"Eligible for open slot(s): {', '.join(dict.fromkeys(fills))}."
                          if fills else "Does not directly fill an open starting slot."),
        "basis": "Blended ADP, estimated draft order and opponents' positional needs; not a probability forecast.",
        "opponent_context": opponent,
    }


def timing_for_shortlist(candidates, *, current_pick=None, following_pick=None,
                         open_slots=(), opponent_by_player=None):
    return {
        str(p.get("player")): evaluate_pick_timing(
            p, current_pick=current_pick, following_pick=following_pick,
            open_slots=open_slots,
            opponent=(opponent_by_player or {}).get(str(p.get("player"))),
        )
        for p in candidates
    }


def player_headshot_url(player_meta, sleeper_player_id=None):
    """Lazy thumbnail from Sleeper CDN, with an NBA-ID option when provided.

    Sleeper player IDs are not interchangeable with NBA player IDs, so URLs
    from those two providers must be assembled independently.
    """
    if not isinstance(player_meta, dict):
        return None
    for key in ("nba_id", "nba_player_id"):
        value = str(player_meta.get(key) or "").strip()
        if value.isascii() and value.isdecimal() and 1 <= len(value) <= 10:
            return ("https://cdn.nba.com/headshots/nba/latest/260x190/"
                    + value + ".png")
    value = str(sleeper_player_id or player_meta.get("player_id") or "").strip()
    if value.isascii() and value.isdecimal() and 1 <= len(value) <= 10:
        return "https://sleepercdn.com/content/nba/players/thumb/" + value
    return None
