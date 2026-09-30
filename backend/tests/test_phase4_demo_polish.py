# backend/tests/test_phase4_demo_polish.py
"""
CryptoTrace LEA — Phase 4 Unit Tests: Demo-Visible Polish & Remaining PS Coverage
Verifies:
- §5.1 Capped hop-decay penalty at -0.20 and deep trace partial scoring
- §5.2 Ranked multi-VASP candidates for ambiguous matches
- §6.2 VASP registry expansion from free sources & address tag lookups
- §6.3 FIU-IND compliance auto-draft on notices (PMLA 12A + nodal email)
- §1.5 / §2.4 Convergence tracking & CONSOLIDATION_FUNNEL typology rule
- §4.2 Fraud-type recovery weighting (+5 task-based, -30 darknet, -10 ransomware)
- §7.2 LEA aggregate analytics dashboard endpoint & queries
- §8.6 WebSocket live trace stream manager & progress event emission
"""

import os
import sys
import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
from backend.attribution.adaptive_vasp_scorer import AdaptiveVASPScorer
from backend.attribution.vasp_registry import VASP_REGISTRY, lookup_address_tags, check_chainabuse_reports
from backend.legal.notice_generator import LegalNoticeGenerator
from backend.assessment.recovery_estimate import RecoveryEstimator
from backend.typologies.rules.other_rules import ConsolidationFunnelRule
from backend.tracing.trace_engine import BoundedTracer, TraceConstraints
from backend.api.ws_routes import TraceStreamManager, emit_trace_event
from backend.db.database import canonical_db


