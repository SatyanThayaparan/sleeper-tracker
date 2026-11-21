"""Shared visual design checks: no API calls and unchanged controls."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PageStyleTests(unittest.TestCase):
    def test_appwide_style_is_loaded_before_scout_override(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("from page_style import inject_page_css", app)
        self.assertIn("inject_css()\ninject_page_css()\ninject_scout_css()", app)
        self.assertIn("with st.sidebar:", app)
        self.assertIn("on_click=select_page", app)
        self.assertIn('key="run_manual_ai_scout"', app)

    def test_shared_css_covers_existing_page_elements(self):
        css = (ROOT / "page_style.py").read_text(encoding="utf-8")
        for marker in (
            "section[data-testid=\"stSidebar\"]",
            "fx-page-header", "fx-page-title", "stMetric",
            "stDataFrame", "fx-team-panel", "fx-roster-player",
            "stDownloadButton", "stTextInput", "st-key-view_",
            "@media (max-width:960px)", "@media (max-width:640px)",
            "@media (prefers-reduced-motion:reduce)",
            "focus-visible",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, css)

    def test_no_network_or_app_logic_in_presentation(self):
        content = (ROOT / "page_style.py").read_text(encoding="utf-8")
        for unsafe in (
            "requests.get", "api_get(", "responses.create(",
            "st.session_state", "st.rerun(", "st.button(",
            "st.image(", "st.fragment(",
        ):
            self.assertNotIn(unsafe, content)

    def test_detail_buttons_and_research_still_remain_native(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('st.html(scout_candidate_html(', app)
        self.assertIn('st.html(scout_hero_html(', app)
        self.assertIn('"View details"', app)
        self.assertIn('"Research Top 5 with AI"', app)
        self.assertIn('"Ask Picky"', app)


if __name__ == "__main__":
    unittest.main()
