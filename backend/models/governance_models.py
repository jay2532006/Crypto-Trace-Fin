"""
CryptoTrace LEA — Phase 4B Evidence & Outcome Governance Models and Dataset Quality Checks
Provides durable schemas and rigorous data governance rules for court-confirmed case ground truth,
legal outcomes, and research dataset auditing (pre-ML quality gate).
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class DispositionStatus(str, Enum):
    """Case legal disposition classification."""
    SUB_JUDICE = "SUB_JUDICE"
    CHARGESHEETED = "CHARGESHEETED"
    CONVICTED = "CONVICTED"
    ACQUITTED = "ACQUITTED"
    RECOVERED = "RECOVERED"
    UNRESOLVED = "UNRESOLVED"
    CLOSED_UNSUBSTANTIATED = "CLOSED_UNSUBSTANTIATED"


class ConfirmationStatus(str, Enum):
    """Authority confirmation level for investigative ground truth."""
    UNCONFIRMED = "UNCONFIRMED"
    LEA_CONFIRMED = "LEA_CONFIRMED"
    PROSECUTION_CONFIRMED = "PROSECUTION_CONFIRMED"
    JUDICIAL_CONFIRMED = "JUDICIAL_CONFIRMED"


class LabelingAuthority(BaseModel):
    """Official LEA / judicial authority certifying the ground truth."""
    authority_id: str
    agency_name: str
    jurisdiction: str
    reviewer_designation: str
    officer_badge_id: str
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OutcomeEvidence(BaseModel):
    """Durable court-admissible outcome evidence."""
    evidence_id: str
    case_id: str
    disposition: DispositionStatus
    confirmation_level: ConfirmationStatus
    court_name: Optional[str] = None
    court_order_ref: Optional[str] = None
    fir_number: Optional[str] = None
    recovery_amount_inr: float = 0.0
    seizure_memo_hash: Optional[str] = None
    frozen_tx_hashes: List[str] = Field(default_factory=list)
    labeling_authority: LabelingAuthority
    notes: Optional[str] = None
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GovernedCaseRecord(BaseModel):
    """Governed case record ready for auditing and empirical training datasets."""
    case_id: str
    chain_id: str
    target_wallet: str
    crime_category: str
    disposition: DispositionStatus
    confirmation: ConfirmationStatus
    first_seen_timestamp: datetime
    last_seen_timestamp: datetime
    transaction_count: int
    total_volume_usd: float
    ground_truth_label: str  # e.g., "MULE_NETWORK", "MIXER_DEPOSIT", "BENIGN_TRANSFER"
    features: Dict[str, Any] = Field(default_factory=dict)
    outcome_evidence: Optional[OutcomeEvidence] = None


# =====================================================================
# Pre-ML Dataset Quality Check Routines (Section 13)
# =====================================================================

class DatasetQualityAudit:
    """
    Validates empirical training and research datasets before any ML exploration.
    Detects duplicate cases, missing labels, class imbalance, temporal coverage gaps,
    chain coverage gaps, feature leakage, and label leakage.
    """

    @staticmethod
    def check_duplicate_cases(records: List[GovernedCaseRecord]) -> Dict[str, Any]:
        """Flags identical or overlapping cases by ID or target wallet."""
        seen_ids: Set[str] = set()
        seen_wallets: Set[str] = set()
        duplicate_ids = []
        duplicate_wallets = []

        for r in records:
            if r.case_id in seen_ids:
                duplicate_ids.append(r.case_id)
            else:
                seen_ids.add(r.case_id)

            wallet_key = f"{r.chain_id}:{r.target_wallet.lower()}"
            if wallet_key in seen_wallets:
                duplicate_wallets.append(wallet_key)
            else:
                seen_wallets.add(wallet_key)

        return {
            "check": "DUPLICATE_CASES",
            "passed": len(duplicate_ids) == 0 and len(duplicate_wallets) == 0,
            "duplicate_case_ids": list(set(duplicate_ids)),
            "duplicate_wallets": list(set(duplicate_wallets)),
            "total_records": len(records),
        }

    @staticmethod
    def check_missing_labels(records: List[GovernedCaseRecord]) -> Dict[str, Any]:
        """Detects records lacking verified ground truth labels or unconfirmed status."""
        missing = []
        for r in records:
            if not r.ground_truth_label or r.ground_truth_label.strip() == "" or r.confirmation == ConfirmationStatus.UNCONFIRMED:
                missing.append(r.case_id)

        return {
            "check": "MISSING_OR_UNCONFIRMED_LABELS",
            "passed": len(missing) == 0,
            "unlabeled_or_unconfirmed_cases": missing,
            "missing_ratio": len(missing) / len(records) if records else 0.0,
        }

    @staticmethod
    def check_class_imbalance(records: List[GovernedCaseRecord], max_skew_ratio: float = 10.0) -> Dict[str, Any]:
        """Measures class distribution skew across ground truth labels."""
        if not records:
            return {"check": "CLASS_IMBALANCE", "passed": False, "error": "No records present"}

        counts: Dict[str, int] = {}
        for r in records:
            counts[r.ground_truth_label] = counts.get(r.ground_truth_label, 0) + 1

        min_c = min(counts.values()) if counts else 0
        max_c = max(counts.values()) if counts else 0
        skew = (max_c / min_c) if min_c > 0 else float("inf")

        return {
            "check": "CLASS_IMBALANCE",
            "passed": skew <= max_skew_ratio,
            "class_counts": counts,
            "skew_ratio": round(skew, 2),
            "max_skew_allowed": max_skew_ratio,
        }

    @staticmethod
    def check_temporal_coverage(records: List[GovernedCaseRecord], min_span_days: int = 30) -> Dict[str, Any]:
        """Ensures training samples span a sufficient chronological window to avoid regime overfitting."""
        if not records:
            return {"check": "TEMPORAL_COVERAGE", "passed": False, "error": "No records present"}

        all_dates = [r.first_seen_timestamp for r in records] + [r.last_seen_timestamp for r in records]
        earliest = min(all_dates)
        latest = max(all_dates)
        span_days = (latest - earliest).days

        return {
            "check": "TEMPORAL_COVERAGE",
            "passed": span_days >= min_span_days,
            "earliest_date": earliest.isoformat(),
            "latest_date": latest.isoformat(),
            "span_days": span_days,
            "required_span_days": min_span_days,
        }

    @staticmethod
    def check_chain_coverage(records: List[GovernedCaseRecord], required_chains: Optional[List[str]] = None) -> Dict[str, Any]:
        """Checks multi-chain representation across indexed cases."""
        if required_chains is None:
            required_chains = ["BTC", "ETH", "TRON"]

        present_chains = {r.chain_id.upper() for r in records}
        missing_chains = [c for c in required_chains if c not in present_chains]

        return {
            "check": "CHAIN_COVERAGE",
            "passed": len(missing_chains) == 0,
            "present_chains": list(present_chains),
            "missing_chains": missing_chains,
        }

    @staticmethod
    def check_feature_and_label_leakage(records: List[GovernedCaseRecord]) -> Dict[str, Any]:
        """
        Detects feature leakage (e.g., using future disposition or post-incident recovery metadata as input features).
        """
        leakage_violations = []
        forbidden_substrings = ["recovery", "court", "disposition", "convicted", "outcome", "seizure"]

        for r in records:
            for feat_key in r.features.keys():
                if any(sub in feat_key.lower() for sub in forbidden_substrings):
                    leakage_violations.append({
                        "case_id": r.case_id,
                        "leaked_feature": feat_key,
                    })

        return {
            "check": "FEATURE_LABEL_LEAKAGE",
            "passed": len(leakage_violations) == 0,
            "violations_found": len(leakage_violations),
            "violations": leakage_violations[:10],
        }

    @classmethod
    def run_full_dataset_audit(cls, records: List[GovernedCaseRecord]) -> Dict[str, Any]:
        """Runs the complete suite of quality checks and determines dataset readiness."""
        checks = [
            cls.check_duplicate_cases(records),
            cls.check_missing_labels(records),
            cls.check_class_imbalance(records),
            cls.check_temporal_coverage(records),
            cls.check_chain_coverage(records),
            cls.check_feature_and_label_leakage(records),
        ]

        all_passed = all(c.get("passed", False) for c in checks)
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "DATASET_QUALIFIED" if all_passed else "QUALITY_GATES_FAILED",
            "all_passed": all_passed,
            "total_records": len(records),
            "checks": checks,
        }
