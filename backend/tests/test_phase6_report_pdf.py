# backend/tests/test_phase6_report_pdf.py
"""
CryptoTrace LEA - Phase 6 Standardized PDF Report Generation Tests
Validates:
1. ReportLab PDF generation with complete forensic sections
2. Idempotent bit-for-bit determinism (identical SHA-256 for identical inputs)
3. Endpoint accessibility and PDF MIME-type headers
"""

import os
import sys
import hashlib
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.legal.report_generator import forensic_report_generator
from backend.fixtures.demo_cases_v2 import CRYPTO_TRACE_FIXTURES
from backend.tracing.trace_engine import bounded_tracer, TraceConstraints
from fastapi.testclient import TestClient
from app import app
from backend.auth.jwt_handler import create_access_token


class TestPhase6ReportPDF(unittest.TestCase):
    def setUp(self):
        self.case = CRYPTO_TRACE_FIXTURES[0]
        self.trace = bounded_tracer.trace(
            start_address=self.case["suspect_wallet"],
            chain=self.case["chain"],
            constraints=TraceConstraints(max_hops=4),
            case_id=self.case["case_id"],
            mode="DEMO"
        )

    def test_01_pdf_generation_content(self):
        pdf_bytes = forensic_report_generator.generate_report_pdf(
            case=self.case,
            trace=self.trace,
            audit_head_hash="0afe893cac1c7162c3cc7ec38a573aa11e0fc593eaa3227012336b86aaea9d03",
            deterministic=True
        )
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 15000)

    def test_02_pdf_determinism(self):
        pdf1 = forensic_report_generator.generate_report_pdf(
            case=self.case,
            trace=self.trace,
            audit_head_hash="0afe893cac1c7162c3cc7ec38a573aa11e0fc593eaa3227012336b86aaea9d03",
            deterministic=True
        )
        pdf2 = forensic_report_generator.generate_report_pdf(
            case=self.case,
            trace=self.trace,
            audit_head_hash="0afe893cac1c7162c3cc7ec38a573aa11e0fc593eaa3227012336b86aaea9d03",
            deterministic=True
        )
        h1 = hashlib.sha256(pdf1).hexdigest()
        h2 = hashlib.sha256(pdf2).hexdigest()
        self.assertEqual(h1, h2, "PDF generation must be bit-for-bit deterministic!")

    def test_03_report_api_endpoint(self):
        client = TestClient(app)
        token = create_access_token({"username": "investigator1", "role": "investigator"})
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/api/v1/cases/CR-2026-MULE-IND-01/report.pdf", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "application/pdf")
        self.assertTrue(resp.content.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
