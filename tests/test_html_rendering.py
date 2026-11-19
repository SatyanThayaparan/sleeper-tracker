"""Regression tests for Streamlit's raw HTML roster/scout rendering.

Keep HTML card helpers isolated from app import, which initializes Streamlit and
can make remote Sleeper requests. No network or browser is required.
"""
import ast
import html
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "app.py"


class HtmlStructure(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        assert self.stack, f"Unmatched closing tag: {tag}"
        opened = self.stack.pop()
        assert opened == tag, f"Expected closing {opened}, saw {tag}"


class RendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = [node for node in tree.body
                     if isinstance(node, ast.FunctionDef)
                     and node.name in ("roster_player_card", "render_roster_grid")]
        cls.names = {fn.name for fn in functions}
        captured = []
        stub_streamlit = SimpleNamespace(html=lambda markup: captured.append(markup))
        env = {
            "escape_html": html.escape,
            "player_name": lambda pid, players, picks: players[str(pid)]["full_name"],
            "player_positions": lambda meta: meta.get("fantasy_positions", []),
            "st": stub_streamlit,
        }
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), "exec"),
             env)
        cls.card = staticmethod(env["roster_player_card"])
        cls.render = staticmethod(env["render_roster_grid"])
        cls.captured = captured

    def test_roster_grid_uses_html_not_markdown(self):
        self.captured.clear()
        roster = {
            "primary": [{"player_id": None, "slot": "PG", "group": "starter",
                         "pick_number": None}],
            "utility": [{"player_id": None, "slot": "UTIL", "group": "utility",
                         "pick_number": None}],
            "bench": [],
        }
        self.render(roster, {}, [])
        self.assertEqual(len(self.captured), 1)
        markup = self.captured[0]
        self.assertIn('class="fx-roster-layout"', markup)
        self.assertIn('class="fx-roster-starters"', markup)
        self.assertIn("Utility & bench", markup)
        parser = HtmlStructure()
        parser.feed(markup)
        self.assertEqual(parser.stack, [])

    def test_dynamic_player_name_is_html_escaped(self):
        players = {"1": {"full_name": '<img src=x onerror="alert(1)">',
                          "fantasy_positions": ["PG"], "team": "TOR"}}
        card = self.card({"player_id": "1", "slot": "PG", "group": "starter",
                          "pick_number": 8}, players, [])
        self.assertNotIn("<img", card)
        self.assertIn("&lt;img", card)
        self.assertIn("#8", card)
        parser = HtmlStructure()
        parser.feed(card)
        self.assertEqual(parser.stack, [])

    def test_scout_heading_uses_html_renderer(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        fragments = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "html"
            and any(isinstance(arg, ast.Constant) and
                    "fx-scout-heading" in str(arg.value)
                    for arg in node.args)
        ]
        self.assertTrue(fragments, "AI heading must use st.html not Markdown.")


if __name__ == "__main__":
    unittest.main()
