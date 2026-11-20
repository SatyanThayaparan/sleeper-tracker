"""No-network coverage for Lock-In scoring, AI follow-ups, and draft evaluation."""
import unittest

from copilot import (MAX_FOLLOWUPS, ask_copilot, compare_question,
                     context_snapshot)
from evaluation import (evaluate_snapshots, evaluation_summary,
                        record_snapshot, replay_adp_baseline, rows_as_csv)
from lockin import best_of_games, lockin_estimate, score_from_stats


class LockInTests(unittest.TestCase):
    def test_scoring_uses_actual_league_weights(self):
        scored = score_from_stats(
            {"pts": 20, "reb": 8, "ast": 5},
            {"pts": 1, "reb": 1.2, "ast": 1.5},
        )
        self.assertAlmostEqual(scored["points"], 37.1)
        self.assertEqual(scored["missing"], [])

    def test_comparable_distribution_enables_lockin_opportunity(self):
        result = lockin_estimate(
            projected_fppg=40, standard_deviation=10,
            games_per_week=4, availability_pct=90,
        )
        self.assertTrue(result["available"])
        self.assertGreater(result["points"], 40)
        self.assertLess(result["points"], 70)
        self.assertGreater(result["no_game_prob"], 0)
        self.assertEqual(best_of_games(40, 10, 1), 40)

    def test_missing_inputs_are_never_fabricated(self):
        self.assertFalse(lockin_estimate(projected_fppg=None)["available"])
        self.assertFalse(lockin_estimate(
            projected_fppg=40, games_per_week=4, availability_pct=95
        )["available"])
        self.assertFalse(lockin_estimate(
            projected_fppg=40, standard_deviation=5, availability_pct=95
        )["available"])
        self.assertFalse(lockin_estimate(
            projected_fppg=40, standard_deviation=5, games_per_week=4
        )["available"])

    def test_partial_stat_projection_does_not_masquerade_as_full_scoring(self):
        result = lockin_estimate(
            projected_stats={"pts": 20},
            league_scoring={"pts": 1, "ast": 1.5},
            games_per_week=3, availability_pct=90,
            standard_deviation=5,
        )
        self.assertFalse(result["available"])
        self.assertIn("ast", result["reason"])

    def test_floor_and_upside_can_approximate_spread(self):
        result = lockin_estimate(
            projected_fppg=30, floor_fppg=18, upside_fppg=44,
            games_per_week=3, availability_pct=0.95,
        )
        self.assertTrue(result["available"])
        self.assertGreater(result["sd"], 0)


class CopilotTests(unittest.TestCase):
    def setUp(self):
        self.candidates = [
            {"player": "Guard", "position": "PG, SG", "team": "TOR",
             "blend_adp": 40, "roster": "Extra guard depth."},
            {"player": "Center", "position": "C", "team": "DEN",
             "blend_adp": 45, "roster": "Relatively thin center coverage."},
        ]
        self.context = context_snapshot(
            self.candidates,
            role_counts={"PG": 6, "SG": 6, "SF": 5, "PF": 3, "C": 2},
            next_pick=35,
        )

    def test_contextual_comparison_uses_no_web_search(self):
        calls = []
        def fake(messages, **kwargs):
            calls.append((messages, kwargs))
            return "Center is thinner, but compare relative points."
        query = compare_question("Guard", "Center", self.context)
        session = {}
        result = ask_copilot(session, key="turn-1", context=self.context,
                             question=query, completion_fn=fake)
        self.assertIn("Center", result)
        self.assertEqual(len(calls), 1)
        self.assertIn('"SG": 6', calls[0][0][1]["content"])
        self.assertNotIn("tools", calls[0][1])
        self.assertEqual(session["picky_copilot_attempts"]["turn-1"], 1)

    def test_different_candidate_required(self):
        with self.assertRaises(ValueError):
            compare_question("Center", "Center", self.context)
        with self.assertRaises(ValueError):
            compare_question("Center", "Unknown", self.context)

    def test_failed_api_requests_count_toward_budget(self):
        session = {}
        def failed(*args, **kwargs):
            raise RuntimeError("Provider down")
        for i in range(MAX_FOLLOWUPS):
            with self.assertRaises(RuntimeError):
                ask_copilot(session, key="turn-1", context=self.context,
                             question="Should I draft the center?",
                             completion_fn=failed)
        self.assertEqual(session["picky_copilot_attempts"]["turn-1"],
                         MAX_FOLLOWUPS)
        with self.assertRaisesRegex(RuntimeError, "limit"):
            ask_copilot(session, key="turn-1", context=self.context,
                         question="And now?", completion_fn=failed)


class EvaluationTests(unittest.TestCase):
    def test_snapshots_record_once_and_measure_real_survival(self):
        session = {}
        candidates = [
            {"player_id": "g", "player": "Guard", "blend_adp": 25},
            {"player_id": "c", "player": "Center", "blend_adp": 35},
        ]
        kwargs = dict(draft_id="draft", upcoming_pick=10,
                      following_pick=20, current_pick=10,
                      candidates=candidates)
        self.assertTrue(record_snapshot(session, **kwargs))
        self.assertFalse(record_snapshot(session, **kwargs))
        picks = [
            {"pick_no": 12, "player_id": "g"},
            {"pick_no": 20, "player_id": "other"},
        ]
        rows = evaluate_snapshots(session["picky_eval_snapshots"], picks)
        self.assertEqual(rows[0]["outcome"], "taken before next pick")
        self.assertEqual(rows[1]["outcome"], "survived to next pick")
        stats = evaluation_summary(rows)
        self.assertEqual(stats["reviewed"], 2)
        self.assertEqual(stats["survived"], 1)
        self.assertIn("Guard", rows_as_csv(rows))

    def test_retrospective_adp_baseline_is_observational(self):
        picks = [{"pick_no": i, "player_id": str(i)}
                 for i in range(1, 13)]
        pool = [{"player_id": str(i), "player": str(i),
                 "blend_adp": i} for i in range(1, 15)]
        rows = replay_adp_baseline(picks, pool, 4)
        self.assertTrue(rows)
        self.assertTrue(all(r["draft"] == "retrospective ADP proxy"
                            for r in rows))
        self.assertTrue(any(r["outcome"] == "taken before next pick"
                            for r in rows))


if __name__ == "__main__":
    unittest.main()
