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
                             "draft_fit": "Open PG", "evidence_date": "Unverified"}
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
        self.assertEqual(result["report"]["recommended_player"], "Example Guard")
        self.assertEqual(captured[0]["tools"][0]["type"], "web_search")
        self.assertEqual(captured[0]["store"], False)
        self.assertEqual(captured[0]["text"]["format"]["type"], "json_schema")
        self.assertIn("research", captured[0]["instructions"].lower())
        self.assertEqual(len(captured), 1)

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