class TestPhase4DemoPolish(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.scorer = AdaptiveVASPScorer()
        cls.recovery_estimator = RecoveryEstimator()
        cls.notice_gen = LegalNoticeGenerator()
        cls.conv_rule = ConsolidationFunnelRule()

    # =========================================================================
    # §5.1: Capped Hop-Decay Penalty & Deep Trace Scoring
    # =========================================================================
    def test_5_1_hop_decay_cap_and_deep_trace_partial(self):
        """
        Verify §5.1: Hop-decay penalty is capped at -0.20 (20 pts) so deep traces
        (hop 4, hop 5) do not collapse valid cluster evidence to 0.
        """
        trace_data = {"data_completeness_pct": 95.0}

        # Hop 1: penalty should be 0.0
        score_hop1 = self.scorer.score_candidate("WAZIRX", trace_data, hop_count=1)
        self.assertEqual(score_hop1.score_components.get("b_hop_decay"), 0.0)

        # Hop 2: (2-1)*0.08 = 0.08 penalty
        score_hop2 = self.scorer.score_candidate("WAZIRX", trace_data, hop_count=2)
        self.assertAlmostEqual(score_hop2.score_components.get("b_hop_decay"), -0.08, places=2)

        # Hop 4: Uncapped would be (4-1)*0.08 = 0.24, must be capped at 0.20
        score_hop4 = self.scorer.score_candidate("WAZIRX", trace_data, hop_count=4)
        self.assertEqual(score_hop4.score_components.get("b_hop_decay"), -0.20)

        # Hop 6: Uncapped would be (6-1)*0.08 = 0.40, must remain capped at 0.20
        score_hop6 = self.scorer.score_candidate("WAZIRX", trace_data, hop_count=6)
        self.assertEqual(score_hop6.score_components.get("b_hop_decay"), -0.20)
        self.assertGreater(score_hop6.score, 0, "Deep hop trace should not collapse to 0")

    # =========================================================================
    # §5.2: Ranked Multi-VASP Candidates
    # =========================================================================
    def test_5_2_ranked_multi_vasp_candidates(self):
        """
        Verify §5.2: Adaptive VASP Scorer ranks all candidate VASPs descending,
        allowing investigators to notify all co-custody or ambiguous entities.
        """
        trace_data = {"data_completeness_pct": 95.0}
        candidates = ["BYBIT", "WAZIRX", "ZEBPAY"]

        ranked = self.scorer.score_all_candidates(
            candidate_keys=candidates,
            trace_result=trace_data,
            hop_count=2,
            is_exact_wallet_match=True,
        )

        self.assertEqual(len(ranked), 3)
        # Scores must be sorted descending
        for i in range(len(ranked) - 1):
            self.assertGreaterEqual(ranked[i].score, ranked[i + 1].score)

        # Indian FIU-registered exchanges (WazirX / ZebPay) score higher than offshore Bybit
        top_names = [r.vasp_name for r in ranked[:2]]
        self.assertTrue(any("WazirX" in n for n in top_names))

        # Trace engine integration: check raw_result contains ranked_vasp_candidates
        tracer = BoundedTracer()
        res = tracer.trace(
            start_address="0x28c6c06298d514db089934071355e5743bf21d60",
            chain="ETH",
            constraints=TraceConstraints(max_hops=1),
            case_id="CR-P4-RANKED-TEST",
            mode="DEMO",
        )
        self.assertIn("ranked_vasp_candidates", res)
        self.assertIsInstance(res["ranked_vasp_candidates"], list)

    # =========================================================================
    # §6.2: VASP Registry Expansion & Free Tag Lookup
    # =========================================================================
    def test_6_2_vasp_registry_expansion_and_tags(self):
        """
        Verify §6.2: Registry contains expanded India-relevant and global VASPs,
        and public tag lookup resolves them correctly without external paid API.
        """
        # Domestic VASPs added in Phase 4
        self.assertIn("MUDREX", VASP_REGISTRY)
        self.assertIn("BITBNS", VASP_REGISTRY)
        self.assertIn("GIOTTUS", VASP_REGISTRY)
        self.assertIn("COINSWITCH", VASP_REGISTRY)
        self.assertIn("BUYUCOIN", VASP_REGISTRY)

        # Global VASPs added in Phase 4
        self.assertIn("OKX", VASP_REGISTRY)
        self.assertIn("MEXC", VASP_REGISTRY)
        self.assertIn("GATEIO", VASP_REGISTRY)

        # Address Tag Lookup (Positive)
        mudrex_addr = "0x3d3c761b0c95d8208466b0a8801d0c4e12e12e01"
        tag_info = lookup_address_tags(mudrex_addr)
        self.assertEqual(tag_info["vasp_key"], "MUDREX")
        self.assertEqual(tag_info["category"], "Exchange")

        # Address Tag Lookup (Negative: Unlabeled)
        random_addr = "0x9999999999999999999999999999999999999999"
        unlabeled = lookup_address_tags(random_addr)
        self.assertEqual(unlabeled["tag"], "Unlabeled")
        self.assertIsNone(unlabeled["vasp_key"])

        # Chainabuse reports helper structure
        report = check_chainabuse_reports(random_addr)
        self.assertEqual(report["address"], random_addr)
        self.assertIn("abuse_flagged", report)

    # =========================================================================
    # §6.3: FIU-IND Compliance Auto-Draft Notices
    # =========================================================================
    def test_6_3_fiu_compliance_auto_draft_notice(self):
        """
        Verify §6.3: Notice generator auto-populates verified nodal officer email
        and statutory Section 12A PMLA 2002 clause for FIU-IND registered VASPs.
        """
        # Case 1: FIU-IND Registered VASP (WazirX)
        trace_registered = {
            "case_id": "CR-P4-NOTICE-FIU",
            "chain": "ETH",
            "suspect_address": "0xsuspect_addr_123",
            "hops": [{"hop_number": 1, "amount": 10000.0, "asset": "USDT", "tx_hash": "0xtx1", "to_address": "0x28c6c..."}],
            "attribution": {
                "vasp_key": "WAZIRX",
                "vasp_name": "Zanmai Labs Pvt Ltd (WazirX)",
                "fiu_status": "REGISTERED",
                "nodal_officer_email": "nodal@wazirx.com",
                "label_type": "VERIFIED",
            },
        }

        draft_fiu = self.notice_gen.create_draft("CR-P4-NOTICE-FIU", trace_registered)
        self.assertIn("nodal@wazirx.com", draft_fiu.draft_text)
        self.assertIn("SECTION 12A OF THE PREVENTION OF MONEY LAUNDERING ACT", draft_fiu.draft_text)
        self.assertIn("MANDATORY REPORTING ENTITY", draft_fiu.draft_text)

        # Case 2: Offshore Unregistered VASP (Bybit) -> Negative test for Section 12A PMLA
        trace_unregistered = {
            "case_id": "CR-P4-NOTICE-OFFSHORE",
            "chain": "ETH",
            "suspect_address": "0xsuspect_addr_456",
            "hops": [{"hop_number": 1, "amount": 5000.0, "asset": "USDT", "tx_hash": "0xtx2", "to_address": "0xf89d..."}],
            "attribution": {
                "vasp_key": "BYBIT",
                "vasp_name": "Bybit Fintech Ltd",
                "fiu_status": "UNREGISTERED",
                "nodal_officer_email": "compliance@bybit.com",
                "label_type": "INFERRED",
            },
        }

        draft_offshore = self.notice_gen.create_draft("CR-P4-NOTICE-OFFSHORE", trace_unregistered)
        self.assertNotIn("SECTION 12A OF THE PREVENTION OF MONEY LAUNDERING ACT", draft_offshore.draft_text)
        self.assertNotIn("MANDATORY REPORTING ENTITY", draft_offshore.draft_text)

    # =========================================================================
    # §1.5 / §2.4: Convergence Tracking & CONSOLIDATION_FUNNEL Typology
    # =========================================================================
    def test_1_5_and_2_4_convergence_and_consolidation_funnel(self):
        """
        Verify §1.5 & §2.4: Multiple incoming branches converging into a single
        intermediate wallet tag node as consolidation_hop and fire CONSOLIDATION_FUNNEL.
        """
        # Synthetic trace with 2 branches merging into 0xcollector_wallet
        convergent_trace = {
            "case_id": "CR-CONV-TEST",
            "chain": "ETH",
            "data_completeness_pct": 90.0,
            "edges": [
                {"from": "0xvictim_a", "to": "0xcollector_wallet", "amount": 25000.0, "asset": "USDT"},
                {"from": "0xvictim_b", "to": "0xcollector_wallet", "amount": 35000.0, "asset": "USDT"},
                {"from": "0xcollector_wallet", "to": "0xvasp_deposit", "amount": 59500.0, "asset": "USDT"},
            ],
            "nodes": [
                {"id": "0xvictim_a", "type": "suspect"},
                {"id": "0xvictim_b", "type": "suspect"},
                {"id": "0xcollector_wallet", "type": "intermediary"},
                {"id": "0xvasp_deposit", "type": "vasp"},
            ],
            "hops": [],
        }

        # 1. Test ConsolidationFunnelRule directly
        finding = self.conv_rule.evaluate(convergent_trace, "CR-CONV-TEST")
        self.assertIsNotNone(finding)
        self.assertEqual(finding.typology_name, "CONSOLIDATION_FUNNEL")
        self.assertEqual(finding.evidence_json.get("convergence_address"), "0xcollector_wallet")
        self.assertEqual(finding.evidence_json.get("inbound_branch_count"), 2)

        # 2. Test Negative: Linear chain with no convergence
        linear_trace = {
            "case_id": "CR-LINEAR-TEST",
            "chain": "ETH",
            "data_completeness_pct": 90.0,
            "edges": [
                {"from": "0xaddr_1", "to": "0xaddr_2", "amount": 10000.0, "asset": "ETH"},
                {"from": "0xaddr_2", "to": "0xaddr_3", "amount": 9900.0, "asset": "ETH"},
            ],
            "nodes": [
                {"id": "0xaddr_1", "type": "suspect"},
                {"id": "0xaddr_2", "type": "intermediary"},
                {"id": "0xaddr_3", "type": "vasp"},
            ],
            "hops": [],
        }
        no_finding = self.conv_rule.evaluate(linear_trace, "CR-LINEAR-TEST")
        self.assertIsNone(no_finding)

    # =========================================================================
    # §4.2: Fraud-Type Recovery Modifiers
    # =========================================================================
    def test_4_2_fraud_type_recovery_modifiers(self):
        """
        Verify §4.2: Calibrated modifiers applied per crime type:
        - Task-based fraud: +5 pts (rapid off-ramp)
        - Ransomware: -10 pts (prolonged negotiation delay)
        - Darknet: -30 pts (near-zero recovery baseline)
        """
        # Baseline eligible parameters
        base_kwargs = {
            "case_id": "CR-FT-TEST",
            "traced_amount_usd": 25000.0,
            "data_completeness_pct": 90.0,
            "attribution_confidence": "HIGH",
            "is_fiu_registered_vasp": True,
            "hop_count": 2,
            "elapsed_hours": 12.0,
            "mixer_detected": False,
        }

        baseline_res = self.recovery_estimator.estimate_recovery(**base_kwargs, fraud_type=None)
        base_score = baseline_res.recovery_score

        # Task-Based (+5)
        task_res = self.recovery_estimator.estimate_recovery(**base_kwargs, fraud_type="TASK_BASED_FRAUD")
        self.assertEqual(task_res.recovery_score, min(95, base_score + 5))

        # Ransomware (-10)
        ransom_res = self.recovery_estimator.estimate_recovery(**base_kwargs, fraud_type="RANSOMWARE")
        self.assertEqual(ransom_res.recovery_score, base_score - 10)

        # Darknet (-30)
        darknet_res = self.recovery_estimator.estimate_recovery(**base_kwargs, fraud_type="DARKNET")
        self.assertEqual(darknet_res.recovery_score, base_score - 30)

        # Negative test: Unknown / baseline fraud type yields 0 modifier
        unknown_res = self.recovery_estimator.estimate_recovery(**base_kwargs, fraud_type="CUSTOM_FRAUD_TYPE")
        self.assertEqual(unknown_res.recovery_score, base_score)

    # =========================================================================
    # §7.2: LEA Aggregate Analytics Dashboard Endpoint
    # =========================================================================
    def test_7_2_lea_aggregate_analytics_endpoint(self):
        """
        Verify §7.2: GET /api/v1/analytics/dashboard returns aggregate metrics
        including case summary, INR totals, CRITICAL alerts count, and distributions.
        """
        resp = self.client.get("/api/v1/analytics/dashboard")
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertIn("data", payload)
        data = payload["data"]

        # Summary KPIs
        self.assertIn("summary", data)
        summary = data["summary"]
        self.assertIn("total_cases", summary)
        self.assertIn("cases_this_week", summary)
        self.assertIn("total_traced_value_inr", summary)
        self.assertIn("critical_alerts_count", summary)
        self.assertIn("avg_trace_time_ms", summary)

        # Fraud type distribution & top VASPs
        self.assertIn("fraud_type_distribution", data)
        self.assertIn("top_vasps", data)
        self.assertIsInstance(data["fraud_type_distribution"], (dict, list))
        self.assertIsInstance(data["top_vasps"], list)

    # =========================================================================
    # §8.6: WebSocket Live Trace Feed & Progress Hooks
    # =========================================================================
    def test_8_6_websocket_trace_events(self):
        """
        Verify §8.6: Live trace BFS traversal invokes progress_callback with
        HOP_COMPLETE, VASP_IDENTIFIED, and TRACE_COMPLETE events without failure.
        """
        recorded_events = []

        def mock_callback(case_id: str, event_data: dict):
            recorded_events.append(event_data)

        tracer = BoundedTracer()
        tracer.trace(
            start_address="0x28c6c06298d514db089934071355e5743bf21d60",
            chain="ETH",
            constraints=TraceConstraints(max_hops=2),
            case_id="CR-P4-WS-TEST",
            mode="DEMO",
            progress_callback=mock_callback,
        )

        event_types = [e.get("event") for e in recorded_events]
        self.assertIn("HOP_COMPLETE", event_types)
        self.assertIn("TRACE_COMPLETE", event_types)

        # Synchronous emit_trace_event safe execution test
        try:
            emit_trace_event("CR-TEST", {"event": "TEST", "status": "OK"})
        except Exception as exc:
            self.fail(f"emit_trace_event raised unexpected exception: {exc}")


if __name__ == "__main__":
    unittest.main()
