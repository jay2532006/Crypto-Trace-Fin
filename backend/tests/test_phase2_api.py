"""
CryptoTrace LEA — Phase 2 API Verification Tests
Tests all endpoints using FastAPI TestClient:
- Case intake & listing
- Bounded trace execution with all 3 innovations
- Supervisor-gated legal notice workflow
- Cryptographic evidence & audit chain verification
- Authentication and security lockdowns (403 on arbitrary Cypher/HTTP)
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app


class TestPhase2API(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_health_and_fixtures(self):
        """Verify health check and SIH 26183 fixture listing."""
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)

        fixtures_resp = self.client.get("/api/v1/fixtures")
        self.assertEqual(fixtures_resp.status_code, 200)
        fixtures = fixtures_resp.json()
        self.assertGreaterEqual(len(fixtures), 3)
        self.assertTrue(all(f.get("demo_data") for f in fixtures))
        self.assertEqual(fixtures[0]["expected_typology"], "MULE_NETWORK")

    def test_02_auth_login_and_roles(self):
        """Verify authentication endpoint and JWT token generation."""
        # Investigator login
        resp = self.client.post("/api/v1/auth/login", json={"username": "investigator1", "password": "Password@123"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["role"], "INVESTIGATOR")

        # Supervisor login
        resp_sup = self.client.post("/api/v1/auth/login", json={"username": "supervisor1", "password": "Password@123"})
        self.assertEqual(resp_sup.status_code, 200)
        self.assertEqual(resp_sup.json()["user"]["role"], "SUPERVISOR")

    def test_03_case_intake(self):
        """Verify authorized case intake."""
        case_payload = {
            "chain": "TRON",
            "wallet": "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6",
            "reported_amount": 54200.0,
            "source": "COMPLAINT",
            "complaint_text": "Victim reported loss to mule network",
            "complainant_name": "S. Verma",
            "fir_number": "FIR-2026/89",
        }
        resp = self.client.post("/api/v1/cases", json=case_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "SUCCESS")
        case_id = data["case_id"]

        # Fetch case
        get_resp = self.client.get(f"/api/v1/cases/{case_id}")
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json()["wallet"], "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6")

    def test_04_trace_endpoint_innovations(self):
        """Verify /api/v1/trace executes bounded trace and returns all 3 innovations."""
        trace_req = {
            "address": "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6",
            "chain": "TRON",
            "case_id": "CR-2026-TEST-E2E",
            "max_hops": 4,
            "mode": "DEMO",
        }
        resp = self.client.post("/api/v1/trace", json=trace_req)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # 1. MULE_NETWORK check
        self.assertIn("pattern_findings", data)
        findings = data["pattern_findings"]
        mule_findings = [f for f in findings if f["typology_name"] == "MULE_NETWORK"]
        self.assertTrue(len(mule_findings) > 0, "MULE_NETWORK should be detected on 3-hop mule chain")
        self.assertEqual(mule_findings[0]["confidence"], "MEDIUM")

        # 2. AdaptiveVASPScorer check
        self.assertIn("attribution", data)
        attr = data["attribution"]
        self.assertEqual(attr["policy_version"], "policy_v1_india_kyc")
        self.assertIn(attr["label_type"], ["VERIFIED", "INFERRED"])
        self.assertGreater(len(attr["scoring_steps"]), 4)

        # 3. Heuristic Recovery Estimate check
        self.assertIn("recovery_estimate", data)
        rec = data["recovery_estimate"]
        self.assertEqual(rec["display_tier"], "eligible")
        self.assertGreater(rec["action_window_hours"], 0)
        self.assertIn("Heuristic Recovery Estimate", rec["disclaimer"])

    def test_05_supervisor_gated_notices(self):
        """Verify preservation request approval gate (Investigator cannot approve; Supervisor can)."""
        # Step 1: Draft notice
        trace_data = {
            "case_id": "CR-2026-NOTICE-GATED",
            "chain": "TRON",
            "suspect_address": "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6",
            "attribution": {"vasp_name": "WazirX", "nodal_officer_email": "nodal@wazirx.com"},
            "hops": [{"hop_number": 1, "tx_hash": "0x123", "amount": 54000, "asset": "USDT", "to_address": "TWazirX"}],
        }
        draft_resp = self.client.post("/api/v1/notices/draft", json={
            "case_id": "CR-2026-NOTICE-GATED",
            "trace_data": trace_data,
            "investigating_officer": "Inspector Sharma",
        })
        self.assertEqual(draft_resp.status_code, 200)
        draft = draft_resp.json()
        draft_id = draft["draft_id"]
        self.assertEqual(draft["status"], "DRAFT")

        # Step 2: Submit for approval
        sub_resp = self.client.post(f"/api/v1/notices/{draft_id}/submit")
        self.assertEqual(sub_resp.status_code, 200)
        self.assertEqual(sub_resp.json()["draft"]["status"], "PENDING_APPROVAL")

        # Step 3: Investigator attempts to approve (MUST FAIL with 403 Forbidden)
        inv_token = self.client.post("/api/v1/auth/login", json={"username": "investigator1", "password": "Password@123"}).json()["access_token"]
        inv_approve = self.client.post(
            f"/api/v1/notices/{draft_id}/approve",
            headers={"Authorization": f"Bearer {inv_token}"},
            json={"supervisor_notes": "Attempted unauthorized approval"},
        )
        self.assertEqual(inv_approve.status_code, 403, "Investigator role must NOT be allowed to approve legal notices")

        # Step 4: Supervisor approves (MUST SUCCEED)
        sup_token = self.client.post("/api/v1/auth/login", json={"username": "supervisor1", "password": "Password@123"}).json()["access_token"]
        sup_approve = self.client.post(
            f"/api/v1/notices/{draft_id}/approve",
            headers={"Authorization": f"Bearer {sup_token}"},
            json={"supervisor_notes": "Approved freeze requisition under Section 91 BNSS 2023"},
        )
        self.assertEqual(sup_approve.status_code, 200)
        self.assertEqual(sup_approve.json()["draft"]["status"], "APPROVED")

    def test_06_evidence_and_audit_verification(self):
        """Verify audit chain verification endpoint."""
        audit_resp = self.client.get("/api/v1/audit/verify-chain")
        self.assertEqual(audit_resp.status_code, 200)
        self.assertTrue(audit_resp.json()["valid"])

    def test_07_security_lockdowns(self):
        """Verify arbitrary Cypher and arbitrary HTTP requests are disabled (403 Forbidden)."""
        cypher_resp = self.client.post("/api/neo4j/query", json={"query": "MATCH (n) RETURN n"})
        self.assertEqual(cypher_resp.status_code, 403)
        self.assertIn("Security Policy Restriction", cypher_resp.json()["detail"])

        http_resp = self.client.post("/api/test/custom", json={"url": "https://example.com"})
        self.assertEqual(http_resp.status_code, 403)
        self.assertIn("Security Policy Restriction", http_resp.json()["detail"])


if __name__ == "__main__":
    unittest.main()
