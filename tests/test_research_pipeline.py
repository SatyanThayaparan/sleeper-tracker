"""Two-stage AI Scout tests: no paid API calls and no invented sources."""
import json
import unittest
from types import SimpleNamespace

from research_pipeline import (
    extract_search_sources, normalized_source_url,
    stage1_search, stage2_analyze, research_player, response_text,
)


class FakeClient:
    def __init__(self, *, with_sources=True, fabricated_id=False):
        self.calls = []
        self.with_sources = with_sources
        self.fabricated_id = fabricated_id

    @property
    def responses(self):
        return self

    def create(self, **params):
        self.calls.append(params)
        if len(self.calls) % 2:
            sources = ([{"url": "https://sports.yahoo.com/fantasy/real-ranking?utm_source=x",
                         "title": "Fantasy basketball points-league rankings"}]
                       if self.with_sources else [])
            return {
                "output_text": "Yahoo Fantasy's points-league rankings discuss Player A's role.",
                "output": [
                    {"type": "web_search_call", "action": {"sources": sources}}
                ],
            }
        return {
            "output_text": json.dumps({
                "name": "Player A",
                "summary": "A points-league option with flexible guard eligibility.",
                "role_outlook": "Potential starter",
                "availability_risk": "Verify recent injury status",
                "draft_fit": "PG depth",
                "why_now": "ADP might be earlier than your next turn",
                "expert_take": "Yahoo analysis mentions the player",
                "findings": [{
                    "source_id": "S77" if self.fabricated_id else "S1",
                    "claim": "Points ranking discusses this player's fantasy role",
                    "reported_date": "Unverified",
                    "ranking_format": "Points league",
                }],
            }),
            "output": [],
        }


