"""No-network HTML and responsive styling checks for Picky AI Scout."""
import unittest
from html.parser import HTMLParser
from pathlib import Path

from scout_design import (
    photo_html, player_photo_url, initials_for, scout_hero_html,
    scout_candidate_html, details_header_html, insight_panel_html,
    source_heading_html,
)


ROOT = Path(__file__).resolve().parents[1]


class Tags(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(dict(attrs))
        elif tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        assert self.stack, f"Unexpected closing tag {tag}"
        opened = self.stack.pop()
        assert opened == tag, f"Expected {opened}, got {tag}"


class ScoutDesignTests(unittest.TestCase):
    def _validate_html(self, markup):
        parser = Tags()
        parser.feed(markup)
        self.assertEqual(parser.stack, [])
        return parser

    def test_sleeper_nba_portrait_url_and_fallback(self):
        self.assertEqual(
            player_photo_url("1240"),
            "https://sleepercdn.com/content/nba/players/thumb/1240",
        )
        for value in ("123.jpg", "1/../a", "<svg>", "javascript:bad", None,
                      "other-player", "1?ref=bad"):
            self.assertEqual(player_photo_url(value), "")
        self.assertEqual(initials_for("Nikola Jokić"), "NJ")
        html = photo_html("Kevin Durant", "1240")
        parser = self._validate_html(html)
        self.assertIn("KD", html)
        self.assertEqual(len(parser.images), 0)
        self.assertIn("picky-photo-image", html)
        self.assertIn("background-image:url('https://sleepercdn.com/content/nba/players/thumb/1240')", html)
        # A blocked/404 CDN URL now fails silently behind the initials.
        self.assertNotIn("<img", html)
        missing = photo_html("NBA Rookie", "unknown")
        self.assertEqual(self._validate_html(missing).images, [])
        self.assertIn("NR", missing)

    def test_all_dynamic_text_html_escaped(self):
        name = '<img src=x onerror="alert(1)">'
        candidate = {
            "player": name, "player_id": "1/onload", "team": "<script>x</script>",
            "position": "PG", "blend_adp": 21.5, "sleeper_search_rank": 20,
        }
        components = [
            scout_hero_html(candidate, summary="<b>danger</b>",
                            risk="elevated", cited_count=3),
            scout_candidate_html(candidate, 1, summary="<svg onload=x>",
                                 cited_count=2),
            details_header_html(candidate, citations=4),
            insight_panel_html("<Title>", "<iframe src=bad>"),
            source_heading_html("<b>ESPN</b>", "Fantasy", "Recent"),
        ]
        for html in components:
            with self.subTest(html=html[:70]):
                self._validate_html(html)
                self.assertNotIn("<script>", html)
                self.assertNotIn("<iframe", html)
                self.assertNotIn('src="https://sleepercdn.com/content/nba/players/thumb/1/onload"', html)
        self.assertIn("&lt;script&gt;", components[0])
        self.assertIn("&lt;b&gt;danger&lt;/b&gt;", components[0])

    def test_hero_and_compact_card_content(self):
        candidate = {
            "player": "Shai Gilgeous-Alexander", "player_id": "1240",
            "position": "PG, SG", "team": "OKC",
            "blend_adp": 3.6, "sleeper_search_rank": 2,
            "roster": "Provides valuable guard flexibility.",
        }
        hero = scout_hero_html(candidate, risk="elevated",
                               following_pick=18, cited_count=2)
        self._validate_html(hero)
        for expected in ("Shai Gilgeous-Alexander", "OKC",
                         "ADP 3.6", "Next pick #18", "2 cited findings",
                         "Wait risk: Elevated"):
            self.assertIn(expected, hero)
        card = scout_candidate_html(candidate, 1, risk="elevated",
                                    summary="Player-specific short report.",
                                    cited_count=1)
        self._validate_html(card)
        self.assertIn("picky-player-identity", card)
        self.assertIn("picky-player-research", card)
        self.assertIn("picky-player-summary", card)
        self.assertIn("picky-player-metrics", card)
        self.assertIn("Sleeper search #2", card)
        self.assertIn("Player-specific short report.", card)
        self.assertIn("1 cited findings", card)

    def test_responsive_style_and_legacy_ranking_preserved(self):
        css = (ROOT / "scout_style.py").read_text(encoding="utf-8")
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("@media (max-width:760px)", css)
        self.assertIn("@media (prefers-reduced-motion:reduce)", css)
        self.assertIn("st-key-ai_candidate_", css)
        self.assertIn("picky-modal-hero", css)
        self.assertIn("with st.container(key=f\"ai_candidate_{rank_no}\"):", app)
        self.assertIn("top_five_for_pick(", app)
        self.assertIn('"View details"', app)
        self.assertIn('"Research Top 5 with AI"', app)
        self.assertIn("with st.expander(\"Research coverage & diagnostics\"):", app)


if __name__ == "__main__":
    unittest.main()
