"""
CryptoTrace LEA — Phase 5 Polish & Completeness Tests (§11.2)
Unit tests for all Phase 5 implementations:
  1. §8.7 — Data completeness KPI metrics & horizons
  2. OFAC entity-name fuzzy screening
  3. AI Copilot fraud-type & completeness prompt grounding
  4. INR / USD dual display across trace root and hops
  5. Standardized VASP geo-mapping & GET /api/v1/vasps/geo endpoint
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
from engine.ofac_sanctions import fuzzy_screen_ofac_entity, bulk_fuzzy_screen_entities
from engine.ai_copilot import chat_copilot, summarize_case, _generate_rule_based_briefing
from backend.tracing.trace_engine import bounded_tracer, TraceConstraints
from backend.attribution.vasp_registry import VASP_REGISTRY, get_vasp_geo_summary
from backend.auth.jwt_handler import create_access_token


class TestOFACFuzzyScreening(unittest.TestCase):
    """OFAC SDN entity-name fuzzy matching."""

    def test_ofac_fuzzy_entity_positive(self):
        """Positive test: Matching 'Lazarus Group' finds known OFAC entries with high ratio."""
        hits = fuzzy_screen_ofac_entity("Lazarus Group", threshold=0.85)
        self.assertIsInstance(hits, list)
        self.assertGreater(len(hits), 0)
        top = hits[0]
        self.assertIn("Lazarus", top.get("entity", ""))
        self.assertGreaterEqual(top["match_ratio"], 0.85)
        self.assertIn("address", top)

    def test_ofac_fuzzy_entity_typo(self):
        """Positive test: Matching with minor typo 'Tornado Csh' finds Tornado Cash entries."""
        hits = fuzzy_screen_ofac_entity("Tornado Csh", threshold=0.85)
        self.assertIsInstance(hits, list)
        self.assertGreater(len(hits), 0)
        self.assertIn("Tornado Cash", hits[0]["entity"])

    def test_ofac_fuzzy_entity_negative(self):
        """Negative test: Non-existent entity name returns empty hit list."""
        hits = fuzzy_screen_ofac_entity("TotallyLegitPerson12345XYZ", threshold=0.85)
        self.assertEqual(hits, [])

    def test_bulk_fuzzy_screen_entities(self):
        """Batch fuzzy screening over multiple entity queries."""
        results = bulk_fuzzy_screen_entities(["Garantex", "NonExistentBank999"], threshold=0.85)
        self.assertIn("Garantex", results)
        self.assertIn("NonExistentBank999", results)
        self.assertGreater(len(results["Garantex"]), 0)
        self.assertEqual(len(results["NonExistentBank999"]), 0)


class TestAICopilotContext(unittest.TestCase):
    """AI Copilot fraud-type and data completeness grounding."""

    def test_rule_based_briefing_fraud_query(self):
        """Rule-based engine returns crime category and completeness when queried."""
        sample_prompt = """
        Investigator Query: what is the crime type and data completeness?
        "fraud_type": "INVESTMENT_TASK_SCAM"
        "data_completeness_pct": 85.0
        "name": "Binance Global"
        "amount_lost_inr": 250000
        "deposit_address": "0x28c6c06298d514db089934071355e5743bf21d60"
        "nodal_email": "compliance@binance.com"
        """
        response = _generate_rule_based_briefing(sample_prompt)
        self.assertIn("INVESTMENT_TASK_SCAM", response)
        self.assertIn("85.0%", response)

    def test_chat_copilot_trace_data_enrichment(self):
        """chat_copilot enriches trace_data with display flags before serializing."""
        trace_data = {
            "fraud_type": "RANSOMWARE_EXTORTION",
            "data_completeness_pct": 72.5,
            "time_window_truncations": 1,
            "partial_result": True,
            "ofac_sanction_hit": True,
        }
        res = chat_copilot("What is the fraud type?", trace_data=trace_data)
        self.assertIn("text", res)
        # Check that trace_data dictionary was mutated with the standard helper keys
        self.assertEqual(trace_data.get("crime_category"), "RANSOMWARE_EXTORTION")
        self.assertEqual(trace_data.get("data_completeness_pct_display"), "72.5%")
        self.assertTrue(trace_data.get("partial_trace_warning"))
        self.assertEqual(trace_data.get("sanctions_nexus"), "CRITICAL OFAC HIT")

    def test_summarize_case_enrichment(self):
        """summarize_case embeds fraud_type and completeness into the LLM prompt."""
        trace_data = {
            "fraud_type": "IMPERSONATION_PHISHING",
            "data_completeness_pct": 92.5,
            "time_window_truncations": 0,
            "partial_result": False,
            "suspect_address": "0x1234567890123456789012345678901234567890",
            "chain": "ETH",
            "nearest_vasp": {"name": "WazirX", "confidence": 90},
            "path_summary": {"total_hops": 2},
        }
        res = summarize_case(trace_data)
        self.assertIn("text", res)


class TestTraceEngineDualCurrency(unittest.TestCase):
    """INR / USD dual currency output across root results and hops."""

    def test_inr_usd_dual_display(self):
        """Root trace result contains both traced_value_usd and traced_value_inr."""
        res = bounded_tracer.trace(
            start_address="0x89205a3e3b2a69de6dbf7f01ed13b2108b2c43e7",
            chain="ETH",
            constraints=TraceConstraints(max_hops=3),
            case_id="CR-TEST-PHASE5-DUAL",
            mode="DEMO",
        )
        self.assertIn("traced_value_usd", res)
        self.assertIn("traced_value_inr", res)
        self.assertIn("inr_conversion_rate", res)
        self.assertAlmostEqual(res["inr_conversion_rate"], 83.5)
        self.assertAlmostEqual(res["traced_value_inr"], round(res["traced_value_usd"] * 83.5, 2))

    def test_hop_amounts_dual_currency(self):
        """Every forward and backward hop contains both amount_usd and amount_inr."""
        res = bounded_tracer.trace(
            start_address="0x89205a3e3b2a69de6dbf7f01ed13b2108b2c43e7",
            chain="ETH",
            constraints=TraceConstraints(max_hops=3, direction="BIDIRECTIONAL", max_backward_hops=1),
            case_id="CR-TEST-PHASE5-HOPS",
            mode="DEMO",
        )
        for h in res.get("hops", []):
            self.assertIn("amount_usd", h)
            self.assertIn("amount_inr", h)
            self.assertAlmostEqual(h["amount_inr"], round(h["amount_usd"] * 83.5, 2))

        for bh in res.get("backward_hops", []):
            self.assertIn("amount_usd", bh)
            self.assertIn("amount_inr", bh)
            self.assertAlmostEqual(bh["amount_inr"], round(bh["amount_usd"] * 83.5, 2))


class TestVASPGeoMapping(unittest.TestCase):
    """VASP geographic coordinates and /api/v1/vasps/geo route."""

    def setUp(self):
        self.client = TestClient(app)
        self.token = create_access_token({"username": "investigator1", "role": "INVESTIGATOR"})
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    def test_vasp_geo_fields_present_in_registry(self):
        """All VASP entries have country, geo_region, geo_lat, geo_lng, and fatf_greylist."""
        self.assertGreater(len(VASP_REGISTRY), 10)
        for key, data in VASP_REGISTRY.items():
            self.assertIn("country", data, f"Missing country for {key}")
            self.assertIn("geo_region", data, f"Missing geo_region for {key}")
            self.assertIn("geo_lat", data, f"Missing geo_lat for {key}")
            self.assertIn("geo_lng", data, f"Missing geo_lng for {key}")
            self.assertIn("fatf_greylist", data, f"Missing fatf_greylist for {key}")
            self.assertIsInstance(data["geo_lat"], float)
            self.assertIsInstance(data["geo_lng"], float)

    def test_get_vasp_geo_summary(self):
        """get_vasp_geo_summary returns populated dictionary with geo attributes."""
        summary = get_vasp_geo_summary()
        self.assertIn("WAZIRX", summary)
        self.assertIn("BINANCE", summary)
        wazirx = summary["WAZIRX"]
        self.assertEqual(wazirx["country"], "IN")
        self.assertEqual(wazirx["fiu_status"], "REGISTERED")
        self.assertAlmostEqual(wazirx["lat"], 19.0760)

    def test_vasp_geo_endpoint(self):
        """GET /api/v1/vasps/geo returns HTTP 200 and geo data when authenticated."""
        resp = self.client.get("/api/v1/vasps/geo", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, dict)
        self.assertIn("COINDCX", data)
        self.assertIn("lat", data["COINDCX"])
        self.assertIn("lng", data["COINDCX"])


class TestDataCompletenessMetric(unittest.TestCase):
    """§8.7: Data completeness score, window truncation, and partial warning."""

    def test_data_completeness_kpi_fields(self):
        """Trace result exposes all required data completeness metrics."""
        res = bounded_tracer.trace(
            start_address="0x89205a3e3b2a69de6dbf7f01ed13b2108b2c43e7",
            chain="ETH",
            constraints=TraceConstraints(max_hops=3),
            case_id="CR-TEST-PHASE5-COMP",
            mode="DEMO",
        )
        self.assertIn("data_completeness_pct", res)
        self.assertIsInstance(res["data_completeness_pct"], (int, float))
        self.assertGreaterEqual(res["data_completeness_pct"], 10.0)
        self.assertLessEqual(res["data_completeness_pct"], 100.0)
        self.assertIn("time_window_truncations", res)
        self.assertIn("partial_result", res)
        self.assertIn("earliest_transaction_date", res)


if __name__ == "__main__":
    unittest.main()
