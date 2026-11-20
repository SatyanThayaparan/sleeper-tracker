"""UI regression checks for Scout research status and source-less fallback."""
from pathlib import Path
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

    def test_empty_structured_response_includes_provider_reason(self):
        source = (ROOT / "scout.py").read_text(encoding="utf-8")
        self.assertIn('incomplete_details', source)
        self.assertIn('incomplete_reason=', source)
        self.assertIn('No AI report was saved', source)


if __name__ == "__main__":
    unittest.main()
