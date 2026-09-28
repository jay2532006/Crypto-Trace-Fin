# backend/api/intake_routes.py
"""
CryptoTrace LEA - External Intake HTTP Routes
Endpoints:
- POST /api/v1/intake/ncrp/complaint (Auth: INTEGRATION_SERVICE / ADMIN)
- POST /api/v1/intake/sahyog/bulletin (Auth: INTEGRATION_SERVICE / ADMIN)
- GET  /api/v1/intake/status (Auth: Any authenticated user)
- GET  /api/v1/intake/queue (Auth: INVESTIGATOR+)
- POST /api/v1/intake/{case_id}/trace (Auth: INVESTIGATOR+)
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Header, status
from pydantic import BaseModel

from backend.ingestion.intake_orchestrator import intake_orchestrator
from backend.auth.jwt_handler import decode_access_token
from backend.auth.decorators import get_current_user
from backend.db.database import db_manager

router = APIRouter(prefix="/api/v1/intake", tags=["Intake"])

def require_integration_service(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token required for intake service endpoints.",
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Bearer token format.",
        )
    payload = decode_access_token(parts[1])
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired intake service token.",
        )
    role = payload.get("role", "")
    if role not in ("INTEGRATION_SERVICE", "ADMINISTRATOR"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Role '{role}' cannot post to external ingest. Requires INTEGRATION_SERVICE.",
        )
    return payload

@router.get("/status")
def get_intake_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns connectivity status of NCRP and SAHYOG gateways."""
    return intake_orchestrator.get_connection_status()

@router.get("/queue")
def get_intake_queue(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns recent ingested cases and their forensic processing progression."""
    return intake_orchestrator.queue

@router.post("/ncrp/complaint")
def ingest_ncrp_complaint(
    complaint: Dict[str, Any],
    service_user: Dict[str, Any] = Depends(require_integration_service),
):
    """Ingests a cybercrime complaint from the NCRP portal."""
    res = intake_orchestrator.process_ncrp_complaint(
        complaint, actor=service_user.get("sub", "ncrp_gateway")
    )
    if res.get("status") == "REJECTED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res)
    return res

@router.post("/sahyog/bulletin")
def ingest_sahyog_bulletin(
    bulletin: Dict[str, Any],
    service_user: Dict[str, Any] = Depends(require_integration_service),
):
    """Ingests an inter-agency collaborative intelligence bulletin from SAHYOG."""
    res = intake_orchestrator.process_sahyog_bulletin(
        bulletin, actor=service_user.get("sub", "sahyog_gateway")
    )
    if res.get("status") == "REJECTED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res)
    return res

@router.post("/{case_id}/trace")
def trigger_case_trace(
    case_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Manually kicks off bounded forensic tracing and notice drafting for an ingested case."""
    case = db_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found.")

    res = intake_orchestrator.run_trace_and_notice(
        case_id=case_id,
        wallet=case["wallet"],
        chain=case.get("chain", "ETH"),
    )
    return res
