"""No-network tests for the deterministic Draft Now vs Wait assessment."""
import unittest

from draft_strategy import evaluate_pick_timing, timing_for_shortlist, player_headshot_url


class TimingTests(unittest.TestCase):
    def test_elevated_when_adp_before_following_pick(self):
        signal = evaluate_pick_timing(
            {"position": "PG, SG", "blend_adp": 39.5},
            current_pick=35, following_pick=46, open_slots=["PG", "C"],
        )
        self.assertEqual(signal["risk"], "elevated")
        self.assertIn("PG", signal["fills"])
        self.assertIn("#46", signal["reason"])
        self.assertNotIn("%", signal["reason"])

    def test_opponent_competition_can_raise_moderate_to_elevated(self):
        signal = evaluate_pick_timing(
            {"position": "SG", "blend_adp": 49},
            current_pick=35, following_pick=46, open_slots=["SG"],
            opponent={"has_roster_context": True,
                      "matching_picks": 3, "matching_teams": 2},
        )
        self.assertEqual(signal["risk"], "elevated")
        self.assertIn("opponents", signal["reason"])
        self.assertNotIn("%", signal["reason"])

    def test_unknown_adp_stays_unknown_despite_opponents(self):
        signal = evaluate_pick_timing(
            {"position": "SF", "blend_adp": None},
            current_pick=35, following_pick=46,
            opponent={"has_roster_context": True,
                      "matching_picks": 5, "matching_teams": 4},
        )
        self.assertEqual(signal["risk"], "unknown")

    def test_moderate_when_adp_near_next_pick(self):
        signal = evaluate_pick_timing(
            {"position": "SF", "blend_adp": 49},
            current_pick=35, following_pick=46, open_slots=["SF"],
        )
        self.assertEqual(signal["risk"], "moderate")

    def test_lower_when_adp_much_later(self):
        signal = evaluate_pick_timing(
            {"position": "C", "blend_adp": 81},
            current_pick=35, following_pick=46, open_slots=["PG"],
        )
        self.assertEqual(signal["risk"], "lower")
        self.assertEqual(signal["fills"], [])
        self.assertIn("not guaranteed", signal["reason"])

    def test_unknown_without_pick_or_valid_adp(self):
        no_pick = evaluate_pick_timing(
            {"position": "PG", "blend_adp": 35.0},
            current_pick=20, following_pick=None
        )
        self.assertEqual(no_pick["risk"], "unknown")
        invalid = evaluate_pick_timing(
            {"position": "C", "blend_adp": float("nan")},
            current_pick=15, following_pick=30
        )
        self.assertEqual(invalid["risk"], "unknown")

    def test_unknown_for_bad_next_pick(self):
        result = evaluate_pick_timing(
            {"position": "G", "blend_adp": 12},
            current_pick=45, following_pick=44, open_slots=["G"]
        )
        self.assertEqual(result["risk"], "unknown")

    def test_headshot_only_with_a_valid_nba_id(self):
        self.assertEqual(
            player_headshot_url({"nba_id": "2544", "player_id": "irrelevant"}),
            "https://cdn.nba.com/headshots/nba/latest/260x190/2544.png",
        )
        self.assertEqual(player_headshot_url({"player_id": "2544"}),
                         "https://sleepercdn.com/content/nba/players/thumb/2544")
        self.assertEqual(player_headshot_url({}, "1240"),
                         "https://sleepercdn.com/content/nba/players/thumb/1240")
        self.assertIsNone(player_headshot_url({"nba_id": "2544.png"}))
        self.assertIsNone(player_headshot_url({"nba_id": "../2544"}))
        self.assertIsNone(player_headshot_url({"nba_id": "0" * 20}))
        self.assertIsNone(player_headshot_url({}))

    def test_supports_flexibility_and_shortlist(self):
        rows = [
            {"player": "A", "position": "SG", "blend_adp": 40},
            {"player": "B", "position": "PF", "blend_adp": 66},
        ]
        signals = timing_for_shortlist(rows, current_pick=34, following_pick=48,
                                       open_slots=["G", "UTIL"])
        self.assertEqual(set(signals), {"A", "B"})
        self.assertIn("G", signals["A"]["fills"])
        self.assertIn("UTIL", signals["B"]["fills"])


if __name__ == "__main__":
    unittest.main()
