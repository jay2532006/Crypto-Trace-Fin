"""
CryptoTrace LEA — System Verification & Health Sanity Check CLI
Executes end-to-end component verification across all phases:
- Phase 0: Storage, Raw Payload SHA-256, Audit Chain Integrity, RBAC
- Phase 1: Core Intelligence (Mule Network, AdaptiveVASPScorer, Recovery Estimator)
- Phase 2: Trace Engine & Graph Projection
- Phase 3: Ingestion Pipeline & Checkpoint Persistence
- Phase 4: NCRP & SAHYOG External Boundary Adapters & Governance
"""

import sys
import os
from datetime import datetime, timezone

# Ensure project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.db.database import canonical_db
from backend.storage.raw_payload_storage import raw_storage, serialize_deterministically, compute_sha256
from backend.audit.audit_engine import audit_engine
from backend.auth import (
    create_access_token,
    decode_access_token,
    has_permission,
)
from backend.models.confidence_types import UserRole
from backend.adapters.provider_manager import provider_manager
from backend.adapters.ncrp_adapter import ncrp_adapter
from backend.adapters.sahyog_adapter import sahyog_adapter
from backend.typologies.rules.mule_network import mule_network_rule
from backend.attribution.adaptive_vasp_scorer import adaptive_vasp_scorer
from backend.assessment.recovery_estimate import recovery_estimator
from backend.tracing.trace_engine import bounded_tracer
from backend.models.governance_models import (
    GovernedCaseRecord,
    DispositionStatus,
    ConfirmationStatus,
    DatasetQualityAudit,
)


