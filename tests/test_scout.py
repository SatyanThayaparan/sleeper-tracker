"""No paid network calls: AI Scout contract and cache tests."""
import time
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from scout import (
    CACHE_TTL_SECONDS, MAX_PER_PICK, cache_entry, research_allowed,
    research_key, run_scout, safe_source_urls, use_scout,
    turn_research_key, auto_research_due, record_auto_attempt,
)


class ScoutTests(unittest.TestCase):
    def setUp(self):
        self.players = [
            {"player_id": "11", "player": "Example Guard",
             "position": "PG", "score": 103.1, "roster": "Fills PG"},
            {"player_id": "22", "player": "Example Wing",
             "position": "SF", "score": 99.2, "roster": "Fills SF"},
        ]

    def test_key_changes_when_candidates_or_roster_change(self):
        key = research_key("draft", 27, [], self.players)
        self.assertNotEqual(key, research_key("draft", 28, [], self.players))
        self.assertNotEqual(key, research_key("draft", 27, ["5"], self.players))
        modified = [dict(self.players[0], score=104), self.players[1]]
        self.assertNotEqual(key, research_key("draft", 27, [], modified))

    def test_cache_expires(self):
        key = "current"
        session = {"ai_scout_cache": {key: {
            "timestamp": 1000, "text": "Test", "sources": []
        }}}
        self.assertIsNotNone(cache_entry(session, key, 1000 + CACHE_TTL_SECONDS - 1))
        self.assertIsNone(cache_entry(session, key, 1000 + CACHE_TTL_SECONDS))

    def test_only_explicit_call_runs_and_is_cached(self):
        session = {}
        key = research_key("draft", 27, [], self.players)
        called = []
        def fake_research(players, *, open_slots):
            called.append((players, open_slots))
            return {"text": "Mock report", "timestamp": time.time(), "sources": []}
        self.assertEqual(len(called), 0)
        result = use_scout(session, key, self.players, open_slots=["SF"],
                           research_fn=fake_research)
        self.assertEqual(len(called), 1)
        self.assertEqual(cache_entry(session, key), result)

    def test_request_limit(self):
        session = {}
        for _ in range(MAX_PER_PICK):
            use_scout(session, "one", self.players, open_slots=[],
                      research_fn=lambda *_args, **_kw: {
                          "text": "test", "timestamp": time.time(), "sources": []
                      })
        self.assertFalse(research_allowed(session, "one"))

    def test_requires_access_code_without_secret(self):
        from ai import scout_access_granted
        with patch("ai.get_scout_access_code", return_value=""):
            self.assertFalse(scout_access_granted("anything"))
        with patch("ai.get_scout_access_code", return_value="secret"):
            self.assertTrue(scout_access_granted("secret"))
            self.assertFalse(scout_access_granted("wrong"))

    def test_provider_citations_only(self):
        note = SimpleNamespace(url="https://example.com/report", title="News")
        text = SimpleNamespace(annotations=[note])
        response = SimpleNamespace(output=[SimpleNamespace(content=[text])])
        self.assertEqual(
            safe_source_urls(response),
            [{"title": "News", "url": "https://example.com/report"}],
        )

    def test_responses_web_search_request(self):
        captured = []
        class FakeResponses:
            def create(self, **kwargs):
                captured.append(kwargs)
                return SimpleNamespace(
                    output_text=json.dumps({
                        "recommended_player": "Example Guard",
                        "headline": "Strong guard option",
                        "why_this_pick": "Fits the open PG role.",
                        "confidence": "medium",
                        "players": [
                            {"name": "Example Guard", "role_outlook": "Starter",
                             "recent_findings": "No recent evidence supplied.",
                             "availability_risk": "Unverified",
                             "draft_fit": "Open PG", "why_now": "ADP urgency is uncertain.", "evidence_date": "Unverified", "evidence": []},
                            {"name": "Example Wing", "role_outlook": "Bench",
                             "recent_findings": "No recent evidence supplied.",
                             "availability_risk": "Unverified",
                             "draft_fit": "Open SF", "why_now": "Limited data on waiting.", "evidence_date": "Unverified", "evidence": []}
                        ],
                        "alternatives": ["Example Wing"],
                        "cautions": ["Verify any injury updates"],
                        "research_summary": "Researched news and role.",
                    }),
                    output=[SimpleNamespace(content=[
                        SimpleNamespace(annotations=[])
                    ])],
                )
        client = SimpleNamespace(responses=FakeResponses())
        result = run_scout(self.players, open_slots=["PG"], client=client)
        self.assertIsNone(result["report"]["recommended_player"])
        self.assertFalse(result["has_source_backed_research"])
        self.assertEqual(result["report"]["confidence"], "low")
        self.assertEqual(captured[0]["tools"][0]["type"], "web_search")
        self.assertEqual(captured[0]["store"], False)
        self.assertIn("why_now", captured[0]["text"]["format"]["schema"]["properties"]["players"]["items"]["properties"])
        self.assertIn("Yahoo", captured[0]["instructions"])
        self.assertIn("ESPN", captured[0]["instructions"])
        self.assertEqual(captured[0]["text"]["format"]["type"], "json_schema")
        self.assertIn("research", captured[0]["instructions"].lower())
        self.assertEqual(len(captured), 1)

    def test_scout_receives_next_turn_and_real_search_rank(self):
        calls = []
        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)
                return SimpleNamespace(
                    output_text=json.dumps({
                        "recommended_player": "Example Guard",
                        "headline": "Conditional pick",
                        "why_this_pick": "Fills need",
                        "confidence": "medium",
                        "players": [
                            {"name": "Example Guard", "role_outlook": "Starter",
                             "recent_findings": "No reports verified",
                             "availability_risk": "Unknown",
                             "draft_fit": "Fills PG", "why_now": "May not last",
                             "evidence_date": "Unverified", "evidence": []},
                            {"name": "Example Wing", "role_outlook": "Bench",
                             "recent_findings": "No reports verified",
                             "availability_risk": "Unknown",
                             "draft_fit": "Adds depth", "why_now": "Can wait",
                             "evidence_date": "Unverified", "evidence": []},
                        ],
                        "alternatives": [],
                        "cautions": [],
                        "research_summary": "Context check",
                    }),
                    output=[],
                )
        rows = [dict(x) for x in self.players]
        rows[0]["sleeper_search_rank"] = 19
        run_scout(rows, open_slots=["PG"], context={
            "current_pick": 30, "upcoming_pick": 30,
            "following_pick": 54, "league_teams": 12,
        }, client=SimpleNamespace(responses=FakeResponses()))
        prompt = calls[0]["input"]
        self.assertIn('"my_following_pick": 54', prompt)
        self.assertIn('"sleeper_search_rank": 19', prompt)

    def test_scout_ignores_evidence_links_not_in_provider_citations(self):
        calls = []
        trusted = "https://www.espn.com/nba/story/_/id/1234/verified"
        invented = "https://www.yahoo.com/fantasy/fictional-report"
        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)
                players = []
                for name, url in [("Example Guard", trusted), ("Example Wing", invented)]:
                    players.append({
                        "name": name, "role_outlook": "Unverified",
                        "recent_findings": "Some claim", "availability_risk": "Unknown",
                        "draft_fit": "Fits", "why_now": "Possible pick",
                        "evidence_date": "2026-11-19",
                        "evidence": [{
                            "claim": "An attributed claim",
                            "source_title": "Article",
                            "source_url": url,
                            "reported_date": "2026-11-19",
                        }],
                    })
                return SimpleNamespace(
                    output_text=json.dumps({
                        "recommended_player": "Example Guard",
                        "headline": "Example", "why_this_pick": "Fit",
                        "confidence": "medium", "players": players,
                        "alternatives": [], "cautions": [],
                        "research_summary": "Two player search",
                    }),
                    output=[SimpleNamespace(content=[SimpleNamespace(
                        annotations=[SimpleNamespace(url=trusted, title="Real source")]
                    )])],
                )
        result = run_scout(self.players, open_slots=["PG"],
                           client=SimpleNamespace(responses=FakeResponses()))
        rows = result["report"]["players"]
        self.assertEqual(len(rows[0]["evidence"]), 1)
        self.assertEqual(rows[1]["evidence"], [])
        self.assertEqual(len(result["sources"]), 1)
        self.assertIn("draft_now_vs_wait", calls[0]["input"])

    def test_reject_more_than_five(self):
        with self.assertRaises(ValueError):
            run_scout(self.players * 3, open_slots=[], client=object())


    def test_reject_candidate_outside_shortlist(self):
        class WrongPlayer:
            def create(self, **_kwargs):
                return SimpleNamespace(
                    output_text=json.dumps({
                        "recommended_player": "Not in list", "players": []
                    }),
                    output=[],
                )
        client = SimpleNamespace(responses=WrongPlayer())
        with self.assertRaisesRegex(RuntimeError, "outside your current shortlist"):
            run_scout(self.players, open_slots=["PG"], client=client)

    def test_reject_unparseable_report(self):
        class BadJSON:
            def create(self, **_kwargs):
                return SimpleNamespace(output_text="not JSON", output=[])
        with self.assertRaisesRegex(RuntimeError, "unreadable structured"):
            run_scout(self.players, open_slots=["PG"],
                      client=SimpleNamespace(responses=BadJSON()))


    def test_auto_scout_only_when_on_clock_and_unlocked(self):
        session = {}
        key = turn_research_key("draft1", "user2", 19)
        common = dict(unlocked=True, configured=True,
                      candidate_count=5, draft_active=True)
        self.assertFalse(auto_research_due(session, key, on_clock=False, **common))
        self.assertFalse(auto_research_due(session, key, on_clock=True,
                          **dict(common, unlocked=False)))
        self.assertFalse(auto_research_due(session, key, on_clock=True,
                          **dict(common, draft_active=False)))
        self.assertFalse(auto_research_due(session, key, on_clock=True,
                          **dict(common, candidate_count=0)))
        self.assertTrue(auto_research_due(session, key, on_clock=True, **common))
        record_auto_attempt(session, key)
        self.assertFalse(auto_research_due(session, key, on_clock=True, **common))

    def test_turn_report_stays_available_until_next_pick(self):
        key = turn_research_key("draft", "me", 27)
        session = {"ai_scout_cache": {key: {
            "timestamp": 100, "report": {"recommended_player": "Example Guard"},
            "sources": [],
        }}}
        self.assertIsNotNone(cache_entry(session, key, 100 + CACHE_TTL_SECONDS * 30))
        self.assertIsNone(cache_entry(
            session, turn_research_key("draft", "me", 39),
            100 + CACHE_TTL_SECONDS * 30,
        ))

    def test_turn_key_is_stable_within_pick_and_new_each_turn(self):
        self.assertEqual(turn_research_key("draft1", "me", 27),
                         turn_research_key("draft1", "me", 27))
        self.assertNotEqual(turn_research_key("draft1", "me", 27),
                            turn_research_key("draft1", "me", 39))
        self.assertNotEqual(turn_research_key("draft1", "me", 27),
                            turn_research_key("draft1", "other", 27))

    def test_failed_auto_scout_does_not_loop_or_charge_again(self):
        session = {}
        key = turn_research_key("draft", "me", 37)
        record_auto_attempt(session, key)
        with self.assertRaises(RuntimeError):
            use_scout(session, key, self.players, open_slots=[],
                      research_fn=lambda *_args, **_kwargs: (
                          (_ for _ in ()).throw(RuntimeError("simulated API failure"))
                      ))
        self.assertFalse(auto_research_due(
            session, key, on_clock=True, unlocked=True, configured=True,
            candidate_count=5, draft_active=True,
        ))
        self.assertEqual(session["ai_scout_call_counts"][key], 1)


if __name__ == "__main__":
    unittest.main()
