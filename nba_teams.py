"""Static NBA franchise metadata used for roster diversity summaries.

These describe NBA franchises, not fantasy league roster positions.
"""
from collections import Counter

# NBA division membership is relatively stable; keep aliases localized here.
DIVISIONS = {
    "Atlantic": ("BOS", "BKN", "NYK", "PHI", "TOR"),
    "Central": ("CHI", "CLE", "DET", "IND", "MIL"),
    "Southeast": ("ATL", "CHA", "MIA", "ORL", "WAS"),
    "Northwest": ("DEN", "MIN", "OKC", "POR", "UTA"),
    "Pacific": ("GSW", "LAC", "LAL", "PHX", "SAC"),
    "Southwest": ("DAL", "HOU", "MEM", "NOP", "SAS"),
}
FRANCHISES = {
    "ATL": "Atlanta Hawks", "BOS": "Boston Celtics",
    "BKN": "Brooklyn Nets", "CHA": "Charlotte Hornets",
    "CHI": "Chicago Bulls", "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons", "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets", "IND": "Indiana Pacers",
    "LAC": "LA Clippers", "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies", "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans", "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder", "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers", "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs", "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz", "WAS": "Washington Wizards",
}
ALIASES = {
    "BRK": "BKN", "BK": "BKN", "NJN": "BKN", "GS": "GSW",
    "GS": "GSW", "NO": "NOP", "NOLA": "NOP", "SA": "SAS",
    "NY": "NYK", "PHO": "PHX", "UTH": "UTA",
}
CORE_POSITIONS = ("PG", "SG", "SF", "PF", "C")


def nba_team(code):
    raw = str(code or "").upper().strip()
    return ALIASES.get(raw, raw) if raw in FRANCHISES or raw in ALIASES else None


def nba_conference_division(code):
    team = nba_team(code)
    if not team:
        return None, None
    for division, members in DIVISIONS.items():
        if team in members:
            conference = "Eastern" if division in ("Atlantic", "Central", "Southeast") else "Western"
            return conference, division
    return None, None


def roster_breakdown(roster_ids, players, roster_state):
    """Core position coverage comes from assigned slots, not eligible-player counts."""
    lineup = (roster_state or {}).get("lineup") or []
    occupied = {
        row.get("slot") for row in lineup
        if row.get("player_id") is not None and row.get("slot") in CORE_POSITIONS
    }
    coverage = {pos: pos in occupied for pos in CORE_POSITIONS}

    # A player can provide flexibility at multiple positions, regardless of
    # which starter/utility/bench slot was allocated to them. Count each
    # player once per eligible core position; do not count the player twice
    # when Sleeper returns repeated position labels.
    eligible_counts = Counter({pos: 0 for pos in CORE_POSITIONS})
    seen_player_ids = set()
    for player_id in roster_ids:
        pid = str(player_id)
        if pid in seen_player_ids:
            continue
        seen_player_ids.add(pid)
        meta = players.get(pid) or {}
        positions = meta.get("fantasy_positions") or []
        if isinstance(positions, str):
            positions = positions.split(",")
        eligible = {str(pos).strip().upper() for pos in positions}
        for pos in CORE_POSITIONS:
            if pos in eligible:
                eligible_counts[pos] += 1

    teams = Counter()
    conferences = Counter()
    divisions = Counter()
    unknown = 0
    for player_id in roster_ids:
        meta = players.get(str(player_id)) or {}
        team = nba_team(meta.get("team"))
        if not team:
            unknown += 1
            continue
        conference, division = nba_conference_division(team)
        teams[team] += 1
        if conference:
            conferences[conference] += 1
        if division:
            divisions[division] += 1
    return {
        "coverage": coverage, "covered_count": sum(coverage.values()),
        "eligible_counts": {pos: eligible_counts[pos] for pos in CORE_POSITIONS},
        "eligible_covered_count": sum(eligible_counts[pos] > 0 for pos in CORE_POSITIONS),
        "eligible_role_total": sum(eligible_counts.values()),
        "teams": teams, "conferences": conferences, "divisions": divisions,
        "unknown": unknown,
    }