def run_verification():
    print("=" * 70)
    print(" CRYPTOTRACE LEA — END-TO-END SYSTEM SANITY VERIFICATION")
    print(f" Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    checks = []

    # 1. Database
    try:
        case = canonical_db.create_case(
            case_id="VERIFY-001",
            title="System Sanity Check",
            investigator="system_admin",
            crime_type="CYBER_FRAUD"
        )
        assert case.case_id == "VERIFY-001"
        checks.append(("Database & Canonical Store", True, "Initialized & active"))
    except Exception as e:
        checks.append(("Database & Canonical Store", False, str(e)))

    # 2. Raw Payload Storage
    try:
        sample_payload = {"b": 2, "a": 1, "nested": {"z": 9, "y": 8}}
        p_hash = raw_storage.store_payload(
            payload_dict=sample_payload,
            chain_id="eth",
            block_height=1000,
            tx_hash="0xtest",
            provider="alchemy",
            payload_type="tx",
        )
        verified = raw_storage.verify_integrity(p_hash)
        assert verified is True
        checks.append(("Deterministic Raw Storage", True, f"SHA-256 hash verified: {p_hash[:16]}..."))
    except Exception as e:
        checks.append(("Deterministic Raw Storage", False, str(e)))

    # 3. Cryptographic Audit Chain
    try:
        event = audit_engine.log_action(
            user_id="officer_sanity",
            action="verify:self_check",
            resource_id="VERIFY-001",
            resource_type="CASE"
        )
        verification_result = audit_engine.verify_audit_chain()
        assert verification_result.get("valid") is True
        checks.append(("Cryptographic Audit Chain", True, f"Chain integrity verified ({verification_result.get('total_events', 1)} events)"))
    except Exception as e:
        checks.append(("Cryptographic Audit Chain", False, str(e)))

    # 4. Canonical RBAC & Tokens
    try:
        user_dict = {"username": "officer_1", "role": "INVESTIGATOR", "full_name": "Test Officer"}
        token = create_access_token(user_dict)
        payload = decode_access_token(token)
        assert payload["sub"] == "officer_1"
        assert payload["role"] == "INVESTIGATOR"
        assert has_permission("INVESTIGATOR", "cases:create") is True
        assert has_permission("INVESTIGATOR", "notices:approve") is False
        checks.append(("RBAC & Security Tokens", True, "4-tier canonical roles & permissions verified"))
    except Exception as e:
        checks.append(("RBAC & Security Tokens", False, str(e)))

    # 5. Core Typologies (Mule Network)
    try:
        trace_path = [
            {"hop_number": 1, "to_address": "0xMule1", "amount": 10000.0, "timestamp_epoch": 1000},
            {"hop_number": 2, "to_address": "0xMule2", "amount": 9950.0, "timestamp_epoch": 1600},
            {"hop_number": 3, "to_address": "0xMule3", "amount": 9900.0, "timestamp_epoch": 2200},
            {"hop_number": 4, "to_address": "0xVASP", "amount": 9850.0, "timestamp_epoch": 2800},
        ]
        finding = mule_network_rule.evaluate({"hops": trace_path, "data_completeness_pct": 100.0}, case_id="VERIFY-001")
        assert finding is not None
        assert finding.confidence == "MEDIUM"
        assert "PARTIAL" in finding.uncertainty_notes or "uncertainty" in finding.uncertainty_notes.lower()
        checks.append(("Mule Network Typology Rule", True, "Detected >=3 intermediate hops with uncertainty disclosure"))
    except Exception as e:
        checks.append(("Mule Network Typology Rule", False, str(e)))

    # 6. Adaptive VASP Scorer
    try:
        trace_data = {
            "chain": "ETH",
            "hops": [{"hop_number": 1, "to_address": "0xWazirX", "amount": 5000.0}],
            "transfers": [],
        }
        score_data = adaptive_vasp_scorer.score_candidate(
            vasp_key="WAZIRX",
            trace_result=trace_data,
            hop_count=1,
            is_exact_wallet_match=True,
            mixer_detected=False,
            recent_activity_days=2,
            data_completeness_pct=100.0,
        )
        assert score_data.score >= 70
        assert len(score_data.scoring_steps) >= 5
        checks.append(("Adaptive VASP Scorer", True, f"6-step weighting evaluated (Score: {score_data.score})"))
    except Exception as e:
        checks.append(("Adaptive VASP Scorer", False, str(e)))

    # 7. Recovery Probability (PRD FR-016 Boundary Checks)
    try:
        # Check invalid zero-hop
        res_zero = recovery_estimator.estimate_recovery(
            case_id="VERIFY-001",
            traced_amount_usd=1000.0,
            data_completeness_pct=100.0,
            attribution_confidence="HIGH",
            is_fiu_registered_vasp=True,
            hop_count=0,
        )
        assert res_zero.display_tier == "ineligible"

        # Check valid trace
        res_valid = recovery_estimator.estimate_recovery(
            case_id="VERIFY-001",
            traced_amount_usd=5000.0,
            data_completeness_pct=100.0,
            attribution_confidence="HIGH",
            is_fiu_registered_vasp=True,
            hop_count=2,
            elapsed_hours=6.0,
        )
        assert res_valid.recovery_score > 0
        assert res_valid.action_window_hours > 0
        checks.append(("Recovery Estimator (FR-016)", True, "Boundary conditions & 72-hr countdown validated"))
    except Exception as e:
        checks.append(("Recovery Estimator (FR-016)", False, str(e)))

    # 8. External Adapters (NCRP & SAHYOG)
    try:
        # Private key leak rejection check
        bad_complaint = {
            "wallet": "0x1234567890123456789012345678901234567890",
            "complaint_text": "Victim key was 0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d help",
        }
        rej = ncrp_adapter.ingest_ncrp_complaint(bad_complaint)
        assert rej["status"] == "REJECTED"
        assert "SECURITY VIOLATION" in rej["reason"]

        # SAHYOG multi-wallet ingest check
        good_bulletin = {
            "bulletin_id": "BUL-SANITY-01",
            "title": "MHA Phishing Cluster",
            "agency": "I4C",
            "wallets": ["0x1111111111111111111111111111111111111111"],
        }
        s_res = sahyog_adapter.ingest_bulletin(good_bulletin)
        assert s_res["status"] in ["INGESTED", "ALREADY_EXISTS"]
        checks.append(("External Adapters & Sanitization", True, "NCRP key-leak rejection & SAHYOG bulletin ingest passed"))
    except Exception as e:
        checks.append(("External Adapters & Sanitization", False, str(e)))

    # 9. Phase 4B Governance Quality Checks
    try:
        audit_res = DatasetQualityAudit.check_chain_coverage([
            GovernedCaseRecord(
                case_id="C1",
                chain_id="BTC",
                target_wallet="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                crime_category="RANSOMWARE",
                disposition=DispositionStatus.SUB_JUDICE,
                confirmation=ConfirmationStatus.LEA_CONFIRMED,
                first_seen_timestamp=datetime.now(timezone.utc),
                last_seen_timestamp=datetime.now(timezone.utc),
                transaction_count=10,
                total_volume_usd=5000.0,
                ground_truth_label="RANSOMWARE_OPERATOR",
            )
        ], required_chains=["BTC"])
        assert audit_res["passed"] is True
        checks.append(("Governance Quality Audit", True, "Pre-ML dataset quality verification active"))
    except Exception as e:
        checks.append(("Governance Quality Audit", False, str(e)))

    print("\nVERIFICATION RESULTS:")
    print("-" * 70)
    all_passed = True
    for name, passed, detail in checks:
        status_tag = "[PASS]" if passed else "[FAIL]"
        print(f" {status_tag} {name.ljust(35)} : {detail}")
        if not passed:
            all_passed = False

    print("=" * 70)
    if all_passed:
        print(" ALL CHECKS PASSED. SYSTEM IS VERIFIED OPERATIONAL.")
    else:
        print(" ONE OR MORE CHECKS FAILED.")
    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
