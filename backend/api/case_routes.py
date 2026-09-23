"""
CryptoTrace LEA — Case Intake & Management APIs
Endpoints:
- POST /api/v1/cases (Authorized Case Intake)
- GET  /api/v1/cases/{case_id}
- GET  /api/v1/cases (List cases)
- GET  /api/v1/fixtures (List SIH 26183 test fixtures)
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.db.database import db_manager
from backend.audit.audit_engine import audit_engine
from backend.auth.decorators import get_current_user
from backend.fixtures.demo_cases_v2 import get_crypto_trace_fixtures

router = APIRouter(prefix="/api/v1", tags=["Cases"])


class CaseIntakeRequest(BaseModel):
    chain: str
    wallet: str
    reported_amount: Optional[float] = None
    source: str = "COMPLAINT"
    complaint_text: Optional[str] = None
    complainant_name: Optional[str] = None
    fir_number: Optional[str] = None
    case_id: Optional[str] = None
    demo_data: bool = False


@router.post("/cases")
def create_case(req: CaseIntakeRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Creates a new authorized case record and logs material action."""
    case_id = req.case_id or f"CR-2026-{req.chain.upper()}-{req.wallet[-6:].upper()}"
    case_dict = {
        "case_id": case_id,
        "source": req.source,
        "chain": req.chain.upper(),
        "wallet": req.wallet.strip(),
        "reported_amount": req.reported_amount,
        "complaint_text": req.complaint_text,
        "complainant_name": req.complainant_name,
        "fir_number": req.fir_number,
        "created_by": current_user.get("username", "investigator1"),
        "assigned_to": current_user.get("username", "investigator1"),
        "status": "OPEN",
        "demo_data": req.demo_data,
        "source_origin": "DEMO_CASE_SIH26183" if req.demo_data else "LIVE_LEA_INTAKE",
    }

    db_manager.create_case(case_dict)

    # Chained Audit Log
    audit_engine.log_action(
        user_id=current_user.get("username", "investigator1"),
        action="case:create",
        resource_id=case_id,
        resource_type="CASE",
        details={"wallet": req.wallet, "chain": req.chain, "source": req.source},
    )

    return {"status": "SUCCESS", "case_id": case_id, "case": case_dict}


@router.get("/cases")
def list_cases(limit: int = 50, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Lists investigations stored in the database."""
    return db_manager.list_cases(limit)


@router.get("/cases/{case_id}")
def get_case(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieves case details by case_id."""
    case = db_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")
    return case


@router.get("/fixtures")
def list_fixtures():
    """Lists dedicated SIH 26183 evaluation test fixtures."""
    return get_crypto_trace_fixtures()
