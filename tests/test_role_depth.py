"""Regression tests for role-depth-aware rankings and explanations."""
import unittest

from recommend import (
    role_counts, role_targets, need_rank_delta,
    need_score_multiplier, need_note, ROLES,
)


class RoleDepthTests(unittest.TestCase):
    def test_multiple_positions_match_role_coverage_counts(self):
        players = {
            "a": {"fantasy_positions": ["PG", "SG", "SF"]},
            "b": {"fantasy_positions": ["SF", "PF", "C"]},
        }
        self.assertEqual(role_counts(["a", "b"], players),
                         {"PG": 1, "SG": 1, "SF": 2, "PF": 1, "C": 1})
        self.assertEqual(role_counts(["a", "a", "b"], players),
                         {"PG": 1, "SG": 1, "SF": 2, "PF": 1, "C": 1})

    def test_six_sg_and_two_centers_not_false_vacancy(self):
        players = {
            **{f"g{i}": {"fantasy_positions": ["PG", "SG"]}
               for i in range(6)},
            "c1": {"fantasy_positions": ["C"]},
            "c2": {"fantasy_positions": ["C", "PF"]},
        }
        counts = role_counts(list(players), players)
        self.assertEqual(counts["SG"], 6)
        self.assertEqual(counts["C"], 2)
        targets = role_targets(["PG", "SG", "SF", "PF", "C", "G", "F", "UTIL"])
        sg_note = need_note(["SG"], counts, targets, True,
                            "Fills your open SG slot.")
        center_note = need_note(["C"], counts, targets, True,
                                "Fills your open C slot.")
        self.assertIn("6 SG-eligible", sg_note)
        self.assertNotIn("no sg", sg_note.lower())
        self.assertIn("2 C-eligible", center_note)
        self.assertIn("SG (6 eligible)", center_note)
        self.assertGreater(need_rank_delta(["SG"], counts, targets, True),
                           need_rank_delta(["C"], counts, targets, True))
        self.assertLess(need_score_multiplier(["SG"], counts, targets, True,
                                              "specific", 15),
                        need_score_multiplier(["C"], counts, targets, True,
                                              "specific", 15))

    def test_multi_eligible_guard_uses_the_thinner_role(self):
        counts = {"PG": 1, "SG": 6, "SF": 3, "PF": 3, "C": 2}
        targets = role_targets(["PG", "SG", "SF", "PF", "C"])
        self.assertEqual(
            need_rank_delta(["PG", "SG"], counts, targets, True),
            need_rank_delta(["PG"], counts, targets, True),
        )
        self.assertIn("1 PG-eligible", need_note(
            ["PG", "SG"], counts, targets, True, "Fills your open PG slot."
        ))

    def test_absent_role_still_reports_true_gap(self):
        counts = {role: 0 for role in ROLES}
        note = need_note(["C"], counts, role_targets(["C"]), True,
                         "Fills your open C slot.")
        self.assertIn("No drafted players are eligible at C", note)


if __name__ == "__main__":
    unittest.main()
