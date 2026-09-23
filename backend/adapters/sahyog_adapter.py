"""
CryptoTrace LEA — Phase 4A SAHYOG Boundary Adapter
Implements the MHA/I4C SAHYOG Intelligence Sharing Boundary Contract:
- Multi-agency bulletin schema
- Multi-wallet extraction and blockchain detection
- PRIVATE-KEY & MNEMONIC REJECTION (Mandatory security safeguard)
- Collaborative case creation and intelligence ingestion
- Source provenance tagging (SAHYOG_BULLETIN)
- Duplicate handling / bulletin deduplication
- Operational boundary: Reports UNAVAILABLE_UNAUTHORIZED if external credentials are not configured.
"""

import re
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.db.database import canonical_db
from backend.audit.audit_engine import audit_engine
from backend.adapters.provider_manager import provider_manager


MNEMONIC_PATTERN = re.compile(
    r"\b(?:abandon|ability|able|about|above|absent|absorb|abstract|absurd|abuse|access|accident|account|accuse|achieve|acid|acoustic|acquire|across|act|action|actor|actress|actual|adapt|add|addict|address|adjust|admit|adult|advance|advice|aerobic|affair|afford|afraid|again|age|agent|agree|ahead|aim|air|airport|aisle|alarm|album|alcohol|alert|alien|all|alley|allow|almost|alone|alpha|already|also|alter|always|amateur|amazing|among|amount|amused|analyst|anchor|ancient|anger|angle|angry|animal|ankle|announce|annual|another|answer|antenna|antique|anxiety|any|apart|apology|appear|apple|approve|april|arch|arctic|area|arena|argue|arm|armed|armor|army|around|arrange|arrest|arrive|arrow|art|artefact|artist|artwork|ask|aspect|assault|asset|assist|assume|asthma|athlete|atom|attack|attend|attitude|attract|auction|audit|august|aunt|author|auto|autumn|average|avocado|avoid|awake|award|aware|away|awesome|awful|awkward|axis|baby|bachelor|bacon|badge|bag|balance|balcony|ball|bamboo|banana|banner|bar|barely|bargain|barrel|base|basic|basket|battle|beach|bean|beauty|because|become|beef|before|begin|behave|behind|believe|below|belt|bench|benefit|best|betray|better|between|beyond|bicycle|bid|bike|bind|biology|bird|birth|bitter|black|blade|blame|blanket|blast|bleak|bless|blind|blood|blossom|blow|blue|blur|blush|board|boat|body|boil|bomb|bone|bonus|book|boost|border|boring|borrow|boss|bottom|bounce|box|boy|bracket|brain|brand|brass|brave|bread|breeze|brick|bridge|brief|bright|bring|brisk|broccoli|broken|bronze|broom|brother|brown|brush|bubble|buddy|budget|buffalo|build|bulb|bulk|bullet|bundle|bunker|burden|burger|burst|bus|business|busy|butter|buyer|buzz)\b",
    re.IGNORECASE,
)
HEX_PRIVATE_KEY_PATTERN = re.compile(r"\b(?:0x)?[a-fA-F0-9]{64}\b")

# Regex pattern for Bitcoin, EVM, Tron addresses
ETH_ADDR_REGEX = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
BTC_ADDR_REGEX = re.compile(r"\b(?:1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-zA-HJ-NP-Z0-9]{39,59})\b")
TRON_ADDR_REGEX = re.compile(r"\bT[A-Za-z1-9]{33}\b")


