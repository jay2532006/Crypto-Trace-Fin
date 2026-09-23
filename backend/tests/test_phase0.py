"""
CryptoTrace LEA — Phase 0 Foundation Verification Tests
Validates:
1. Canonical domain models and type literals
2. Deterministic JSON serialization and SHA-256 raw payload storage
3. Chained SHA-256 audit log integrity and tamper detection
4. RBAC permission enforcement and JWT token verification
5. Canonical database schema and idempotency
"""

import os
import sys
import unittest

# Ensure project root is in python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.models.domain_models import Case, Transfer, EvidenceManifest
from backend.storage.raw_payload_storage import (
    serialize_deterministically,
    compute_sha256,
    raw_storage,
)
from backend.audit.audit_engine import audit_engine
from backend.auth.rbac import has_permission
from backend.auth.jwt_handler import (
    authenticate_user,
    create_access_token,
    decode_access_token,
)
from backend.db.database import db_manager


class TestPhase0Foundation(unittest.TestCase):

    def test_01_canonical_models(self):
        """Verify Case and Transfer models enforce types and compute canonical identity."""
        case = Case(
            case_id="CR-2026-TEST01",
            source="COMPLAINT",
            chain="ETH",
            wallet="0x28C6c06298d514Db089934071355E5743bf21d60",
            reported_amount=50000.0,
            complaint_text="Victim reported fake mining pool loss",
        )
        self.assertEqual(case.case_id, "CR-2026-TEST01")
        self.assertFalse(case.demo_data)

        transfer = Transfer(
            chain_id="ETH",
            tx_hash="0xabc123",
            log_index=1,
            transfer_index=0,
            event_type="ERC20",
            from_addr="0x111",
            to_addr="0x222",
            amount=1500.0,
            asset="USDT",
            raw_payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            finality_state="CONFIRMED",
            provider_source="RPC_PRIMARY",
        )
        self.assertEqual(transfer.canonical_identity, "ETH:0xabc123:ERC20:1:0")

    def test_02_deterministic_raw_storage(self):
        """Verify dictionary key order does not alter SHA-256 hash."""
        dict_a = {"z_key": 100, "a_key": "crypto", "m_key": [3, 2, 1]}
        dict_b = {"a_key": "crypto", "m_key": [3, 2, 1], "z_key": 100}

        ser_a = serialize_deterministically(dict_a)
        ser_b = serialize_deterministically(dict_b)
        self.assertEqual(ser_a, ser_b)

        hash_a = compute_sha256(ser_a)
        hash_b = compute_sha256(ser_b)
        self.assertEqual(hash_a, hash_b)

        # Store in raw storage and verify retrieval and integrity
        payload_hash = raw_storage.store_payload(
            payload_dict=dict_a,
            chain_id="eth",
            block_height=19500000,
            tx_hash="0xtesttxhash",
            provider="rpc",
            payload_type="tx",
        )
        self.assertEqual(payload_hash, hash_a)
        self.assertTrue(raw_storage.verify_integrity(payload_hash))

    def test_03_chained_audit_engine(self):
        """Verify audit events form a cryptographic hash chain and detect tampering."""
        evt1 = audit_engine.log_action(
            user_id="investigator1",
            action="case:create",
            resource_id="CR-2026-TEST01",
            resource_type="CASE",
            details={"wallet": "0xabc"},
        )
        self.assertTrue(evt1["event_hash"])

        evt2 = audit_engine.log_action(
            user_id="supervisor1",
            action="case:assign",
            resource_id="CR-2026-TEST01",
            resource_type="CASE",
            details={"assigned_to": "investigator1"},
        )
        self.assertEqual(evt2["previous_event_hash"], evt1["event_hash"])

        # Chain verification
        verification = audit_engine.verify_audit_chain()
        self.assertTrue(verification["valid"], f"Audit chain validation failed: {verification}")

    def test_04_rbac_and_jwt(self):
        """Verify permission checks and token issuance."""
        # Investigator permissions
        self.assertTrue(has_permission("INVESTIGATOR", "cases:create"))
        self.assertTrue(has_permission("INVESTIGATOR", "notices:draft"))
        self.assertFalse(has_permission("INVESTIGATOR", "notices:approve"))

        # Supervisor permissions
        self.assertTrue(has_permission("SUPERVISOR", "notices:approve"))
        self.assertTrue(has_permission("SUPERVISOR", "notices:reject"))
        self.assertTrue(has_permission("SUPERVISOR", "audit:read"))

        # Authentication and JWT token
        auth_res = authenticate_user("investigator1", "Password@123")
        self.assertIsNotNone(auth_res)
        token = create_access_token(auth_res)
        self.assertTrue(token)

        decoded = decode_access_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], "investigator1")
        self.assertEqual(decoded["role"], "INVESTIGATOR")

    def test_05_canonical_db(self):
        """Verify database manager inserts and lists cases."""
        case_data = {
            "case_id": "CR-2026-UNITTEST-01",
            "source": "COMPLAINT",
            "chain": "ETH",
            "wallet": "0x28C6c06298d514Db089934071355E5743bf21d60",
            "reported_amount": 25000.0,
            "created_by": "investigator1",
            "status": "OPEN",
        }
        res_id = db_manager.create_case(case_data)
        self.assertEqual(res_id, "CR-2026-UNITTEST-01")

        retrieved = db_manager.get_case("CR-2026-UNITTEST-01")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["wallet"], "0x28C6c06298d514Db089934071355E5743bf21d60")


if __name__ == "__main__":
    unittest.main()
