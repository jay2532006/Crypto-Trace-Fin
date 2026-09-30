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
def list_cases(
    page: int = 1,
    per_page: int = 25,
    chain: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Lists investigations stored in the database with pagination and filtering."""
    fetch_limit = limit or max(50, page * per_page)
    cases = db_manager.list_cases(fetch_limit)
    if chain:
        cases = [c for c in cases if (c.get("chain") or "").upper() == chain.upper()]
    if status:
        cases = [c for c in cases if (c.get("status") or "").upper() == status.upper()]
    start_idx = (page - 1) * per_page
    return cases[start_idx : start_idx + per_page]


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

@router.get("/cases/{case_id}/report.pdf")
def download_case_report_pdf(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Generates and returns deterministic, court-admissible PDF forensic investigation report.
    Guarded by RBAC and logged in immutable chained audit engine.
    """
    from fastapi.responses import Response
    from backend.legal.report_generator import forensic_report_generator
    from backend.tracing.trace_engine import bounded_tracer, TraceConstraints

    case = db_manager.get_case(case_id)
    if not case:
        for fix in get_crypto_trace_fixtures():
            if fix["case_id"] == case_id:
                case = fix
                break
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")

    wallet = case.get("suspect_wallet") or case.get("wallet") or ""
    chain = case.get("chain", "ETH")
    mode = "DEMO" if case.get("demo_data") else "LIVE"

    trace_data = bounded_tracer.trace(
        start_address=wallet,
        chain=chain,
        constraints=TraceConstraints(max_hops=4),
        case_id=case_id,
        mode=mode,
    )

    audit_head = audit_engine.verify_audit_chain().get("latest_hash")

    pdf_bytes = forensic_report_generator.generate_report_pdf(
        case=case,
        trace=trace_data,
        audit_head_hash=audit_head,
        deterministic=True,
    )

    audit_engine.log_action(
        user_id=current_user.get("username", "investigator1"),
        action="report:generate_pdf",
        resource_id=case_id,
        resource_type="REPORT_PDF",
        details={"case_id": case_id, "size_bytes": len(pdf_bytes)},
    )

    filename = f"Forensic_Report_{case_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@router.get("/cases/{case_id}/linked-cases")
def get_linked_cases(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """§6.1: Retrieves cross-case linked investigations based on shared suspect/mule wallets."""
    linked = db_manager.get_linked_cases_for_case(case_id)
    return {
        "case_id": case_id,
        "linked_case_count": len(linked),
        "linked_cases": linked,
    }


@router.get("/analytics/dashboard")
def get_analytics_dashboard(current_user: Dict[str, Any] = Depends(get_current_user)):
    """§7.2: Retrieves aggregate LEA analytics dashboard metrics."""
    return {
        "status": "ok",
        "data": db_manager.get_lea_aggregate_analytics(),
    }

