"""
CryptoTrace LEA - Trace Routes
Endpoints:
- POST /api/v1/trace (Executes Bounded Forensic Attribution Trace)
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from backend.tracing.trace_engine import bounded_tracer, TraceConstraints
from backend.audit.audit_engine import audit_engine
from backend.auth.decorators import get_current_user

router = APIRouter(prefix="/api/v1", tags=["Tracing"])
limiter = Limiter(key_func=get_remote_address)


class BoundedTraceRequest(BaseModel):
    address: str
    chain: Optional[str] = "ETH"
    case_id: Optional[str] = None
    max_hops: int = 5
    mode: Optional[str] = "DEMO"  # DEMO or LIVE
    direction: Optional[str] = "FORWARD"  # FORWARD, BACKWARD, BIDIRECTIONAL (§1.4)
    max_backward_hops: Optional[int] = 2


@router.post("/trace")
@limiter.limit("20/minute")
def execute_trace(request: Request, req: BoundedTraceRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Executes bounded deterministic multi-hop tracing (Rate limited: 20/min).
    Runs MULE_NETWORK, AdaptiveVASPScorer, and Heuristic Recovery Estimator.
    Supports forward, backward (fan-in), and bidirectional tracing per §1.4.
    """
    address = (req.address or "").strip()
    if not address:
        raise HTTPException(status_code=422, detail="Target address is required.")

    case_id = req.case_id or f"CR-2026-AUTO-{address[-6:].upper()}"
    constraints = TraceConstraints(
        max_hops=req.max_hops,
        direction=req.direction or "FORWARD",
        max_backward_hops=req.max_backward_hops or 2,
    )

    result = bounded_tracer.trace(
        start_address=address,
        chain=req.chain or "ETH",
        constraints=constraints,
        case_id=case_id,
        mode=req.mode or "DEMO",
    )

    # Chained Audit Log
    audit_engine.log_action(
        user_id=current_user.get("username", "investigator1"),
        action="trace:execute",
        resource_id=case_id,
        resource_type="TRACE",
        details={
            "address": address,
            "chain": req.chain,
            "mode": req.mode,
            "hops_discovered": len(result.get("hops", [])),
            "nearest_vasp": result.get("attribution", {}).get("vasp_name"),
        },
    )

    return result


@router.get("/vasps/geo")
def get_vasp_geo(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    §Phase5: Returns registered VASP geographic coordinates and FIU compliance metadata
    for jurisdiction map overlays.
    """
    from backend.attribution.vasp_registry import get_vasp_geo_summary
    return get_vasp_geo_summary()
