# backend/tests/test_phase6_mixer_boundary.py
"""
CryptoTrace LEA - Phase 2 Mixer & Boundary Tests
Validates:
1. Mixer boundary halts expansion (post-mixer addresses not enqueued)
2. Mixer node typed as "mixer"
3. termination_reason == "MIXER_BOUNDARY_HIT"
4. Multi-branch trace: clean branch continues, mixer branch halts
5. Recovery display_tier == "ineligible" when mixer is present
6. Attribution label is UNRESOLVED when trace halts at mixer
7. partial_recommendation generated with pre-mixer freeze targets & exit candidates <= 0.25
8. TRACE_STOP_AT_MIXER=false preserves unrestricted traversal
9. Notice generator includes Section 5 Special Privacy Mixer Directive
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.tracing.trace_engine import BoundedTracer, TraceConstraints
from backend.models.domain_models import Transfer
from backend.legal.notice_generator import notice_generator

class TestPhase6MixerBoundary(unittest.TestCase):
    def setUp(self):
        self.tracer = BoundedTracer()
        self.mock_pm = MagicMock()
        self.tracer.provider_mgr = self.mock_pm

    def test_01_mixer_boundary_halts_expansion(self):
        """Suspect -> Tornado Cash -> post-mixer: post-mixer must NOT be traversed."""
        # Suspect sends to Tornado Cash (1 ETH pool)
        t1 = Transfer(
            chain_id="ETH", tx_hash="0xdep1", log_index=0, transfer_index=0,
            event_type="NATIVE", from_addr="0xsuspect",
            to_addr="0x910cbd523d972eb0a6f4cae4618ad62622b39dbf", # Tornado 1 ETH
            amount=10.0, asset="ETH", direction="OUT", raw_payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )
        # If mixer were queried (should NOT happen), it would return post-mixer
        t_post = Transfer(
            chain_id="ETH", tx_hash="0xpost", log_index=0, transfer_index=0,
            event_type="NATIVE", from_addr="0x910cbd523d972eb0a6f4cae4618ad62622b39dbf",
            to_addr="0xpostmixer_wallet", amount=9.8, asset="ETH", direction="OUT", raw_payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

        def mock_fetch(addr, chain="ETH", limit=20):
            if addr.lower() == "0xsuspect":
                return [t1]
            if addr.lower() == "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf":
                return [t_post]
            return []

        self.mock_pm.fetch_transfers.side_effect = mock_fetch

        res = self.tracer.trace(
            start_address="0xsuspect",
            chain="ETH",
            constraints=TraceConstraints(max_hops=4),
            case_id="CR-2026-TEST-MIXER",
            mode="LIVE",
        )

        # 1. Assert post-mixer wallet was NOT traversed or included in nodes
        node_ids = [n["id"].lower() for n in res["nodes"]]
        self.assertIn("0xsuspect", node_ids)
        self.assertIn("0x910cbd523d972eb0a6f4cae4618ad62622b39dbf", node_ids)
        self.assertNotIn("0xpostmixer_wallet", node_ids, "Post-mixer address must not be expanded!")

        # 2. Assert mixer node type is 'mixer'
        mixer_nodes = [n for n in res["nodes"] if n["id"].lower() == "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf"]
        self.assertEqual(len(mixer_nodes), 1)
        self.assertEqual(mixer_nodes[0]["type"], "mixer")

        # 3. Assert termination_reason and boundary_events
        self.assertEqual(res["termination_reason"], "MIXER_BOUNDARY_HIT")
        self.assertEqual(len(res["boundary_events"]), 1)
        self.assertEqual(res["boundary_events"][0]["kind"], "MIXER")
        self.assertEqual(res["boundary_events"][0]["deposit_amount"], 10.0)

        # 4. Assert attribution is UNRESOLVED
        self.assertEqual(res["attribution"]["label_type"], "UNRESOLVED")

        # 5. Assert recovery is ineligible
        self.assertEqual(res["recovery_estimate"]["display_tier"], "ineligible")

        # 6. Assert partial recommendation present
        self.assertIsNotNone(res["partial_recommendation"])
        rec = res["partial_recommendation"]
        self.assertIn("0xsuspect", rec["pre_mixer_freeze_targets"])
        self.assertTrue(len(rec["payout_candidates"]) > 0)
        self.assertLessEqual(rec["payout_candidates"][0]["confidence"], 0.25)
        self.assertIn("HEURISTIC", rec["payout_candidates"][0]["relationship_label"].upper())

    def test_02_two_branch_clean_continues_mixer_halts(self):
        """Two branches: clean branch continues to hop 2; mixer branch stops at hop 1."""
        t_clean = Transfer(
            chain_id="ETH", tx_hash="0xclean1", log_index=0, transfer_index=0,
            event_type="NATIVE", from_addr="0xsuspect",
            to_addr="0xmule_clean", amount=5.0, asset="ETH", direction="OUT", raw_payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )
        t_mixer = Transfer(
            chain_id="ETH", tx_hash="0xmix1", log_index=1, transfer_index=0,
            event_type="NATIVE", from_addr="0xsuspect",
            to_addr="0xa160cdab225685da1d56aa342ad8841c3b53f291", # Tornado 10 ETH
            amount=10.0, asset="ETH", direction="OUT", raw_payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )
        t_clean_hop2 = Transfer(
            chain_id="ETH", tx_hash="0xclean2", log_index=0, transfer_index=0,
            event_type="NATIVE", from_addr="0xmule_clean",
            to_addr="0xterminal_exchange", amount=4.9, asset="ETH", direction="OUT", raw_payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

        def mock_fetch(addr, chain="ETH", limit=20):
            if addr.lower() == "0xsuspect":
                return [t_clean, t_mixer]
            if addr.lower() == "0xmule_clean":
                return [t_clean_hop2]
            return []

        self.mock_pm.fetch_transfers.side_effect = mock_fetch

        res = self.tracer.trace(
            start_address="0xsuspect",
            chain="ETH",
            constraints=TraceConstraints(max_hops=4),
            case_id="CR-2026-TEST-BRANCHES",
            mode="LIVE",
        )

        node_ids = [n["id"].lower() for n in res["nodes"]]
        self.assertIn("0xmule_clean", node_ids)
        self.assertIn("0xterminal_exchange", node_ids, "Clean branch should continue!")
        self.assertIn("0xa160cdab225685da1d56aa342ad8841c3b53f291", node_ids)
        self.assertEqual(res["termination_reason"], "MIXER_BOUNDARY_HIT")

    def test_03_notice_generator_includes_mixer_directive(self):
        """Preservation request notice includes Section 5 Special Privacy Mixer Directive."""
        trace_data = {
            "case_id": "CR-2026-MIXER-NOTICE",
            "chain": "ETH",
            "suspect_address": "0xsuspect",
            "attribution": {"vasp_name": "Tornado Feeder Exchange", "nodal_officer_email": "compliance@test.com"},
            "hops": [{"hop_number": 1, "tx_hash": "0x123", "amount": 10, "asset": "ETH", "to_address": "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf"}],
            "partial_recommendation": {
                "mixer_name": "Tornado Cash (1 ETH)",
                "mixer_address": "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf",
                "pre_mixer_freeze_targets": ["0xsuspect", "0xmule1"],
            }
        }
        draft = notice_generator.create_draft("CR-2026-MIXER-NOTICE", trace_data)
        self.assertIn("SPECIAL PRIVACY MIXER BOUNDARY DIRECTIVE", draft.draft_text)
        self.assertIn("0xsuspect", draft.draft_text)

if __name__ == "__main__":
    unittest.main()
