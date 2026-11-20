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
                         open_slots=()):
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
    return {
        "risk": level,
        "reason": reason,
        "adp": adp,
        "next_pick": next_pick,
        "fills": fills,
        "position_note": (f"Eligible for open slot(s): {', '.join(dict.fromkeys(fills))}."
                          if fills else "Does not directly fill an open starting slot."),
        "basis": "Blended ADP and estimated draft order; not a probability forecast.",
    }


def timing_for_shortlist(candidates, *, current_pick=None, following_pick=None,
                         open_slots=()):
    return {
        str(p.get("player")): evaluate_pick_timing(
            p, current_pick=current_pick, following_pick=following_pick,
            open_slots=open_slots
        )
        for p in candidates
    }
