"""Offline tests for Sleeper opponent pick ownership and positional signals."""
import unittest

from opponent_draft import (
    opponent_context_for_candidate, opponent_need_summary,
    opponent_picks_before_next_turn,
)


class OpponentDraftTests(unittest.TestCase):
    def setUp(self):
        self.draft = {
            "type": "snake",
            "slot_to_roster_id": {"1": 10, "2": 20, "3": 30, "4": 40},
        }
        self.players = {
            "pg": {"fantasy_positions": ["PG", "SG"]},
            "wing": {"fantasy_positions": ["SF", "SG"]},
            "center": {"fantasy_positions": ["C"]},
        }
        self.picks = [
            {"pick_no": 1, "roster_id": 10, "player_id": "pg"},
            {"pick_no": 2, "roster_id": 20, "player_id": "center"},
            {"pick_no": 3, "roster_id": 30, "player_id": "wing"},
        ]

    def test_sleeper_snake_mapping_and_own_picks_excluded(self):
        result = opponent_picks_before_next_turn(
            self.picks, self.draft, current_pick=4, following_pick=9,
            teams=4, my_roster_ids={"10"}, traded_picks=[],
        )
        self.assertEqual([(r["pick_no"], r["roster_id"]) for r in result],
                         [(4, "40"), (5, "40"), (6, "30"), (7, "20")])

    def test_traded_pick_owner_overrides_original_slot(self):
        result = opponent_picks_before_next_turn(
            self.picks, self.draft, current_pick=4, following_pick=7,
            teams=4, my_roster_ids={"10"},
            traded_picks=[{"round": 2, "roster_id": 40, "owner_id": 20}],
        )
        # Round 2 starts at pick 5, originally owned by roster 40.
        self.assertEqual([(r["pick_no"], r["roster_id"]) for r in result],
                         [(4, "40"), (5, "20"), (6, "30")])

    def test_missing_owner_mapping_or_trades_is_unknown(self):
        self.assertEqual(opponent_picks_before_next_turn(
            self.picks, {"type": "snake"}, current_pick=4,
            following_pick=9, teams=4, my_roster_ids={"10"}, traded_picks=[],
        ), [])
        self.assertEqual(opponent_picks_before_next_turn(
            self.picks, self.draft, current_pick=4,
            following_pick=9, teams=4, my_roster_ids={"10"}, traded_picks=None,
        ), [])
        self.assertEqual(opponent_picks_before_next_turn(
            self.picks, self.draft, current_pick=4,
            following_pick=9, teams=4, my_roster_ids=(), traded_picks=[],
        ), [])

    def test_opponents_needing_guard_are_not_guaranteed_to_select_one(self):
        upcoming = [
            {"pick_no": 4, "roster_id": "40"},
            {"pick_no": 5, "roster_id": "40"},
            {"pick_no": 6, "roster_id": "30"},
            {"pick_no": 7, "roster_id": "20"},
        ]
        result = opponent_need_summary(
            upcoming, self.picks, self.players,
            ["PG", "SG", "SF", "PF", "C"],
            candidate_positions=["PG", "SG"],
        )
        # 20 drafted a C only, 30 drafted SG/SF, 40 has no players.
        self.assertEqual(result["matching_teams"], 2)
        self.assertEqual(result["matching_picks"], 3)
        self.assertEqual(result["teams_picking"], 3)

    def test_player_context_includes_conservative_explanation(self):
        context = opponent_context_for_candidate(
            {"position": "PG, SG"}, picks=self.picks,
            draft=self.draft, players=self.players,
            slots=["PG", "SG", "SF", "PF", "C"],
            current_pick=4, following_pick=9, teams=4,
            my_roster_ids={"10"}, traded_picks=[],
        )
        self.assertEqual(context["matching_picks"], 3)
        self.assertIn("not a predicted selection", context["explanation"])

    def test_missing_position_information_cannot_imply_need(self):
        result = opponent_need_summary(
            [{"pick_no": 4, "roster_id": "40"}],
            self.picks, self.players, [], candidate_positions=["PG"],
        )
        self.assertFalse(result["has_roster_context"])
        self.assertEqual(result["matching_picks"], 0)


if __name__ == "__main__":
    unittest.main()
