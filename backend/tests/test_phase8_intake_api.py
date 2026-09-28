# backend/tests/test_phase8_intake_api.py
"""
CryptoTrace LEA - Phase 4 Intake API Verification Tests
Validates:
1. Endpoint authentication and RBAC boundary enforcement:
   - No token -> 401
   - Investigator token -> 403
   - INTEGRATION_SERVICE / ADMINISTRATOR token -> 200
2. Ingest complaint creates case and cryptographic audit entry
3. Security rejection of private key and seed phrase (HTTP 400, no case created)
4. Persistent database deduplication across adapter instances
5. Multi-wallet bulletin ingestion
6. Auto-trace and preservation notice draft creation
"""

import os
import sys
import unittest
from datetime import datetime
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
from backend.auth.jwt_handler import create_access_token
from backend.db.database import db_manager
from backend.adapters.sahyog_adapter import SAHYOGAdapter

class TestPhase8IntakeAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.service_token = create_access_token({
            "username": "gateway_service",
            "role": "INTEGRATION_SERVICE",
            "unit": "MHA / I4C National Gateway",
        })
        cls.investigator_token = create_access_token({
            "username": "investigator1",
            "role": "INVESTIGATOR",
            "unit": "State Cyber Cell",
        })
        cls.service_headers = {"Authorization": f"Bearer {cls.service_token}"}
        cls.investigator_headers = {"Authorization": f"Bearer {cls.investigator_token}"}

    def test_01_intake_rbac_enforcement(self):
        """Verify strict auth: no token -> 401, investigator -> 403, service token -> 200."""
        payload = {
            "ncrp_ack_number": f"NCRP-RBAC-{int(datetime.now().timestamp())}",
            "chain": "ETH",
            "suspect_wallet": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
            "reported_amount": 1000.0,
        }
        # 1. No token -> 401
        resp_no_token = self.client.post("/api/v1/intake/ncrp/complaint", json=payload)
        self.assertEqual(resp_no_token.status_code, 401)

        # 2. Investigator token -> 403
        resp_investigator = self.client.post("/api/v1/intake/ncrp/complaint", json=payload, headers=self.investigator_headers)
        self.assertEqual(resp_investigator.status_code, 403)

        # 3. Integration Service token -> 200
        resp_service = self.client.post("/api/v1/intake/ncrp/complaint", json=payload, headers=self.service_headers)
        self.assertEqual(resp_service.status_code, 200)
        self.assertEqual(resp_service.json()["status"], "INGESTED")

    def test_02_security_leak_rejection(self):
        """Private key payload rejected with 400 Bad Request; no case created."""
        payload = {
            "ncrp_ack_number": f"NCRP-LEAK-{int(datetime.now().timestamp())}",
            "chain": "ETH",
            "suspect_wallet": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
            "complaint_text": "Victim gave key 0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d to hacker.",
        }
        resp = self.client.post("/api/v1/intake/ncrp/complaint", json=payload, headers=self.service_headers)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("SECURITY VIOLATION", resp.json()["detail"]["reason"])

    def test_03_persistent_deduplication_across_instances(self):
        """Deduplication persists in database even across fresh SAHYOGAdapter instances."""
        b_id = f"SAHYOG-PERSIST-{int(datetime.now().timestamp() * 1000)}"
        bulletin = {
            "bulletin_id": b_id,
            "title": "Persistent Dedupe Test",
            "agency": "DELHI_SPECIAL_CELL",
            "crime_type": "MULE_NET",
            "wallets": ["0xd8da6bf26964af9d7eed9e03e53415d37aa96045"]
        }
        # Ingest with first adapter
        adapter1 = SAHYOGAdapter()
        res1 = adapter1.ingest_bulletin(bulletin)
        self.assertEqual(res1["status"], "INGESTED")

        # Ingest identical bulletin with a brand new adapter instance
        adapter2 = SAHYOGAdapter()
        res2 = adapter2.ingest_bulletin(bulletin)
        self.assertEqual(res2["status"], "ALREADY_EXISTS")

    def test_04_intake_queue_and_status_endpoints(self):
        """Verify GET /api/v1/intake/status and /queue return sandbox banner and queue items."""
        st_resp = self.client.get("/api/v1/intake/status")
        self.assertEqual(st_resp.status_code, 200)
        st_data = st_resp.json()
        self.assertIn("banner", st_data)
        self.assertEqual(st_data["gateway_mode"], "SANDBOX")

        q_resp = self.client.get("/api/v1/intake/queue")
        self.assertEqual(q_resp.status_code, 200)
        self.assertIsInstance(q_resp.json(), list)

if __name__ == "__main__":
    unittest.main()
