"""Regression tests for live draft refresh, missing player crash and opt-in AI fees."""
import ast
from pathlib import Path
import time
import unittest

from scout import (
    auto_research_due, cached_report_matches, record_auto_attempt,
    turn_research_key, use_scout,
)

APP = Path(__file__).resolve().parents[1] / "app.py"


class DraftRefreshTests(unittest.TestCase):
    def test_player_name_function_is_not_shadowed_by_local_string(self):
        """Regression: Overview previously set player_name = 'Kevin Durant',
        then tried to call player_name(pid, players, picks), raising TypeError.
        The shadow also broke Draft Board due Python local scoping.
        """
        tree = ast.parse(APP.read_text(encoding="utf-8"))
        funcs = {node.name: node for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        dashboard = funcs["live_dashboard"]
        shadow_assignments = [
            node for node in ast.walk(dashboard)
            if isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Store)
            and node.id == "player_name"
        ]
        self.assertFalse(shadow_assignments)
        self.assertIn("player_name(pick.get(\"player_id\"), players, picks)",
                      APP.read_text(encoding="utf-8"))

    def test_force_refresh_controls_clear_only_draft_snapshot_cache(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn('key="check_sleeper_overview"', source)
        self.assertIn('key="check_sleeper_board"', source)
        self.assertEqual(source.count("live_draft_snapshot.clear(draft_id)"), 2)
        self.assertIn('st.rerun(scope="fragment")', source)
        self.assertNotIn("api_get.clear()", source)

    def test_opt_in_mode_visible_and_manual_button_remains(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn('"Automatically research when I\'m on the clock"', source)
        self.assertIn('key="scout_auto_on_turn"', source)
        self.assertIn('auto_enabled=bool(st.session_state.get("scout_auto_on_turn"))', source)
        self.assertIn('"Research Top 5 with AI"', source)
        self.assertIn('record_auto_attempt(st.session_state, turn_key)', source)


class AutoScoutTests(unittest.TestCase):
    KEY = "turn-example-123"
    CANDIDATES = [{"player": "Kevin Durant"}]

    def due(self, session, **overrides):
        props = dict(
            on_clock=True, unlocked=True, configured=True,
            candidate_count=5, draft_active=True,
            candidates=self.CANDIDATES, auto_enabled=True,
        )
        props.update(overrides)
        return auto_research_due(session, self.KEY, **props)

    def test_off_by_default_and_not_when_opponent_picking(self):
        self.assertFalse(self.due({}, auto_enabled=False))
        self.assertFalse(self.due({}, on_clock=False))
        self.assertFalse(self.due({}, unlocked=False))
        self.assertFalse(self.due({}, configured=False))
        self.assertFalse(self.due({}, draft_active=False))
        self.assertFalse(self.due({}, candidate_count=0))
        self.assertFalse(auto_research_due(
            {}, "", auto_enabled=True, on_clock=True, unlocked=True,
            configured=True, candidate_count=5, draft_active=True,
        ))

    def test_one_attempt_per_turn_even_when_api_fails(self):
        session = {}
        self.assertTrue(self.due(session))
        record_auto_attempt(session, self.KEY)
        self.assertFalse(self.due(session))
        # A different owned turn may trigger a new request after opted in.
        self.assertTrue(auto_research_due(
            session, "turn-next", auto_enabled=True, on_clock=True,
            unlocked=True, configured=True, candidate_count=5,
            draft_active=True, candidates=self.CANDIDATES,
        ))

    def test_cached_research_prevents_duplicate_paid_auto_request(self):
        session = {"ai_scout_cache": {
            self.KEY: {
                "timestamp": time.time(),
                "candidate_names": ["Kevin Durant"],
                "report": {"players": [{"name": "Kevin Durant"}]},
            },
        }}
        self.assertFalse(self.due(session))
        # If shortlist changed but the same owned pick remains, the current
        # auto call can run once to study the newly available candidates.
        self.assertTrue(self.due(session, candidates=[{"player": "Jayson Tatum"}]))

    def test_manual_button_can_still_retry_after_automatic_attempt(self):
        session = {}
        record_auto_attempt(session, self.KEY)
        received = []
        def fake_research(candidates, *, open_slots):
            received.append(candidates[0]["player"])
            return {"timestamp": time.time(), "report": {"players": []}}
        for _ in range(2):
            use_scout(session, self.KEY, self.CANDIDATES, open_slots=[],
                      research_fn=fake_research)
        self.assertEqual(received, ["Kevin Durant", "Kevin Durant"])
        self.assertFalse(self.due(session))


if __name__ == "__main__":
    unittest.main()
