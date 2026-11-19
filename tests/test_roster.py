"""Unit tests for pick planning; run with python -m unittest discover -s tests."""
import unittest

from roster import assign_lineup, chronological_roster, next_user_picks, top_five_for_pick


class RosterTests(unittest.TestCase):
    def test_multi_position_assignment_keeps_critical_slot_open_when_needed(self):
        players = {
            "guard": {"fantasy_positions": ["PG", "SG"]},
            "point": {"fantasy_positions": ["PG"]},
            "center": {"fantasy_positions": ["C"]},
        }
        result = assign_lineup(["guard", "point", "center"], players,
                               ["PG", "SG", "C", "UTIL", "BN"])
        self.assertEqual(result["filled"], 3)
        self.assertEqual(result["total"], 4)
        self.assertEqual(result["open_slots"], ["UTIL"])
        self.assertEqual(result["bench_ids"], [])

    def test_ineligible_player_stays_on_bench(self):
        result = assign_lineup(["one"], {"one": {"fantasy_positions": ["C"]}},
                               ["PG", "BN"])
        self.assertEqual(result["open_slots"], ["PG"])
        self.assertEqual(result["bench_ids"], ["one"])

    def test_chronological_first_eight_then_utility_and_bench(self):
        slots = ["PG", "SG", "SF", "PF", "C", "G", "F", "UTIL",
                 "UTIL", "UTIL", "BN", "BN"]
        ids = [str(i) for i in range(1, 13)]
        players = {
            pid: {"fantasy_positions": ["PG", "SG", "SF", "PF", "C"]}
            for pid in ids
        }
        result = chronological_roster(
            ids, players, slots, pick_numbers=list(range(10, 22))
        )
        self.assertEqual(
            [row["player_id"] for row in result["primary"]],
            ids[:8],
        )
        self.assertEqual(
            [row["player_id"] for row in result["utility"]],
            ids[8:10],
        )
        self.assertEqual(
            [row["player_id"] for row in result["bench"]],
            ids[10:],
        )
        self.assertEqual(result["bench"][0]["group"], "bench")
        self.assertEqual(result["utility"][0]["group"], "utility")
        self.assertEqual(result["lineup"][0]["pick_number"], 10)

    def test_chronological_does_not_reorder_early_picks(self):
        players = {
            "center": {"fantasy_positions": ["C"]},
            "point": {"fantasy_positions": ["PG"]},
            "guard": {"fantasy_positions": ["PG", "SG"]},
        }
        result = chronological_roster(
            ["center", "point", "guard"], players,
            ["PG", "SG", "C", "UTIL", "BN"],
        )
        self.assertEqual(result["primary"][2]["player_id"], "center")
        self.assertEqual(result["primary"][0]["player_id"], "point")
        self.assertEqual(result["primary"][1]["player_id"], "guard")
        self.assertEqual(result["bench"], [])

    def test_ineligible_early_pick_is_visible_on_bench(self):
        players = {
            "center": {"fantasy_positions": ["C"]},
            "pg": {"fantasy_positions": ["PG"]},
        }
        result = chronological_roster(
            ["center", "pg"], players,
            ["PG", "BN"], pick_numbers=[3, 7],
        )
        self.assertEqual(result["primary"][0]["player_id"], "pg")
        self.assertEqual(result["bench"][0]["player_id"], "center")
        self.assertEqual(result["bench"][0]["pick_number"], 3)

    def test_next_snake_picks(self):
        draft = {"type": "snake", "draft_order": {"me": 2}}
        picks = [{"pick_no": x} for x in range(1, 13)]
        self.assertEqual(next_user_picks(picks, draft, "me", 4, 4), [15])

    def test_missing_slot_returns_no_predictions(self):
        self.assertEqual(next_user_picks([], {"draft_order": {}}, "me", 12, 13), [])

    def test_best_five_not_one_per_position(self):
        rows = [
            {"player_id": str(i), "score": 100 - i,
             "position": "PG", "hard_negative": False}
            for i in range(8)
        ]
        self.assertEqual([r["player_id"] for r in top_five_for_pick(rows)],
                         ["0", "1", "2", "3", "4"])

    def test_injury_flagged_players_excluded_when_alternatives_exist(self):
        rows = [
            {"player_id": "risk", "score": 99, "hard_negative": True},
            {"player_id": "safe", "score": 95, "hard_negative": False},
        ]
        self.assertEqual(top_five_for_pick(rows)[0]["player_id"], "safe")


if __name__ == "__main__":
    unittest.main()