class SAHYOGAdapter:
    """
    SAHYOG Inter-Agency Intelligence Sharing Boundary Adapter.
    """

    def __init__(self, api_url: Optional[str] = None, auth_token: Optional[str] = None):
        self.api_url = api_url
        self.auth_token = auth_token
        self.processed_bulletin_hashes = set()

    def is_operational(self) -> bool:
        """SAHYOG live gateway requires explicit authorized endpoint and token."""
        return bool(self.api_url and self.auth_token)

    def get_connection_status(self) -> Dict[str, Any]:
        """Returns connection status per PRD Rule 1 (never fake live status)."""
        if not self.is_operational():
            return {
                "status": "UNAVAILABLE_UNAUTHORIZED",
                "operational": False,
                "message": "SAHYOG Inter-Agency gateway credentials are not configured in environment.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        return {
            "status": "CONNECTED_AUTHORIZED",
            "operational": True,
            "endpoint": self.api_url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def validate_and_sanitize_bulletin(self, bulletin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates bulletin schema, extracts target wallets, and sanitizes against key leaks.
        """
        raw_text = " ".join([
            str(bulletin.get("title", "")),
            str(bulletin.get("description", "")),
            str(bulletin.get("intelligence_notes", "")),
            str(bulletin.get("agency", "")),
        ])

        # 1. Private Key / Seed Phrase Detection & Rejection
        if HEX_PRIVATE_KEY_PATTERN.search(raw_text):
            return {
                "valid": False,
                "error": "SECURITY VIOLATION: Potential 64-character private key detected in bulletin text. Rejected for security compliance.",
            }

        words = raw_text.lower().split()
        bip39_matches = [w for w in words if MNEMONIC_PATTERN.match(w)]
        if len(bip39_matches) >= 12:
            return {
                "valid": False,
                "error": "SECURITY VIOLATION: Potential seed phrase detected in bulletin text. Rejected to protect cryptographic credentials.",
            }

        bulletin_id = str(bulletin.get("bulletin_id") or bulletin.get("id") or "").strip()
        if not bulletin_id:
            return {"valid": False, "error": "Bulletin identifier (bulletin_id) is missing."}

        # 2. Multi-wallet extraction
        candidate_wallets = list(bulletin.get("wallets") or [])
        if not candidate_wallets:
            # Auto-extract from raw text if explicit list was not given
            candidate_wallets.extend(ETH_ADDR_REGEX.findall(raw_text))
            candidate_wallets.extend(BTC_ADDR_REGEX.findall(raw_text))
            candidate_wallets.extend(TRON_ADDR_REGEX.findall(raw_text))

        # Deduplicate and detect chains
        extracted_wallets = []
        for w in set(candidate_wallets):
            chain = provider_manager.detect_chain(w)
            if chain:
                extracted_wallets.append({"address": w, "chain": chain.upper()})

        if not extracted_wallets:
            return {
                "valid": False,
                "error": "No valid blockchain addresses identified in SAHYOG bulletin.",
            }

        return {
            "valid": True,
            "bulletin_id": bulletin_id,
            "title": bulletin.get("title", "Inter-Agency Intelligence Bulletin"),
            "agency": bulletin.get("issuing_agency") or bulletin.get("agency", "LEA_COLLABORATIVE"),
            "classification": bulletin.get("classification", "CONFIDENTIAL_LAW_ENFORCEMENT"),
            "wallets": extracted_wallets,
            "crime_type": bulletin.get("crime_type", "CYBER_FRAUD"),
            "published_at": bulletin.get("published_at") or datetime.now(timezone.utc).isoformat(),
            "notes": bulletin.get("intelligence_notes", ""),
        }

    def ingest_bulletin(self, bulletin: Dict[str, Any], actor: str = "sahyog_gateway") -> Dict[str, Any]:
        """
        Idempotently ingest an inter-agency bulletin and create or update collaborative case intelligence.
        """
        val = self.validate_and_sanitize_bulletin(bulletin)
        if not val["valid"]:
            audit_engine.log_action(
                user_id=actor,
                action="sahyog:bulletin_rejected",
                resource_id=bulletin.get("bulletin_id", "UNKNOWN"),
                resource_type="BULLETIN",
                details={"reason": val["error"]},
            )
            return {"status": "REJECTED", "reason": val["error"]}

        # Deduplication check via content hash
        bulletin_bytes = f"{val['bulletin_id']}:{val['agency']}:{len(val['wallets'])}".encode()
        b_hash = hashlib.sha256(bulletin_bytes).hexdigest()
        if b_hash in self.processed_bulletin_hashes:
            return {
                "status": "ALREADY_EXISTS",
                "message": f"Bulletin {val['bulletin_id']} has already been processed.",
                "bulletin_id": val["bulletin_id"],
            }

        # Create or link to collaborative case
        bid = val["bulletin_id"]
        case_id = bid if bid.startswith("SAHYOG-") else f"SAHYOG-{bid}"
        existing_case = canonical_db.get_case(case_id)
        if not existing_case:
            created_case = canonical_db.create_case(
                case_id=case_id,
                title=f"SAHYOG: {val['title']}",
                investigator=f"SAHYOG_{val['agency']}",
                crime_type=val["crime_type"],
                source="SAHYOG_BULLETIN",
            )
        else:
            created_case = existing_case

        # Associate extracted wallets with case
        for w_item in val["wallets"]:
            canonical_db.save_wallet({
                "address": w_item["address"],
                "chain": w_item["chain"],
                "first_seen_block": 0,
                "case_id": case_id,
                "provenance": {
                    "source": "SAHYOG_BULLETIN",
                    "bulletin_id": val["bulletin_id"],
                    "agency": val["agency"],
                    "classification": val["classification"],
                },
            })

        self.processed_bulletin_hashes.add(b_hash)

        audit_engine.log_action(
            user_id=actor,
            action="sahyog:bulletin_ingested",
            resource_id=val["bulletin_id"],
            resource_type="BULLETIN",
            details={
                "case_id": case_id,
                "agency": val["agency"],
                "wallet_count": len(val["wallets"]),
                "classification": val["classification"],
            },
        )

        return {
            "status": "INGESTED",
            "case_id": case_id,
            "bulletin_id": val["bulletin_id"],
            "agency": val["agency"],
            "wallets_linked": len(val["wallets"]),
            "wallets": val["wallets"],
        }


sahyog_adapter = SAHYOGAdapter()
