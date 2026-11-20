"""League-aware exploratory Lock-In projection model.

A Lock-In manager chooses one completed player-game score for the week.
This models expected *best available game* as an optimistic opportunity
ceiling, not a guaranteed locked score or forecast of manager timing.
No score is generated without both credible game-score and volatility inputs.
"""
from __future__ import annotations

from math import comb, isfinite
from statistics import NormalDist

STATS = ("pts", "reb", "ast", "stl", "blk", "tov", "fg3m",
         "fgm", "fga", "ftm", "fta", "oreb", "dreb", "pf", "dd", "td")
ALIASES = {"turnovers": "tov", "three_pm": "fg3m", "threes": "fg3m",
           "three_pointers": "fg3m", "points": "pts",
           "rebounds": "reb", "assists": "ast", "steals": "stl",
           "blocks": "blk"}


def finite_number(value):
    try:
        result = float(value)
        return result if isfinite(result) else None
    except (ValueError, TypeError):
        return None


def score_from_stats(projected_stats, league_scoring):
    """Apply *only* overlapping known Sleeper stat keys to CSV stat means.

    Returns None if no supported stat match is supplied. Warn callers that
    missing stats/bonuses create a partial estimate.
    """
    stats = {}
    for key, value in (projected_stats or {}).items():
        normalized = ALIASES.get(str(key).lower(), str(key).lower())
        if normalized in STATS and finite_number(value) is not None:
            stats[normalized] = float(value)
    total = 0.0
    matched = []
    missing = []
    for key, value in (league_scoring or {}).items():
        normalized = ALIASES.get(str(key).lower(), str(key).lower())
        if normalized not in STATS:
            continue
        weight = finite_number(value)
        if weight is None or weight == 0:
            continue
        if normalized in stats:
            total += stats[normalized] * weight
            matched.append(normalized)
        else:
            missing.append(normalized)
    return {"points": total, "matched": sorted(set(matched)),
            "missing": sorted(set(missing))} if matched else None


def best_of_games(mean, standard_deviation, games):
    """Numerically integrate E[max(X_1,...,X_n)] for normal per-game X.

    This is an optimistic theoretical maximum for actively managed Lock-In,
    not an exact Sleeper outcome (lock decisions occur after each game).
    """
    mean = finite_number(mean)
    sd = finite_number(standard_deviation)
    if mean is None or sd is None or sd < 0:
        return None
    n = min(6, max(1, int(games)))
    if n == 1 or sd == 0:
        return mean
    standard = NormalDist()
    # For max of n normal draws, quantile at u is Phi^-1(u^(1/n)).
    count = 96
    return mean + sd * sum(
        standard.inv_cdf(((j + .5) / count) ** (1 / n))
        for j in range(count)
    ) / count


def lockin_estimate(*, projected_fppg=None, floor_fppg=None,
                    upside_fppg=None, standard_deviation=None,
                    games_per_week=None, availability_pct=None,
                    projected_stats=None, league_scoring=None):
    weighted = score_from_stats(projected_stats, league_scoring)
    mean = (weighted["points"] if weighted and not weighted["missing"]
            else finite_number(projected_fppg))
    if mean is None and weighted:
        # Partial scoring is not safe to substitute for full league points.
        return {"available": False, "reason": "League scoring input is incomplete; missing stat projections: "
                + ", ".join(weighted["missing"]), "points": None}
    if mean is None:
        return {"available": False, "reason": "No league-scored per-game projection supplied.",
                "points": None}
    sd = finite_number(standard_deviation)
    if sd is None:
        low, high = finite_number(floor_fppg), finite_number(upside_fppg)
        # Only treat floor/upside as approximate P10/P90 by convention.
        if low is not None and high is not None and high >= low:
            sd = (high - low) / (2 * 1.28155)
    if sd is None:
        return {"available": False, "reason": "No game-to-game variation supplied (stdev or floor/upside).",
                "points": None, "mean": round(mean, 2)}
    games = finite_number(games_per_week)
    if games is None or games < 1:
        return {"available": False, "reason": "Games per week missing; cannot estimate Lock-In opportunity.",
                "points": None, "mean": round(mean, 2)}
    n = min(6, max(1, round(games)))
    availability = finite_number(availability_pct)
    if availability is None:
        return {"available": False, "reason": "Availability percentage missing; cannot price missed games.",
                "points": None, "mean": round(mean, 2)}
    # Accept 0-1 or 0-100 user-entered availability percentages.
    p = max(0.0, min(1.0, availability / 100 if availability > 1 else availability))
    value = 0.0
    no_game_prob = (1 - p) ** n
    for played in range(1, n + 1):
        chance = comb(n, played) * (p ** played) * ((1 - p) ** (n - played))
        value += chance * best_of_games(mean, sd, played)
    return {
        "available": True, "points": round(value, 2),
        "mean": round(mean, 2), "sd": round(sd, 2),
        "scheduled_games": n, "availability": round(p, 3),
        "no_game_prob": round(no_game_prob, 3),
        "method": "Optimistic expected best game; not a guaranteed lock score",
        "scoring_source": "full league-stat projection" if weighted and not weighted["missing"]
                          else "imported league-scored FPPG",
    }
