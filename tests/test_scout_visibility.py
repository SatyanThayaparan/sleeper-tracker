"""UI regression checks for intentionally invoked, clutter-free AI Scout."""
from pathlib import Path
import unittest
from scout import research_allowed, use_scout, auto_research_due

ROOT = Path(__file__).resolve().parents[1]


class ResearchVisibilityTests(unittest.TestCase):
    def test_single_explicit_research_button(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('"Research Top 5 with AI"', source)
        self.assertIn('use_scout(', source)
        self.assertNotIn('"Run one-time AI research recovery"', source)
        self.assertNotIn("AI research requests are exhausted", source)
        self.assertIn('with st.expander("Expert research · sources, articles and diagnostics")', source)

    def test_unresearched_details_are_labeled_as_ranking_only(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        start = source.index('def show_scout_player_details(')
        end = source.index('def render_scout_report(', start)
        modal = source[start:end]
        self.assertIn("if not player_ai:", modal)
        self.assertIn("not from ESPN/Yahoo research", modal)
        self.assertIn("return", modal)

    def test_no_browser_spending_limits_or_auto_research(self):
        session = {"ai_scout_call_counts": {"turn-1": 999},
                   "ai_scout_session_calls": 999}
        self.assertTrue(research_allowed(session, "turn-1"))
        self.assertFalse(auto_research_due(
            session, "turn-1", on_clock=True, unlocked=True,
            configured=True, candidate_count=5, draft_active=True
        ))
        calls = []
        def mocked(*args, **kwargs):
            calls.append(1)
            return {"timestamp": 100, "report": {"players": []}}
        for _ in range(3):
            use_scout(session, "turn-1", [{"player": "A"}],
                      open_slots=[], research_fn=mocked)
        self.assertEqual(len(calls), 3)

    def test_empty_structured_response_includes_provider_reason(self):
        source = (ROOT / "scout.py").read_text(encoding="utf-8")
        self.assertIn("incomplete_details", source)
        self.assertIn("incomplete_reason=", source)
        self.assertIn("No AI report was saved", source)


if __name__ == "__main__":
    unittest.main()
