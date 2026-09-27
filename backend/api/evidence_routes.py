"""
CryptoTrace LEA — Evidence Manifest & Audit Verification APIs
Endpoints:
- GET  /api/v1/evidence/payload/{payload_hash}
- POST /api/v1/evidence/verify/{payload_hash}
- GET  /api/v1/audit/trail/{case_id}
- GET  /api/v1/audit/verify-chain
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from backend.storage.raw_payload_storage import raw_storage
from backend.audit.audit_engine import audit_engine

router = APIRouter(prefix="/api/v1", tags=["Evidence & Audit"])


@router.get("/evidence/payload/{payload_hash}")
def get_raw_payload(payload_hash: str):
    """Retrieves raw JSON payload by SHA-256 hash."""
    payload = raw_storage.retrieve_payload(payload_hash)
    if not payload:
        raise HTTPException(status_code=404, detail="Raw payload hash not found in evidence repository.")
    return {"payload_hash": payload_hash, "data": payload}


@router.post("/evidence/verify/{payload_hash}")
def verify_payload_integrity(payload_hash: str):
    """
    Re-computes SHA-256 hash of on-disk serialized payload to prove forensic integrity.
    """
    is_valid = raw_storage.verify_integrity(payload_hash)
    return {
        "payload_hash": payload_hash,
        "integrity_verified": is_valid,
        "status": "VALID_FORENSIC_EVIDENCE" if is_valid else "TAMPERING_DETECTED",
    }


@router.get("/audit/trail/{case_id}")
def get_case_audit_trail(case_id: str):
    """Fetches chronological chained audit events for a case."""
    return audit_engine.get_case_audit_trail(case_id)


@router.get("/audit/verify-chain")
def verify_audit_chain():
    """
    Validates cryptographic chained SHA-256 integrity across the entire audit log.
    """
    return audit_engine.verify_audit_chain()


@router.get("/audit/events")
def get_all_audit_events(limit: int = 100):
    """Fetches chronological chained audit events across the platform."""
    return audit_engine.get_all_events(limit=limit)
