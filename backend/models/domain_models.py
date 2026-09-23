"""
CryptoTrace LEA — Canonical Domain Models
Defines Pydantic data models for the 12 core entities, evidence manifests, and audit events.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from .confidence_types import (
    ConfidenceLevel,
    LabelType,
    LinkType,
    RiskCategory,
    EventType,
    FinalityState,
    CaseSource,
    NoticeStatus,
    UserRole,
    DisplayTier,
)


class Case(BaseModel):
    case_id: str
    source: CaseSource = "COMPLAINT"
    chain: str
    wallet: str
    reported_amount: Optional[float] = None
    complaint_text: Optional[str] = None
    complainant_name: Optional[str] = None
    fir_number: Optional[str] = None
    created_by: str = "investigator1"
    assigned_to: Optional[str] = "investigator1"
    status: str = "OPEN"
    created_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    demo_data: bool = False
    source_origin: str = "LIVE_LEA_INTAKE"


class Transaction(BaseModel):
    chain_id: str
    tx_hash: str
    block_number: int
    timestamp: str
    status: str = "SUCCESS"
    raw_payload_hash: str


class Transfer(BaseModel):
    chain_id: str
    tx_hash: str
    log_index: int = 0
    transfer_index: int = 0
    event_type: EventType = "NATIVE"
    from_addr: str
    to_addr: str
    amount: float
    asset: str
    direction: str = "OUT"
    raw_payload_hash: str
    finality_state: FinalityState = "CONFIRMED"
    timestamp: Optional[str] = None
    provider_source: str = "RPC_PRIMARY"

    @property
    def canonical_identity(self) -> str:
        return f"{self.chain_id}:{self.tx_hash}:{self.event_type}:{self.log_index}:{self.transfer_index}"


class EntityLabel(BaseModel):
    entity_id: str
    address: str
    chain: str
    label: str
    source: str
    confidence_level: ConfidenceLevel
    label_type: LabelType
    verified_date: Optional[str] = None


class VASPCluster(BaseModel):
    cluster_id: str
    vasp_name: str
    regions: List[str] = []
    hot_wallet_patterns: List[Dict[str, Any]] = []
    known_deposits: List[str] = []
    nodal_officer_email: str
    fiu_registration_status: str = "REGISTERED"
    policy_version: str = "policy_v1_india_kyc"


class PatternFinding(BaseModel):
    finding_id: str
    case_id: str
    typology_name: str
    rule_version: str = "1.0"
    confidence: ConfidenceLevel
    evidence_json: Dict[str, Any]
    uncertainty_notes: str
    data_completeness_pct: float = 100.0
    india_specific: bool = False


class CrossChainLink(BaseModel):
    from_chain: str
    from_addr: str
    to_chain: str
    to_addr: str
    link_type: LinkType
    supporting_evidence: Dict[str, Any]
    confidence: ConfidenceLevel


class RiskAssessment(BaseModel):
    case_id: str
    risk_score: int  # 0 to 100
    risk_category: RiskCategory
    component_scores: Dict[str, Any]


class RecoveryAssessment(BaseModel):
    case_id: str
    recovery_score: int  # 0 to 100
    action_window_hours: int
    display_tier: DisplayTier
    calculation_basis: str
    disclaimer: str = (
        "Heuristic Recovery Estimate is an operational urgency indicator based on path complexity, "
        "elapsed time, and exchange cooperation. It is not a statistical probability or legal guarantee."
    )


class EvidenceManifest(BaseModel):
    manifest_id: str
    case_id: str
    event_id: str
    payload_hash: str
    provider_source: str
    serialization_version: str = "v1-deterministic"
    verified_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class AuditEvent(BaseModel):
    event_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    user_id: str
    action: str
    resource_id: str
    resource_type: str
    result: str = "SUCCESS"
    details_json: Dict[str, Any] = {}
    previous_event_hash: str = ""
    event_hash: str = ""


class PreservationRequestDraft(BaseModel):
    draft_id: str
    case_id: str
    trace_id: Optional[int] = None
    created_by: str
    created_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    recipient_vasp: str
    recipient_email: str
    legal_authority: str = "SECTION_91_BNSS_2023"
    demanded_items: List[str] = [
        "Immediate freezing of designated recipient deposit wallet/account",
        "KYC document disclosure (Aadhaar, PAN, Passport, Driving License)",
        "Login IP access logs and device fingerprints",
        "Linked fiat beneficiary bank accounts",
    ]
    transaction_references: List[Dict[str, Any]] = []
    draft_text: str
    status: NoticeStatus = "DRAFT"
    supervisor_id: Optional[str] = None
    supervisor_notes: Optional[str] = None
