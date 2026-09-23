"""
CryptoTrace LEA — Legal Notice & Preservation Request Generator
Operates strictly as a draft-only, human-supervised preservation workflow:
DRAFT -> PENDING_APPROVAL -> APPROVED / REJECTED by Supervisor -> EXPORT

Legal Basis: Section 91 Bharatiya Nagarik Suraksha Sanhita (BNSS 2023) / Section 91 CrPC.
CryptoTrace NEVER automatically transmits or files notices.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from backend.models.domain_models import PreservationRequestDraft
from backend.models.confidence_types import NoticeStatus
from backend.audit.audit_engine import audit_engine
from backend.db.database import db_manager


class LegalNoticeGenerator:
    def create_draft(
        self,
        case_id: str,
        trace_data: Dict[str, Any],
        investigating_officer: str = "Inspector R. Sharma",
        unit: str = "Cyber Crime Police Station",
        state: str = "Maharashtra",
        fir_number: str = "FIR-CR-2026/89",
        complainant: str = "S. Verma",
    ) -> PreservationRequestDraft:
        """Generates a formal legal preservation draft in DRAFT status."""
        draft_id = f"DRAFT-BNSS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        attribution = trace_data.get("attribution", {})
        vasp_name = attribution.get("vasp_name", "Designated Virtual Asset Service Provider")
        nodal_email = attribution.get("nodal_officer_email", "nodal@exchange.com")
        suspect_wallet = trace_data.get("suspect_address", "")
        chain = trace_data.get("chain", "TRON")
        hops = trace_data.get("hops", [])

        # Format transaction references
        tx_refs = [
            {"hop": h.get("hop_number"), "tx_hash": h.get("tx_hash"), "amount": h.get("amount"), "asset": h.get("asset")}
            for h in hops
        ]

        tx_bullets = "\n".join(
            f"  - Hop {h.get('hop_number')}: {h.get('amount')} {h.get('asset')} | TXID: {h.get('tx_hash')} -> Dest: {h.get('to_address')}"
            for h in hops
        )

        draft_text = f"""
LEGAL REQUISITION NOTICE UNDER SECTION 91 BHARATIYA NAGARIK SURAKSHA SANHITA (BNSS 2023)
[FORMERLY SECTION 91 CODE OF CRIMINAL PROCEDURE (CrPC 1973)]
FOR PRODUCTION OF ELECTRONIC EVIDENCE & IMMEDIATE EMERGENCY FUND FREEZING

DATE OF REQUISITION: {datetime.now().strftime('%d %B %Y')}
DISPATCH STATUS: [DRAFT — STRICTLY PENDING SUPERVISORY AUTHORIZATION]
CASE / FIR REFERENCE: {fir_number}
POLICE STATION / LEA UNIT: {unit}, State of {state}
INVESTIGATING OFFICER: {investigating_officer}

TO:
The Nodal Officer / Compliance Department,
{vasp_name}
Email: {nodal_email}

SUBJECT: NOTICE FOR PRODUCTION OF RECORDS, KYC DISCLOSURE & URGENT PRESERVATION OF ILLICIT PROCEEDS OF CRIME

1. WHEREAS, a formal cybercrime complaint ({case_id}) has been lodged by {complainant} regarding unauthorized fraudulent siphoning and diversion of funds;

2. AND WHEREAS, cryptographic forensic on-chain tracing conducted by this agency on the {chain} blockchain has traced the illicit proceeds of crime traversing through intermediary mule accounts into a deposit/hot-wallet cluster controlled by your exchange:
{tx_bullets}

3. NOW THEREFORE, by virtue of the powers vested in me under Section 91 of the Bharatiya Nagarik Suraksha Sanhita (BNSS 2023), you are hereby legally required to:
   (a) IMMEDIATELY PRESERVE and FREEZE the designated recipient account(s) / wallet(s) pending judicial orders;
   (b) DISCLOSE complete Know-Your-Customer (KYC) records of the account holder (Aadhaar, PAN, Passport, Driving License);
   (c) FURNISH login IP access logs, device fingerprints, and timestamps for the relevant transaction period;
   (d) PROVIDE linked fiat bank account details, beneficiary names, and IFSC codes utilized for withdrawals.

4. TAKE NOTE that under Section 67C of the Information Technology Act 2000, you are mandated to preserve all traffic data and subscriber records. Non-compliance attracts statutory penal liability under the Bharatiya Nyaya Sanhita (BNS 2023).

ISSUED BY:
{investigating_officer}
{unit}
State Police Administration
"""

        draft = PreservationRequestDraft(
            draft_id=draft_id,
            case_id=case_id,
            trace_id=trace_data.get("trace_id"),
            created_by=investigating_officer,
            recipient_vasp=vasp_name,
            recipient_email=nodal_email,
            legal_authority="SECTION_91_BNSS_2023",
            transaction_references=tx_refs,
            draft_text=draft_text.strip(),
            status="DRAFT",
        )

        # Log audit trail
        audit_engine.log_action(
            user_id=investigating_officer,
            action="notice:draft",
            resource_id=draft_id,
            resource_type="LEGAL_NOTICE",
            details={"case_id": case_id, "vasp": vasp_name, "status": "DRAFT"},
        )

        return draft


notice_generator = LegalNoticeGenerator()
