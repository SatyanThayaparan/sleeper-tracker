"""Prevent drift between Picky's browser favicon, sidebar logo and polling defaults."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BrandAndRefreshTests(unittest.TestCase):
    def test_same_picky_png_is_used_for_tab_and_sidebar(self):
        theme = (ROOT / "theme.py").read_text(encoding="utf-8")
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertRegex(
            theme,
            r'ICON_PATH\s*=\s*Path\(__file__\)\.resolve\(\)\.parent\s*/\s*"assets"\s*/\s*"picky-logo.png"',
        )
        self.assertIn("logo_path = ICON_PATH", theme)
        self.assertIn("page_icon=_page_icon", app)
        self.assertIn("_page_icon = str(ICON_PATH)", app)
        self.assertTrue((ROOT / "assets" / "picky-logo.png").is_file())

    def test_default_check_every_five_seconds_without_overwriting_preferences(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertRegex(
            app,
            r'if "cfg_refresh" not in st\.session_state:\s*st\.session_state\.cfg_refresh = 5',
        )
        self.assertIn("options=[5, 10, 15, 30, 60]", app)
        self.assertIn('refresh = int(st.session_state.cfg_refresh)', app)
        self.assertIn('@st.fragment(run_every=f"{refresh}s")', app)
        self.assertIn('key="check_sleeper_overview"', app)
        self.assertIn('key="check_sleeper_board"', app)


if __name__ == "__main__":
    unittest.main()
