# backend/ingestion/intake_orchestrator.py
"""
CryptoTrace LEA - Intake to Trace Orchestrator
Bridges external gateway ingestion (NCRP / SAHYOG) to forensic tracing and preservation notices.
Maintains state progression: RECEIVED -> VALIDATED -> TRACING -> ATTRIBUTED -> NOTICE DRAFTED.
Preserves strict human-in-the-loop: legal notices remain in DRAFT status.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.adapters.ncrp_adapter import NCRPAdapter
from backend.adapters.sahyog_adapter import SAHYOGAdapter
from backend.tracing.trace_engine import bounded_tracer, TraceConstraints
from backend.legal.notice_generator import notice_generator
from backend.audit.audit_engine import audit_engine
from backend.config.base import get_config

class IntakeOrchestrator:
    def __init__(self):
        self.ncrp_adapter = NCRPAdapter()
        self.sahyog_adapter = SAHYOGAdapter()
        self.queue: List[Dict[str, Any]] = []

    def get_connection_status(self) -> Dict[str, Any]:
        return {
            "ncrp": self.ncrp_adapter.get_connection_status(),
            "sahyog": self.sahyog_adapter.get_connection_status(),
            "gateway_mode": "SANDBOX" if not (self.ncrp_adapter.is_operational() or self.sahyog_adapter.is_operational()) else "LIVE",
            "banner": "SANDBOX GATEWAY ? NOT A LIVE MHA CONNECTION"
        }

    def process_ncrp_complaint(self, complaint: Dict[str, Any], actor: str = "ncrp_gateway") -> Dict[str, Any]:
        res = self.ncrp_adapter.ingest_ncrp_complaint(complaint, actor=actor)
        if res.get("status") == "INGESTED":
            case_id = res.get("case_id")
            wallet = complaint.get("suspect_wallet") or complaint.get("wallet")
            queue_entry = {
                "id": f"QUEUE-{case_id}",
                "source": "NCRP",
                "case_id": case_id,
                "wallet": wallet,
                "chain": complaint.get("chain", "ETH"),
                "status": "VALIDATED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self.queue.insert(0, queue_entry)
            if get_config().INTAKE_AUTOTRACE:
                self.run_trace_and_notice(case_id, wallet, complaint.get("chain", "ETH"))
        return res

    def process_sahyog_bulletin(self, bulletin: Dict[str, Any], actor: str = "sahyog_gateway") -> Dict[str, Any]:
        res = self.sahyog_adapter.ingest_bulletin(bulletin, actor=actor)
        if res.get("status") == "INGESTED":
            case_id = res.get("case_id")
            wallets = bulletin.get("wallets", [])
            primary_wallet = wallets[0] if wallets else "0xUnknown"
            queue_entry = {
                "id": f"QUEUE-{case_id}",
                "source": "SAHYOG",
                "case_id": case_id,
                "wallet": primary_wallet,
                "chain": "ETH",
                "status": "VALIDATED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self.queue.insert(0, queue_entry)
            if get_config().INTAKE_AUTOTRACE:
                self.run_trace_and_notice(case_id, primary_wallet, "ETH")
        return res

    def run_trace_and_notice(self, case_id: str, wallet: str, chain: str = "ETH") -> Dict[str, Any]:
        for item in self.queue:
            if item.get("case_id") == case_id:
                item["status"] = "TRACING"

        trace_res = bounded_tracer.trace(
            start_address=wallet,
            chain=chain,
            constraints=TraceConstraints(max_hops=4),
            case_id=case_id,
            mode="DEMO" if get_config().APP_MODE == "demo" else "LIVE"
        )

        for item in self.queue:
            if item.get("case_id") == case_id:
                item["status"] = "ATTRIBUTED"

        draft = notice_generator.create_draft(case_id=case_id, trace_data=trace_res)

        for item in self.queue:
            if item.get("case_id") == case_id:
                item["status"] = "NOTICE DRAFTED"
                item["notice_id"] = draft.draft_id

        audit_engine.log_action(
            user_id="intake_orchestrator",
            action="intake:autotrace_complete",
            resource_id=case_id,
            resource_type="CASE",
            details={"notice_id": draft.draft_id, "status": "DRAFT"}
        )

        return {"trace": trace_res, "notice": draft.model_dump()}

intake_orchestrator = IntakeOrchestrator()
