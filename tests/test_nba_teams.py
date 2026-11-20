"""No-network checks for NBA franchises, conferences and positional coverage."""
import unittest
from nba_teams import (
    FRANCHISES, DIVISIONS, nba_team, nba_conference_division, roster_breakdown
)


class NBATeamTests(unittest.TestCase):
    def test_all_30_teams_in_exactly_one_division(self):
        self.assertEqual(len(FRANCHISES), 30)
        all_members = [team for teams in DIVISIONS.values() for team in teams]
        self.assertEqual(len(all_members), 30)
        self.assertEqual(set(all_members), set(FRANCHISES))

    def test_team_alias_and_conference(self):
        self.assertEqual(nba_team("brk"), "BKN")
        self.assertEqual(nba_team("no"), "NOP")
        self.assertEqual(nba_conference_division("TOR"), ("Eastern", "Atlantic"))
        self.assertEqual(nba_conference_division("LAL"), ("Western", "Pacific"))
        self.assertEqual(nba_conference_division("NOP"), ("Western", "Southwest"))
        self.assertEqual(nba_conference_division("FA"), (None, None))

    def test_roster_counts_assigned_core_positions_not_player_eligibility(self):
        players = {
            "1": {"team": "TOR", "fantasy_positions": ["PG", "SG"]},
            "2": {"team": "BOS", "fantasy_positions": ["C", "PF"]},
            "3": {"team": "LAL", "fantasy_positions": ["PF"]},
            "4": {"team": "TOR", "fantasy_positions": ["SF"]},
        }
        state = {"lineup": [
            {"slot": "PG", "player_id": "1"},
            {"slot": "C", "player_id": "2"},
            {"slot": "UTIL", "player_id": "3"},
            {"slot": "SG", "player_id": None},
        ]}
        result = roster_breakdown(["1", "2", "3", "4"], players, state)
        self.assertEqual(result["covered_count"], 2)
        self.assertTrue(result["coverage"]["PG"])
        self.assertFalse(result["coverage"]["SG"])
        self.assertFalse(result["coverage"]["PF"])
        self.assertEqual(result["teams"]["TOR"], 2)
        self.assertEqual(result["conferences"]["Eastern"], 3)
        self.assertEqual(result["conferences"]["Western"], 1)
        self.assertEqual(result["divisions"]["Atlantic"], 3)
        self.assertEqual(result["divisions"]["Pacific"], 1)

    def test_multiple_eligible_roles_per_player(self):
        # Player A: PG/SG/SF; Player B: SF/PF/C => 1,1,2,1,1.
        players = {
            "a": {"team": "TOR", "fantasy_positions": ["PG", "SG", "SF"]},
            "b": {"team": "LAL", "fantasy_positions": ["SF", "PF", "C"]},
        }
        state = {"lineup": [
            {"slot": "PG", "player_id": "a"},
            {"slot": "UTIL", "player_id": "b"},
            {"slot": "C", "player_id": None},
        ]}
        result = roster_breakdown(["a", "b"], players, state)
        self.assertEqual(result["eligible_counts"],
                         {"PG": 1, "SG": 1, "SF": 2, "PF": 1, "C": 1})
        self.assertEqual(result["eligible_covered_count"], 5)
        self.assertEqual(result["eligible_role_total"], 6)
        # Only the PG starting slot is assigned; utility doesn't count here.
        self.assertEqual(result["covered_count"], 1)

    def test_eligibility_includes_bench_and_deduplicates(self):
        players = {
            "starter": {"fantasy_positions": ["PG", "PG", "SG"]},
            "bench": {"fantasy_positions": ["SF", "PF", "C"]},
        }
        state = {"lineup": [{"slot": "PG", "player_id": "starter"}]}
        result = roster_breakdown(
            ["starter", "starter", "bench"], players, state
        )
        self.assertEqual(result["eligible_counts"],
                         {"PG": 1, "SG": 1, "SF": 1, "PF": 1, "C": 1})
        self.assertEqual(result["eligible_role_total"], 5)

    def test_no_players_and_unknown_franchises(self):
        empty = roster_breakdown([], {}, {"lineup": []})
        self.assertEqual(empty["covered_count"], 0)
        self.assertEqual(dict(empty["teams"]), {})
        self.assertEqual(empty["eligible_counts"],
                         {"PG": 0, "SG": 0, "SF": 0, "PF": 0, "C": 0})
        result = roster_breakdown(["1"], {"1": {"team": "FA"}},
                                  {"lineup": [{"slot": "PG", "player_id": "1"}]})
        self.assertEqual(result["covered_count"], 1)
        self.assertEqual(result["unknown"], 1)


if __name__ == "__main__":
    unittest.main()
