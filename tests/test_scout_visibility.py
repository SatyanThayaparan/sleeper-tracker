"""UI regression checks for Scout research status and source-less fallback."""
from pathlib import Path
from scout import (MAX_PER_PICK, MAX_PER_SESSION, recovery_allowed,
                   research_allowed, use_scout, auto_research_due)
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ResearchVisibilityTests(unittest.TestCase):
    def test_a_real_research_request_can_be_started_while_on_clock(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        start = source.index('if auto_research_due(')
        end = source.index('# Show the actual concept recommendation card', start)
        main = source[start:end]
        self.assertIn('"Run AI research now"', main)
        self.assertIn('research_allowed(st.session_state, turn_key)', main)
        self.assertIn('use_scout(', main)
        self.assertIn('AI research requests this pick:', main)
        self.assertIn('AI research failed for this pick', main)
        self.assertIn('No completed AI research has been run', main)
        self.assertIn('record_auto_attempt(st.session_state, turn_key)', main)

    def test_unresearched_details_are_labeled_as_ranking_only(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        start = source.index('def show_scout_player_details(')
        end = source.index('def render_scout_report(', start)
        modal = source[start:end]
        self.assertIn('if not player_ai:', modal)
        self.assertIn('not from ESPN/Yahoo research', modal)
        self.assertIn('return', modal)
        self.assertIn('player_ai.get("expert_take")', modal)

    def test_exhausted_browser_can_make_exactly_one_confirmed_recovery(self):
        key = "turn-limited"
        session = {
            "ai_scout_call_counts": {key: MAX_PER_PICK},
            "ai_scout_session_calls": MAX_PER_SESSION,
        }
        self.assertFalse(research_allowed(session, key))
        self.assertTrue(recovery_allowed(session, key))
        called = []
        def fake(candidates, **kwargs):
            called.append(True)
            return {"report": {"players": [{"name": "Player"}]},
                    "timestamp": 100, "sources": []}
        response = use_scout(
            session, key, [{"player": "Player"}],
            open_slots=[], recovery=True, research_fn=fake
        )
        self.assertEqual(len(called), 1)
        self.assertEqual(response["candidate_names"], ["Player"])
        self.assertEqual(session["ai_scout_call_counts"][key], MAX_PER_PICK + 1)
        self.assertEqual(session["ai_scout_session_calls"], MAX_PER_SESSION + 1)
        self.assertFalse(recovery_allowed(session, key))
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            use_scout(session, key, [{"player": "Player"}],
                      open_slots=[], recovery=True, research_fn=fake)
        self.assertEqual(len(called), 1)

    def test_recovery_is_never_automatic(self):
        key = "turn-full"
        session = {
            "ai_scout_call_counts": {key: MAX_PER_PICK},
            "ai_scout_session_calls": MAX_PER_SESSION,
        }
        self.assertFalse(auto_research_due(
            session, key, on_clock=True, unlocked=True, configured=True,
            candidate_count=5, draft_active=True,
        ))
        with self.assertRaisesRegex(RuntimeError, "limit"):
            use_scout(session, key, [{"player": "Player"}],
                      open_slots=[], research_fn=lambda *args, **kwargs: {})
        self.assertTrue(recovery_allowed(session, key))

    def test_failed_recovery_counts_and_does_not_repeat(self):
        key = "turn-full"
        session = {
            "ai_scout_call_counts": {key: MAX_PER_PICK},
            "ai_scout_session_calls": MAX_PER_SESSION,
        }
        def broken(*args, **kwargs):
            raise RuntimeError("Provider unavailable")
        with self.assertRaisesRegex(RuntimeError, "Provider unavailable"):
            use_scout(session, key, [{"player": "Player"}],
                      open_slots=[], recovery=True, research_fn=broken)
        self.assertFalse(recovery_allowed(session, key))

    def test_limit_ui_displays_confirmation_and_recovery(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("Run one-time AI research recovery", source)
        self.assertIn("disabled=not confirmed", source)
        self.assertIn("recovery_allowed(st.session_state, turn_key)", source)
        self.assertIn("recovery=True", source)

    def test_empty_structured_response_includes_provider_reason(self):
        source = (ROOT / "scout.py").read_text(encoding="utf-8")
        self.assertIn('incomplete_details', source)
        self.assertIn('incomplete_reason=', source)
        self.assertIn('No AI report was saved', source)


if __name__ == "__main__":
    unittest.main()
