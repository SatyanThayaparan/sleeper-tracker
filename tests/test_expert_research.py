"""Source verification and ESPN/Yahoo expert reporting, all offline."""
import json
import unittest
from datetime import date
from types import SimpleNamespace

from expert_research import (
    classify_evidence, publisher, reported_age,
    verified_expert_evidence, report_research_summary,
)
from scout import (run_scout, turn_research_key, auto_research_due,
                   use_scout, cached_report_matches, cache_entry)


class ExpertEvidenceTests(unittest.TestCase):
    def test_publisher_and_ranking_format_classification(self):
        self.assertEqual(publisher("https://sports.yahoo.com/fantasy/article/rankings"), "Yahoo Sports")
        self.assertEqual(publisher("https://www.espn.com/fantasy/basketball/"), "ESPN")
        self.assertEqual(publisher("https://www.nba.com/news/nba-fantasy-top-250-points-league-rankings"), "NBA.com")
        self.assertEqual(classify_evidence("Top 250 points league rankings", "https://nba.com/x"), "Expert rankings / cheat sheet")
        self.assertEqual(classify_evidence("Injury update", "https://espn.com/nba/injuries",
                                           "I read a ranking"), "NBA news / player report")

    def test_freshness_and_missing_future_dates(self):
        today = date(2026, 11, 19)
        self.assertEqual(reported_age("2026-11-18", today=today), (1, "Recent · ≤7 days"))
        self.assertEqual(reported_age("2026-10-01", today=today),
                         (49, "Older research · verify current status"))
        self.assertEqual(reported_age("2027-01-01", today=today),
                         (None, "Future / unverified date"))
        self.assertEqual(reported_age("not a date", today=today),
                         (None, "Date not verified"))

    def test_only_cited_player_specific_sources_survive(self):
        yahoo = "https://sports.yahoo.com/fantasy/article/points-league-rankings"
        bogus = "https://www.espn.com/fantasy/basketball/fictional-ranking"
        news = "https://www.nba.com/news/real-injury-report"
        player = {
            "name": "Example Player",
            "expert_rankings": [
                {"claim": "Mentioned on the season points list",
                 "source_title": "Fantasy basketball points league rankings",
                 "reported_date": "2026-10-10",
                 "source_url": yahoo, "ranking_format": "Points league"},
                {"claim": "Fabricated expert rank",
                 "source_title": "Fantasy basketball rankings",
                 "reported_date": "2026-11-18",
                 "source_url": bogus, "ranking_format": "Points league"},
                {"claim": "A false ranking based on a game report",
                 "source_title": "NBA injury update",
                 "reported_date": "2026-11-18",
                 "source_url": news, "ranking_format": "Points league"},
            ],
            "evidence": [
                {"claim": "Player had a status update", "source_title": "NBA injury update",
                 "source_url": news, "reported_date": "2026-11-18"},
            ],
        }
        rows = verified_expert_evidence(player, {yahoo, news}, today=date(2026, 11, 19))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["publisher"], "Yahoo Sports")
        self.assertEqual(rows[0]["age_days"], 40)
        self.assertEqual(rows[1]["kind"], "NBA news / player report")
        report = report_research_summary({"players": [dict(player, verified_expert_evidence=rows)]})
        self.assertEqual(report["players_with_rankings"], 1)
        self.assertEqual(report["total_verified_links"], 2)

    def test_draft_changes_invalidate_prior_shortlist(self):
        key = turn_research_key("draft", "owner", 103)
        session = {}
        use_scout(session, key, [
            {"player": "Guard"}, {"player": "Center"}
        ], open_slots=[], research_fn=lambda *_args, **_kwargs: {
            "report": {"players": [{"name": "Guard"}, {"name": "Center"}]},
            "sources": [], "timestamp": 100,
        })
        stored = cache_entry(session, key, now=101)
        self.assertTrue(cached_report_matches(
            stored, [{"player": "Guard"}, {"player": "Center"}]
        ))
        changed = [{"player": "Forward"}, {"player": "Center"}]
        self.assertFalse(cached_report_matches(stored, changed))
        self.assertTrue(auto_research_due(
            session, key, on_clock=True, unlocked=True, configured=True,
            candidate_count=2, draft_active=True, candidates=changed,
        ))
        self.assertFalse(auto_research_due(
            session, key, on_clock=True, unlocked=True, configured=True,
            candidate_count=2, draft_active=True,
            candidates=[{"player": "Center"}, {"player": "Guard"}],
        ))

    def test_preturn_report_prevents_duplicate_auto_charge(self):
        key = turn_research_key("draft", "user", 103)
        fake_entry = {"report": {"players": []}, "timestamp": 1, "sources": []}
        session = {}
        use_scout(session, key, [{"player": "A"}], open_slots=[],
                  research_fn=lambda *_args, **_kwargs: fake_entry)
        self.assertFalse(auto_research_due(
            session, key, on_clock=True, unlocked=True, configured=True,
            candidate_count=1, draft_active=True
        ))


class ExpertScoutContractTests(unittest.TestCase):
    def test_research_prompt_and_ranking_links_are_verified(self):
        actual = "https://sports.yahoo.com/fantasy/article/real-points-rankings"
        forged = "https://www.espn.com/fantasy/basketball/imaginary"
        class FakeResponses:
            def __init__(self):
                self.request = None
            def create(self, **kwargs):
                self.request = kwargs
                p = {
                    "name": "Example Guard", "role_outlook": "Available",
                    "recent_findings": "No recent verified injury",
                    "availability_risk": "Unverified", "draft_fit": "Extra guard depth",
                    "why_now": "Consider ADP", "evidence_date": "Unverified",
                    "evidence": [], "expert_take": "Mixed expert opinions",
                    "expert_rankings": [
                        {"claim": "Yahoo named player in points list",
                         "source_title": "Yahoo Fantasy points league rankings",
                         "source_url": actual, "reported_date": "2026-10-12",
                         "ranking_format": "Points"},
                        {"claim": "ESPN made this player #1",
                         "source_title": "ESPN draft cheat sheet",
                         "source_url": forged, "reported_date": "2026-11-19",
                         "ranking_format": "Points"},
                    ],
                }
                return SimpleNamespace(
                    output_text=json.dumps({
                        "recommended_player": "Example Guard",
                        "headline": "Unverified current form",
                        "why_this_pick": "Based on ADP",
                        "confidence": "low", "players": [p],
                        "alternatives": [], "cautions": [],
                        "research_summary": "Expert research check",
                    }),
                    output=[SimpleNamespace(content=[
                        SimpleNamespace(annotations=[
                            SimpleNamespace(url=actual, title="Yahoo expert ranking")
                        ])
                    ])],
                )
        fake = FakeResponses()
        result = run_scout(
            [{"player": "Example Guard", "position": "PG, SG",
              "score": 40, "roster": "Guard depth"}],
            open_slots=["SG"], client=SimpleNamespace(responses=fake)
        )
        report = result["report"]["players"][0]
        self.assertEqual(len(report["expert_rankings"]), 1)
        self.assertEqual(report["expert_rankings"][0]["source_url"], actual)
        self.assertEqual(result["research_quality"]["players_with_rankings"], 1)
        self.assertIn("ESPN", fake.request["instructions"])
        self.assertIn("Yahoo", fake.request["instructions"])
        self.assertIn("expert_rankings", fake.request["text"]["format"]["schema"]["properties"]["players"]["items"]["properties"])
        self.assertEqual(fake.request["tools"][0]["type"], "web_search")
        self.assertTrue(fake.request["store"] is False)


if __name__ == "__main__":
    unittest.main()