class PipelineTests(unittest.TestCase):
    def test_source_urls_normalized_without_cross_article_matching(self):
        self.assertEqual(
            normalized_source_url("http://www.espn.com/fantasy/x/?utm=x#top"),
            "https://espn.com/fantasy/x",
        )
        self.assertNotEqual(
            normalized_source_url("https://espn.com/fantasy/player-a"),
            normalized_source_url("https://espn.com/fantasy/player-b"),
        )
        self.assertEqual(normalized_source_url("ftp://example.org/a"), "")
        self.assertEqual(normalized_source_url("https://localhost/admin"), "")
        self.assertNotEqual(
            normalized_source_url("https://espn.com/view?id=123&utm_source=a"),
            normalized_source_url("https://espn.com/view?id=456"),
        )

    def test_collects_sources_from_action_and_inline_annotations(self):
        response = {
            "output": [
                {"type": "web_search_call", "action": {
                    "sources": [{"url": "https://www.nba.com/news/player-a",
                                 "title": "NBA report"}]}},
                {"type": "message", "content": [
                    {"annotations": [
                        {"url": "https://nba.com/news/player-a?tracking=1"},
                        {"url": "https://espn.com/nba/report", "title": "ESPN"}
                    ]}
                ]},
            ]
        }
        sources = extract_search_sources(response)
        self.assertEqual(len(sources), 2)
        self.assertEqual([s["id"] for s in sources], ["S1", "S2"])
        self.assertEqual(sources[0]["title"], "NBA report")

    def test_independent_web_search_then_non_web_analysis(self):
        fake = FakeClient()
        result = research_player(fake, {
            "player": "Player A", "team": "TOR", "position": "PG, SG",
            "roster": "Adds PG depth", "blend_adp": 50, "score": 48,
            "eligible_depth": {"PG": 1, "SG": 6},
        }, open_slots=["PG"], context={"roster_eligible_counts": {
            "PG": 1, "SG": 6, "C": 2
        }})
        self.assertEqual(len(fake.calls), 2)
        self.assertEqual(fake.calls[0]["tools"][0]["type"], "web_search")
        self.assertEqual(fake.calls[0]["tool_choice"], "required")
        self.assertNotIn("tools", fake.calls[1])
        self.assertIn('"SG": 6', fake.calls[1]["input"])
        self.assertIn("source_id", fake.calls[1]["text"]["format"]["schema"]["properties"]["findings"]["items"]["properties"])
        self.assertEqual(result["source_status"]["sources"], 1)
        self.assertEqual(result["player"]["name"], "Player A")
        self.assertIn("points-league option", result["player"]["recent_findings"])

    def test_fabricated_source_id_is_discarded_but_summary_kept(self):
        fake = FakeClient(fabricated_id=True)
        result = research_player(fake, {"player": "Player A"}, open_slots=[])
        self.assertEqual(result["player"]["verified_expert_evidence"], [])
        self.assertIn("points-league option", result["player"]["recent_findings"])

    def test_no_search_sources_cannot_masquerade_as_cited(self):
        fake = FakeClient(with_sources=False)
        result = research_player(fake, {"player": "Player A"}, open_slots=[])
        self.assertEqual(result["player"]["verified_expert_evidence"], [])
        self.assertEqual(result["sources"], [])

    def test_wrong_player_does_not_erase_paid_search_brief(self):
        class Wrong(FakeClient):
            def create(self, **params):
                response = super().create(**params)
                if len(self.calls) == 2:
                    obj = json.loads(response["output_text"])
                    obj["name"] = "Different Player"
                    response["output_text"] = json.dumps(obj)
                return response
        result = research_player(Wrong(), {"player": "Player A"}, open_slots=[])
        self.assertEqual(result["analysis_status"], "retrieval_only")
        self.assertEqual(result["player"]["name"], "Player A")
        self.assertIn("Yahoo Fantasy", result["player"]["recent_findings"])
        self.assertEqual(result["player"]["verified_expert_evidence"], [])
        self.assertTrue(result["sources"])
        self.assertIn("different player", result["analysis_error"])

    def test_raw_output_message_text_is_accepted(self):
        response = {"output_text": "", "output": [
            {"type": "message", "content": [
                {"type": "output_text", "text": "Research summary found."}
            ]}
        ]}
        self.assertEqual(response_text(response), "Research summary found.")

    def test_search_with_sources_without_summary_is_preserved(self):
        class SourcesOnly:
            def __init__(self):
                self.calls = []
            @property
            def responses(self):
                return self
            def create(self, **params):
                self.calls.append(params)
                return {"output_text": "", "status": "incomplete",
                        "incomplete_details": {"reason": "max_output_tokens"},
                        "output": [{"type": "web_search_call", "action": {
                            "sources": [{"url": "https://nba.com/news/player-a",
                                         "title": "News"}]}}]}
        result = stage1_search(SourcesOnly(), "Player A", model="gpt-4.1-mini")
        self.assertEqual(len(result["sources"]), 1)
        self.assertIn("no written research summary", result["brief"])

    def test_truncated_analysis_keeps_search_brief_and_links(self):
        class Incomplete(FakeClient):
            def create(self, **params):
                result = super().create(**params)
                if len(self.calls) == 2:
                    result = {"output_text": "", "output": [],
                              "status": "incomplete",
                              "incomplete_details": {"reason": "max_output_tokens"}}
                return result
        client = Incomplete()
        result = research_player(client, {"player": "Player A"}, open_slots=[])
        self.assertEqual(result["analysis_status"], "retrieval_only")
        self.assertIn("Yahoo Fantasy", result["player"]["recent_findings"])
        self.assertEqual(len(result["sources"]), 1)
        self.assertIn("incomplete_reason=max_output_tokens", result["analysis_error"])
        self.assertEqual(client.calls[0]["max_output_tokens"], 3500)
        self.assertEqual(client.calls[1]["max_output_tokens"], 2600)
        self.assertEqual(result["player"]["verified_expert_evidence"], [])


if __name__ == "__main__":
    unittest.main()
