"""
Test Suite for CryptoTrace LEA Phase 4A (External Boundaries) and Phase 4B (Governance)
"""

import pytest
from datetime import datetime, timezone, timedelta

from backend.adapters.ncrp_adapter import NCRPAdapter
from backend.adapters.sahyog_adapter import SAHYOGAdapter
from backend.models.governance_models import (
    GovernedCaseRecord,
    DispositionStatus,
    ConfirmationStatus,
    LabelingAuthority,
    OutcomeEvidence,
    DatasetQualityAudit,
)


def test_ncrp_private_key_rejection():
    adapter = NCRPAdapter()
    complaint = {
        "suspect_wallet": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
        "complaint_text": "Victim stated suspect sent key 0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d to access wallet.",
        "reported_amount": 50000,
    }
    result = adapter.ingest_ncrp_complaint(complaint)
    assert result["status"] == "REJECTED"
    assert "SECURITY VIOLATION" in result["reason"]
    assert "private key" in result["reason"].lower()


def test_ncrp_seed_phrase_rejection():
    adapter = NCRPAdapter()
    mnemonic_narrative = (
        "Complainant was instructed to write down words: "
        "abandon ability able about above absent absorb abstract absurd abuse access accident"
    )
    complaint = {
        "suspect_wallet": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
        "complaint_text": mnemonic_narrative,
        "reported_amount": 10000,
    }
    result = adapter.ingest_ncrp_complaint(complaint)
    assert result["status"] == "REJECTED"
    assert "SECURITY VIOLATION" in result["reason"]
    assert "seed phrase" in result["reason"].lower()


def test_ncrp_valid_ingest_and_unauthorized_boundary():
    adapter = NCRPAdapter()
    # Boundary check: unconfigured credentials report UNAVAILABLE_UNAUTHORIZED
    assert adapter.is_operational() is False
    status = adapter.get_connection_status()
    assert status["status"] == "UNAVAILABLE_UNAUTHORIZED"

    # Valid complaint ingest
    unique_ack = f"NCRP-TEST-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    complaint = {
        "suspect_wallet": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
        "complaint_text": "Fraudulent crypto investment scheme on Telegram.",
        "reported_amount": 75000,
        "ncrp_ack_number": unique_ack,
        "complainant_name": "Rajesh Sharma",
    }
    result = adapter.ingest_ncrp_complaint(complaint)
    assert result["status"] == "INGESTED"
    assert result["case_id"] == unique_ack


def test_sahyog_bulletin_ingest_and_multi_wallet_extraction():
    adapter = SAHYOGAdapter()
    assert adapter.is_operational() is False
    status = adapter.get_connection_status()
    assert status["status"] == "UNAVAILABLE_UNAUTHORIZED"

    unique_bul_id = f"SAHYOG-MHA-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    bulletin = {
        "bulletin_id": unique_bul_id,
        "title": "Cross-Border Cyber Syndicate",
        "agency": "I4C_DELHI",
        "description": "Suspects utilized multiple addresses across EVM and Bitcoin networks.",
        "wallets": [
            "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
            "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        ],
        "crime_type": "INVESTMENT_SCAM",
    }
    res = adapter.ingest_bulletin(bulletin)
    assert res["status"] == "INGESTED"
    assert res["wallets_linked"] == 2
    assert res["case_id"] == unique_bul_id

    # Deduplication test
    dup_res = adapter.ingest_bulletin(bulletin)
    assert dup_res["status"] == "ALREADY_EXISTS"


def test_sahyog_private_key_rejection():
    adapter = SAHYOGAdapter()
    bulletin = {
        "bulletin_id": "SAHYOG-BAD-KEY",
        "title": "Leaked Key Bulletin",
        "agency": "STATE_CYBER",
        "description": "Private key 0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d was recovered",
        "wallets": ["0x71C7656EC7ab88b098defB751B7401B5f6d8976F"],
    }
    res = adapter.ingest_bulletin(bulletin)
    assert res["status"] == "REJECTED"
    assert "SECURITY VIOLATION" in res["reason"]


def test_dataset_quality_audit_checks():
    now = datetime.now(timezone.utc)
    earlier = now - timedelta(days=45)

    valid_records = [
        GovernedCaseRecord(
            case_id="CASE-1",
            chain_id="ETH",
            target_wallet="0x1111111111111111111111111111111111111111",
            crime_category="PHISHING",
            disposition=DispositionStatus.CHARGESHEETED,
            confirmation=ConfirmationStatus.LEA_CONFIRMED,
            first_seen_timestamp=earlier,
            last_seen_timestamp=now,
            transaction_count=25,
            total_volume_usd=12000.0,
            ground_truth_label="MULE_NETWORK",
            features={"hop_count": 4, "velocity_minutes": 15},
        ),
        GovernedCaseRecord(
            case_id="CASE-2",
            chain_id="BTC",
            target_wallet="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            crime_category="RANSOMWARE",
            disposition=DispositionStatus.CONVICTED,
            confirmation=ConfirmationStatus.JUDICIAL_CONFIRMED,
            first_seen_timestamp=earlier,
            last_seen_timestamp=now,
            transaction_count=10,
            total_volume_usd=85000.0,
            ground_truth_label="RANSOMWARE_OPERATOR",
            features={"hop_count": 2, "velocity_minutes": 120},
        ),
        GovernedCaseRecord(
            case_id="CASE-3",
            chain_id="TRON",
            target_wallet="TLyqzVGLV1srkB7dToTAwdg29TFVKbh58A",
            crime_category="USDT_LAUNDERING",
            disposition=DispositionStatus.SUB_JUDICE,
            confirmation=ConfirmationStatus.PROSECUTION_CONFIRMED,
            first_seen_timestamp=earlier,
            last_seen_timestamp=now,
            transaction_count=50,
            total_volume_usd=40000.0,
            ground_truth_label="MIXER_DEPOSIT",
            features={"hop_count": 5, "velocity_minutes": 8},
        ),
    ]

    # Test complete audit on valid records
    full_audit = DatasetQualityAudit.run_full_dataset_audit(valid_records)
    assert full_audit["overall_status"] == "DATASET_QUALIFIED"
    assert full_audit["all_passed"] is True

    # Test duplicate detection
    dup_records = valid_records + [valid_records[0]]
    dup_res = DatasetQualityAudit.check_duplicate_cases(dup_records)
    assert dup_res["passed"] is False
    assert "CASE-1" in dup_res["duplicate_case_ids"]

    # Test feature leakage detection
    leaked_record = GovernedCaseRecord(
        case_id="CASE-LEAK",
        chain_id="ETH",
        target_wallet="0x2222222222222222222222222222222222222222",
        crime_category="FRAUD",
        disposition=DispositionStatus.RECOVERED,
        confirmation=ConfirmationStatus.LEA_CONFIRMED,
        first_seen_timestamp=earlier,
        last_seen_timestamp=now,
        transaction_count=5,
        total_volume_usd=1000.0,
        ground_truth_label="BENIGN",
        features={"court_conviction_recorded": True},  # LEAK!
    )
    leak_res = DatasetQualityAudit.check_feature_and_label_leakage([leaked_record])
    assert leak_res["passed"] is False
    assert leak_res["violations_found"] == 1
