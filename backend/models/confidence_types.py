"""
CryptoTrace LEA — Confidence, Typology & Label Types
Strict enumeration of domain certainty bounds and operational states.
"""

from typing import Literal

# Evidence & Attribution Confidence
ConfidenceLevel = Literal["LOW", "MEDIUM", "HIGH"]
LabelType = Literal["VERIFIED", "INFERRED", "UNRESOLVED"]
LinkType = Literal["PROVEN", "HEURISTIC_CORRELATION"]
RiskCategory = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]

# Blockchain Canonical Event Types
EventType = Literal["NATIVE", "ERC20", "TRC20", "INTERNAL", "BRIDGE"]
FinalityState = Literal["PENDING", "CONFIRMED", "FINALIZED", "REORGANIZED"]

# Governance & Workflow
CaseSource = Literal["COMPLAINT", "NCRP_BULLETIN", "SAHYOG", "DEMO_CASE_SIH26183"]
NoticeStatus = Literal["DRAFT", "PENDING_APPROVAL", "APPROVED", "REJECTED"]
UserRole = Literal["INVESTIGATOR", "SUPERVISOR", "ADMINISTRATOR", "INTEGRATION_SERVICE"]

# Recovery Eligibility
DisplayTier = Literal["eligible", "ineligible"]
