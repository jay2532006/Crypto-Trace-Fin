from backend.adapters.bip39_validator import detect_private_key, detect_mnemonic
"""
CryptoTrace LEA — Phase 4A NCRP Boundary Adapter
Implements the National Cybercrime Reporting Portal (NCRP) boundary contract:
- Complaint payload validation
- Address and blockchain network detection
- PRIVATE-KEY & MNEMONIC REJECTION (Mandatory security safeguard)
- Idempotent case creation
- External provenance tagging
- Real-world connectivity boundary: Reports UNAVAILABLE_UNAUTHORIZED if external credentials are not configured (Never fakes a live government connection).
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.db.database import canonical_db
from backend.audit.audit_engine import audit_engine
from backend.adapters.provider_manager import provider_manager


# BIP-39 common word snippet regex for private key/mnemonic leakage detection
MNEMONIC_PATTERN = re.compile(
    r"\b(?:abandon|ability|able|about|above|absent|absorb|abstract|absurd|abuse|access|accident|account|accuse|achieve|acid|acoustic|acquire|across|act|action|actor|actress|actual|adapt|add|addict|address|adjust|admit|adult|advance|advice|aerobic|affair|afford|afraid|again|age|agent|agree|ahead|aim|air|airport|aisle|alarm|album|alcohol|alert|alien|all|alley|allow|almost|alone|alpha|already|also|alter|always|amateur|amazing|among|amount|amused|analyst|anchor|ancient|anger|angle|angry|animal|ankle|announce|annual|another|answer|antenna|antique|anxiety|any|apart|apology|appear|apple|approve|april|arch|arctic|area|arena|argue|arm|armed|armor|army|around|arrange|arrest|arrive|arrow|art|artefact|artist|artwork|ask|aspect|assault|asset|assist|assume|asthma|athlete|atom|attack|attend|attitude|attract|auction|audit|august|aunt|author|auto|autumn|average|avocado|avoid|awake|award|aware|away|awesome|awful|awkward|axis|baby|bachelor|bacon|badge|bag|balance|balcony|ball|bamboo|banana|banner|bar|barely|bargain|barrel|base|basic|basket|battle|beach|bean|beauty|because|become|beef|before|begin|behave|behind|believe|below|belt|bench|benefit|best|betray|better|between|beyond|bicycle|bid|bike|bind|biology|bird|birth|bitter|black|blade|blame|blanket|blast|bleak|bless|blind|blood|blossom|blow|blue|blur|blush|board|boat|body|boil|bomb|bone|bonus|book|boost|border|boring|borrow|boss|bottom|bounce|box|boy|bracket|brain|brand|brass|brave|bread|breeze|brick|bridge|brief|bright|bring|brisk|broccoli|broken|bronze|broom|brother|brown|brush|bubble|buddy|budget|buffalo|build|bulb|bulk|bullet|bundle|bunker|burden|burger|burst|bus|business|busy|butter|buyer|buzz)\b",
    re.IGNORECASE,
)
HEX_PRIVATE_KEY_PATTERN = re.compile(r"\b(?:0x)?[a-fA-F0-9]{64}\b")


class NCRPAdapter:
    def __init__(self, api_url: Optional[str] = None, auth_token: Optional[str] = None):
        self.api_url = api_url
        self.auth_token = auth_token

    def is_operational(self) -> bool:
        """NCRP live gateway requires explicit authorized endpoint and token."""
        return bool(self.api_url and self.auth_token)

    def get_connection_status(self) -> Dict[str, Any]:
        """Returns connection status per PRD Rule 1 (never fake live status)."""
        if not self.is_operational():
            return {
                "status": "UNAVAILABLE_UNAUTHORIZED",
                "operational": False,
                "message": "NCRP national cybercrime portal gateway credentials are not configured in environment.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        return {
            "status": "CONNECTED_AUTHORIZED",
            "operational": True,
            "endpoint": self.api_url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def validate_and_sanitize_complaint(self, complaint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates complaint fields and ensures no private keys or mnemonics are present.
        """
        raw_text = " ".join([
            str(complaint.get("complaint_text", "")),
            str(complaint.get("narrative", "")),
            str(complaint.get("additional_notes", ""))
        ])

        # 1. Private Key / Seed Phrase Detection & Rejection
        if detect_private_key(raw_text):
            return {
                "valid": False,
                "error": "SECURITY VIOLATION: Potential 64-character private key detected in complaint narrative. Rejected for security compliance.",
            }

        if detect_mnemonic(raw_text, threshold=12):
            return {
                "valid": False,
                "error": "SECURITY VIOLATION: Potential 12/24-word seed phrase / mnemonic detected in complaint narrative. Rejected to protect victim credentials.",
            }

        # 2. Wallet & Chain Validation
        wallet = (complaint.get("suspect_wallet") or complaint.get("wallet") or "").strip()
        if not wallet:
            return {"valid": False, "error": "Suspect wallet address is missing."}

        chain = complaint.get("chain") or provider_manager.detect_chain(wallet)
        if not chain:
            return {
                "valid": False,
                "error": f"Cannot determine supported blockchain for wallet '{wallet}'.",
            }

        return {
            "valid": True,
            "wallet": wallet,
            "chain": chain.upper(),
            "amount": float(complaint.get("reported_amount") or 0.0),
            "ncrp_ack_number": complaint.get("ncrp_ack_number") or complaint.get("acknowledgement_no"),
            "complainant_name": complaint.get("complainant_name", "Anonymous"),
            "complaint_text": complaint.get("complaint_text", ""),
            "fir_number": complaint.get("fir_number"),
        }

    def ingest_ncrp_complaint(self, complaint: Dict[str, Any], actor: str = "ncrp_gateway") -> Dict[str, Any]:
        """
        Idempotently ingest an NCRP cybercrime complaint into canonical cases.
        """
        val = self.validate_and_sanitize_complaint(complaint)
        if not val["valid"]:
            audit_engine.log_action(
                user_id=actor,
                action="ncrp:ingest_rejected",
                resource_id=complaint.get("ncrp_ack_number", "UNKNOWN"),
                resource_type="CASE",
                details={"reason": val["error"]},
            )
            return {"status": "REJECTED", "reason": val["error"]}

        ack = val["ncrp_ack_number"]
        if ack:
            case_id = ack if ack.startswith("NCRP-") else f"NCRP-{ack}"
        else:
            case_id = f"NCRP-{val['wallet'][-8:].upper()}"

        # Idempotency check: Don't duplicate if already ingested
        existing = canonical_db.get_case(case_id)
        if existing:
            return {
                "status": "EXISTING",
                "case_id": case_id,
                "message": "NCRP complaint previously ingested and indexed.",
            }

        # Create canonical Case
        case_dict = {
            "case_id": case_id,
            "source": "NCRP",
            "chain": val["chain"],
            "wallet": val["wallet"],
            "reported_amount": val["amount"],
            "complaint_text": val["complaint_text"],
            "complainant_name": val["complainant_name"],
            "fir_number": val["fir_number"],
            "created_by": actor,
            "assigned_to": "investigator1",
            "status": "OPEN",
            "created_date": datetime.now(timezone.utc).isoformat(),
            "demo_data": False,
            "source_origin": "NCRP_PORTAL",
        }
        canonical_db.create_case(case_dict)

        audit_engine.log_action(
            user_id=actor,
            action="ncrp:ingest_success",
            resource_id=case_id,
            resource_type="CASE",
            details={
                "chain": val["chain"],
                "wallet": val["wallet"],
                "amount": val["amount"],
                "ncrp_ack": ack,
            },
        )

        return {
            "status": "INGESTED",
            "case_id": case_id,
            "chain": val["chain"],
            "wallet": val["wallet"],
            "source": "NCRP",
        }

    def check_remote_connectivity(self) -> Dict[str, Any]:
        """
        Reports operational boundary status per PRD mandate:
        'If NCRP connectivity is not authorized or operational, report it as unavailable rather than simulating a successful live connection.'
        """
        if not self.is_operational():
            return {
                "system": "MHA_NCRP_GATEWAY",
                "status": "UNAVAILABLE_UNAUTHORIZED",
                "message": "Direct MHA NCRP gateway credentials are not configured in this environment. Ingest is restricted to authorized boundary intake.",
                "live_connection": False,
            }
        return {
            "system": "MHA_NCRP_GATEWAY",
            "status": "OPERATIONAL",
            "live_connection": True,
        }


ncrp_adapter = NCRPAdapter()
