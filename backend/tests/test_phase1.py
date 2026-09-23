"""
CryptoTrace LEA — Phase 1 Core Intelligence Verification Tests
Validates:
1. MULE_NETWORK typology rule (India-specific 3+ wallet peel pattern, MEDIUM confidence cap)
2. MIXER_BOUNDARY typology rule (+14,400s window, 0.25 confidence, heuristic label)
3. AdaptiveVASPScorer 6-step sequence and explainable scoring steps
4. RecoveryProbabilityScore / Heuristic Recovery Estimate eligibility and action window
5. Cross-chain PROVEN vs HEURISTIC link classification
6. BoundedTracer execution and termination reasons
7. Supervisor-gated preservation notice workflow
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.typologies.rules.mule_network import mule_network_rule
from backend.typologies.rules.mixer_boundary import mixer_boundary_rule
from backend.attribution.adaptive_vasp_scorer import adaptive_vasp_scorer
from backend.assessment.recovery_estimate import recovery_estimator
from backend.assessment.risk_assessment import risk_assessor
from backend.cross_chain.cross_chain_analyzer import cross_chain_analyzer
from backend.tracing.trace_engine import bounded_tracer, TraceConstraints
from backend.legal.notice_generator import notice_generator


class TestPhase1Intelligence(unittest.TestCase):

    def test_01_mule_network_rule(self):
        """Verify MULE_NETWORK triggers on 3+ wallets and caps confidence strictly at MEDIUM."""
        # Trace with 3 single-in/single-out mule hops
        trace_data = {
            "chain": "TRON",
            "hops": [
                {"hop_number": 1, "to_address": "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW1", "amount": 50000.0, "timestamp_epoch": 1000},
                {"hop_number": 2, "to_address": "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW2", "amount": 49500.0, "timestamp_epoch": 1600},
                {"hop_number": 3, "to_address": "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW3", "amount": 49000.0, "timestamp_epoch": 2400},
                {"hop_number": 4, "to_address": "TT2T17KZhoDu47i2E4FWxfG79z45QC4t8", "amount": 48500.0, "timestamp_epoch": 3200},
            ],
            "data_completeness_pct": 95.0,
        }

        finding = mule_network_rule.evaluate(trace_data, "CR-2026-TEST-MULE")
        self.assertIsNotNone(finding, "MULE_NETWORK should be detected for 3+ fee-normalized hops")
        self.assertEqual(finding.typology_name, "MULE_NETWORK")
        self.assertEqual(finding.confidence, "MEDIUM", "MULE_NETWORK confidence must be hard-capped at MEDIUM")
        self.assertTrue(finding.india_specific)
        self.assertIn("PARTIAL", finding.uncertainty_notes)
        self.assertGreaterEqual(finding.evidence_json["wallet_count"], 3)

    def test_02_mixer_boundary_rule(self):
        """Verify MIXER_BOUNDARY enforces +14,400s window and 0.25 confidence."""
        trace_data = {
            "chain": "ETH",
            "hops": [
                {
                    "hop_number": 1,
                    "to_address": "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b",  # Tornado Cash Router
                    "amount": 10.0,
                }
            ],
            "data_completeness_pct": 80.0,
        }

        finding = mixer_boundary_rule.evaluate(trace_data, "CR-2026-TEST-MIXER")
        self.assertIsNotNone(finding)
        self.assertEqual(finding.typology_name, "MIXER_BOUNDARY")
        self.assertEqual(finding.evidence_json["confidence_score"], 0.25)
        self.assertEqual(finding.evidence_json["search_window_seconds"], 14400)
        self.assertEqual(finding.evidence_json["relationship_label"], "Possible Exit — Heuristic Only")
        self.assertIn("CRITICAL UNCERTAINTY", finding.uncertainty_notes)

    def test_03_adaptive_vasp_scorer(self):
        """Verify AdaptiveVASPScorer executes 6 steps and sets policy version."""
        trace_data = {"data_completeness_pct": 90.0}
        attribution = adaptive_vasp_scorer.score_candidate(
            vasp_key="WAZIRX",
            trace_result=trace_data,
            hop_count=1,
            is_exact_wallet_match=True,
            mixer_detected=False,
            recent_activity_days=2,
            data_completeness_pct=90.0,
        )

        self.assertEqual(attribution.policy_version, "policy_v1_india_kyc")
        self.assertEqual(attribution.label_type, "VERIFIED")
        self.assertEqual(attribution.confidence_band, "HIGH")
        self.assertGreaterEqual(attribution.score, 75)
        self.assertGreaterEqual(len(attribution.scoring_steps), 5)

        # Test Mixer penalty suppression: mixer must degrade confidence
        attr_mixer = adaptive_vasp_scorer.score_candidate(
            vasp_key="WAZIRX",
            trace_result=trace_data,
            hop_count=3,
            is_exact_wallet_match=False,
            mixer_detected=True,
            data_completeness_pct=90.0,
        )
        self.assertNotEqual(attr_mixer.confidence_band, "HIGH")
        self.assertIn(attr_mixer.label_type, ["INFERRED", "UNRESOLVED"])

    def test_04_heuristic_recovery_estimate(self):
        """Verify RecoveryEstimator eligibility gates and action window."""
        # Eligible Case: Amount >= $120, Completeness >= 70%, Attribution >= MEDIUM
        rec_eligible = recovery_estimator.estimate_recovery(
            case_id="CR-2026-TEST",
            traced_amount_usd=50000.0,
            data_completeness_pct=90.0,
            attribution_confidence="HIGH",
            is_fiu_registered_vasp=True,
            hop_count=2,
            elapsed_hours=12.0,
            mixer_detected=False,
        )
        self.assertEqual(rec_eligible.display_tier, "eligible")
        self.assertGreaterEqual(rec_eligible.recovery_score, 60)
        self.assertGreater(rec_eligible.action_window_hours, 0)
        self.assertIn("Heuristic Recovery Estimate", rec_eligible.disclaimer)

        # Ineligible Case: Below minimum value threshold ($50 < $120)
        rec_ineligible = recovery_estimator.estimate_recovery(
            case_id="CR-2026-TEST-SMALL",
            traced_amount_usd=50.0,
            data_completeness_pct=90.0,
            attribution_confidence="HIGH",
            is_fiu_registered_vasp=True,
            hop_count=2,
            elapsed_hours=12.0,
            mixer_detected=False,
        )
        self.assertEqual(rec_ineligible.display_tier, "ineligible")
        self.assertEqual(rec_ineligible.recovery_score, 0)

        # PRD FR-016 Boundary Rule: Zero-hop trace is invalid for recovery scoring
        rec_zerohop = recovery_estimator.estimate_recovery(
            case_id="CR-2026-ZEROHOP",
            traced_amount_usd=50000.0,
            data_completeness_pct=90.0,
            attribution_confidence="HIGH",
            is_fiu_registered_vasp=True,
            hop_count=0,
            elapsed_hours=12.0,
        )
        self.assertEqual(rec_zerohop.display_tier, "ineligible")
        self.assertIn("Zero-hop trace is invalid", rec_zerohop.calculation_basis)

        # PRD FR-016 Boundary Rule: LEAD top candidate is invalid for recovery scoring
        rec_lead = recovery_estimator.estimate_recovery(
            case_id="CR-2026-LEAD",
            traced_amount_usd=50000.0,
            data_completeness_pct=90.0,
            attribution_confidence="LEAD",
            is_fiu_registered_vasp=True,
            hop_count=2,
            elapsed_hours=12.0,
        )
        self.assertEqual(rec_lead.display_tier, "ineligible")
        self.assertIn("LEAD", rec_lead.calculation_basis)

    def test_05_cross_chain_proven_vs_heuristic(self):
        """Verify PROVEN smart contract link vs HEURISTIC correlation."""
        # Proven bridge
        proven_link = cross_chain_analyzer.analyze_cross_chain(
            from_chain="ETH",
            from_addr="0x111",
            to_chain="TRON",
            to_addr="T222",
            amount_from=1000.0,
            amount_to=998.0,
            time_delta_seconds=120,
            bridge_tx_hash="0xbridge_event_hash",
        )
        self.assertEqual(proven_link.link_type, "PROVEN")
        self.assertEqual(proven_link.confidence, "HIGH")

        # Heuristic correlation
        heuristic_link = cross_chain_analyzer.analyze_cross_chain(
            from_chain="ETH",
            from_addr="0x111",
            to_chain="TRON",
            to_addr="T222",
            amount_from=1000.0,
            amount_to=998.0,
            time_delta_seconds=120,
            bridge_tx_hash=None,
        )
        self.assertEqual(heuristic_link.link_type, "HEURISTIC_CORRELATION")
        self.assertIn("disclaimer", heuristic_link.supporting_evidence)

    def test_06_bounded_tracer(self):
        """Verify BoundedTracer produces complete forensic dossier with all 3 innovations."""
        result = bounded_tracer.trace(
            start_address="TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6",
            chain="TRON",
            constraints=TraceConstraints(max_hops=4),
            case_id="CR-2026-E2E-TEST",
            mode="DEMO",
        )
        self.assertIn("pattern_findings", result)
        self.assertIn("attribution", result)
        self.assertIn("risk", result)
        self.assertIn("recovery_estimate", result)
        self.assertEqual(result["termination_reason"], "MAX_HOPS")

    def test_07_legal_notice_drafting(self):
        """Verify Section 91 notice creates DRAFT without auto-submitting."""
        trace_result = {
            "case_id": "CR-2026-NOTICE-TEST",
            "chain": "TRON",
            "suspect_address": "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6",
            "attribution": {"vasp_name": "WazirX", "nodal_officer_email": "nodal@wazirx.com"},
            "hops": [{"hop_number": 1, "tx_hash": "0x123", "amount": 1000, "asset": "USDT", "to_address": "TWazirX"}],
        }
        draft = notice_generator.create_draft(
            case_id="CR-2026-NOTICE-TEST",
            trace_data=trace_result,
            investigating_officer="Inspector Sharma",
        )
        self.assertEqual(draft.status, "DRAFT")
        self.assertIn("SECTION 91 BHARATIYA NAGARIK SURAKSHA SANHITA", draft.draft_text)
        self.assertIn("nodal@wazirx.com", draft.recipient_email)


if __name__ == "__main__":
    unittest.main()
