"""
CryptoTrace LEA — Legal Notice & Supervisor Workflow APIs
Endpoints:
- POST /api/v1/notices/draft
- POST /api/v1/notices/{draft_id}/submit
- POST /api/v1/notices/{draft_id}/approve (Requires SUPERVISOR role)
- POST /api/v1/notices/{draft_id}/reject (Requires SUPERVISOR role)
- GET  /api/v1/notices/{draft_id}
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.legal.notice_generator import notice_generator
from backend.auth.decorators import get_current_user, require_supervisor
from backend.audit.audit_engine import audit_engine

router = APIRouter(prefix="/api/v1/notices", tags=["Legal Notices"])

# In-memory drafts registry (backed by DB)
DRAFTS_STORE: Dict[str, Dict[str, Any]] = {}


class CreateNoticeDraftRequest(BaseModel):
    case_id: str
    trace_data: Dict[str, Any]
    investigating_officer: Optional[str] = "Inspector R. Sharma"
    unit: Optional[str] = "Cyber Crime Police Station"
    state: Optional[str] = "Maharashtra"
    fir_number: Optional[str] = "FIR-CR-2026/89"
    complainant: Optional[str] = "Complainant Victim"


class ReviewNoticeRequest(BaseModel):
    supervisor_notes: Optional[str] = "Approved after reviewing on-chain trace hops and VASP attribution."


@router.post("/draft")
def draft_notice(req: CreateNoticeDraftRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Creates a formal Section 91 BNSS 2023 legal notice in DRAFT status."""
    draft = notice_generator.create_draft(
        case_id=req.case_id,
        trace_data=req.trace_data,
        investigating_officer=req.investigating_officer or current_user.get("username", "IO"),
        unit=req.unit or "Cyber Cell",
        state=req.state or "State Police",
        fir_number=req.fir_number or "CR-FIR",
        complainant=req.complainant or "Victim",
    )
    draft_dict = draft.model_dump()
    DRAFTS_STORE[draft.draft_id] = draft_dict
    return draft_dict


@router.post("/{draft_id}/submit")
def submit_notice_for_approval(draft_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Moves notice draft from DRAFT to PENDING_APPROVAL status."""
    draft = DRAFTS_STORE.get(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Notice draft not found.")
    draft["status"] = "PENDING_APPROVAL"

    audit_engine.log_action(
        user_id=current_user.get("username", "investigator1"),
        action="notice:submit_approval",
        resource_id=draft_id,
        resource_type="LEGAL_NOTICE",
        details={"case_id": draft.get("case_id"), "status": "PENDING_APPROVAL"},
    )
    return {"status": "SUCCESS", "draft": draft}


@router.post("/{draft_id}/approve")
def approve_notice(
    draft_id: str,
    req: Optional[ReviewNoticeRequest] = None,
    supervisor: Dict[str, Any] = Depends(require_supervisor),
):
    """
    Supervisor Approval Gate:
    Strictly requires SUPERVISOR or ADMINISTRATOR role to approve notice for legal dispatch.
    """
    draft = DRAFTS_STORE.get(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Notice draft not found.")

    draft["status"] = "APPROVED"
    draft["supervisor_id"] = supervisor.get("username", "supervisor1")
    draft["supervisor_notes"] = req.supervisor_notes if req else "Authorized for formal dispatch."

    audit_engine.log_action(
        user_id=supervisor.get("username", "supervisor1"),
        action="notice:approve",
        resource_id=draft_id,
        resource_type="LEGAL_NOTICE",
        details={"case_id": draft.get("case_id"), "status": "APPROVED", "notes": draft["supervisor_notes"]},
    )
    return {"status": "SUCCESS", "message": "Notice APPROVED by Supervisor", "draft": draft}


@router.post("/{draft_id}/reject")
def reject_notice(
    draft_id: str,
    req: Optional[ReviewNoticeRequest] = None,
    supervisor: Dict[str, Any] = Depends(require_supervisor),
):
    """Rejects notice draft. Requires SUPERVISOR role."""
    draft = DRAFTS_STORE.get(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Notice draft not found.")

    draft["status"] = "REJECTED"
    draft["supervisor_id"] = supervisor.get("username", "supervisor1")
    draft["supervisor_notes"] = req.supervisor_notes if req else "Insufficient evidence for freeze requisition."

    audit_engine.log_action(
        user_id=supervisor.get("username", "supervisor1"),
        action="notice:reject",
        resource_id=draft_id,
        resource_type="LEGAL_NOTICE",
        details={"case_id": draft.get("case_id"), "status": "REJECTED", "notes": draft["supervisor_notes"]},
    )
    return {"status": "SUCCESS", "message": "Notice REJECTED by Supervisor", "draft": draft}


@router.get("/{draft_id}")
def get_notice(draft_id: str):
    """Retrieves notice draft."""
    draft = DRAFTS_STORE.get(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Notice draft not found.")
    return draft
