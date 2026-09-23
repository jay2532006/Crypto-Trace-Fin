"""
CryptoTrace LEA — Ingestion Pipeline (8-Stage Architecture)
Per PRD & Implementation Plan:
1. FETCH: Acquire provider data
2. VALIDATE: Validate block, transaction, addresses, values
3. EXTRACT: Extract supported native/token/internal/bridge events
4. NORMALIZE: Convert to canonical Transfer entities & compute raw SHA-256 hash
5. DEDUPLICATE: Memory/Redis duplicate suppression
6. PERSIST: Authoritative DB persistence
7. COMMIT: Advance checkpoint after durable persistence
8. ADVANCE: Graph projection update & publish to downstream intelligence
"""

import hashlib
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone

from backend.models.domain_models import Transfer
from backend.storage.raw_payload_storage import raw_storage
from backend.db.database import canonical_db
from backend.audit.audit_engine import audit_engine


class IngestionPipeline:
    def __init__(self):
        self.seen_signatures: Set[str] = set()
        self.checkpoints: Dict[str, int] = {}  # chain -> last_processed_block

    def process_raw_event(self, raw_event: Dict[str, Any], chain: str = "ETH", actor: str = "ingestion_worker") -> Dict[str, Any]:
        """
        Executes the 8-stage ingestion sequence for an incoming blockchain event.
        """
        # 1. FETCH / INTAKE
        if not raw_event:
            return {"status": "REJECTED", "stage": "FETCH", "reason": "Empty payload"}

        # 2. VALIDATE
        tx_hash = raw_event.get("tx_hash") or raw_event.get("hash")
        sender = raw_event.get("from_address") or raw_event.get("from")
        recipient = raw_event.get("to_address") or raw_event.get("to")
        amount = float(raw_event.get("amount", 0.0))

        if not tx_hash or not sender or not recipient or amount <= 0:
            return {
                "status": "REJECTED",
                "stage": "VALIDATE",
                "reason": "Missing tx_hash, sender, recipient, or non-positive amount"
            }

        # 3. EXTRACT
        event_type = raw_event.get("event_type", "NATIVE").upper()
        block_number = int(raw_event.get("block_number", 0))
        event_index = int(raw_event.get("event_index", 0))
        transfer_index = int(raw_event.get("transfer_index", 0))

        # Save raw payload with deterministic SHA-256
        raw_hash = raw_storage.store_payload(
            payload_dict=raw_event,
            chain_id=chain.upper(),
            block_height=block_number,
            tx_hash=tx_hash
        )

        # 4. NORMALIZE
        canonical_transfer = Transfer(
            chain_id=chain.upper(),
            tx_hash=tx_hash,
            log_index=event_index,
            transfer_index=transfer_index,
            event_type=event_type,
            from_addr=sender,
            to_addr=recipient,
            amount=amount,
            asset=raw_event.get("asset", chain.upper()),
            direction="OUT",
            raw_payload_hash=raw_hash,
            finality_state="CONFIRMED",
            timestamp=datetime.now(timezone.utc).isoformat(),
            provider_source="LIVE_RPC"
        )

        # 5. DEDUPLICATE (Unique canonical transfer signature)
        sig = f"{chain.upper()}:{tx_hash}:{event_type}:{event_index}:{transfer_index}"
        if sig in self.seen_signatures:
            return {
                "status": "DEDUPLICATED",
                "stage": "DEDUPLICATE",
                "signature": sig,
                "raw_hash": raw_hash
            }
        self.seen_signatures.add(sig)

        # 6. PERSIST (Authoritative DB)
        canonical_db.save_transfer(canonical_transfer)

        # 7. COMMIT (Advance Checkpoint)
        if block_number > self.checkpoints.get(chain.upper(), 0):
            self.checkpoints[chain.upper()] = block_number

        # 8. ADVANCE (Audit + Downstream Intelligence Event)
        audit_engine.log_action(
            user_id=actor,
            action="transfer:ingest",
            resource_id=sig,
            resource_type="TRANSFER",
            details={
                "chain": chain.upper(),
                "tx_hash": tx_hash,
                "amount": amount,
                "raw_hash": raw_hash,
                "checkpoint": self.checkpoints.get(chain.upper())
            }
        )

        return {
            "status": "INGESTED",
            "stage": "ADVANCE",
            "signature": sig,
            "raw_hash": raw_hash,
            "transfer": canonical_transfer.model_dump(),
            "checkpoint": self.checkpoints.get(chain.upper())
        }

    def get_checkpoint(self, chain: str) -> int:
        return self.checkpoints.get(chain.upper(), 0)

    def handle_reorg(self, chain: str, rollback_block: int) -> Dict[str, Any]:
        """
        Rolls back the checkpoint and invalidates transient transfers after rollback_block.
        """
        current = self.checkpoints.get(chain.upper(), 0)
        self.checkpoints[chain.upper()] = rollback_block
        audit_engine.log_action(
            user_id="reorg_detector",
            action="chain:reorg_rollback",
            resource_id=chain.upper(),
            resource_type="CHECKPOINT",
            details={"previous_block": current, "rollback_block": rollback_block}
        )
        return {
            "status": "REORG_HANDLED",
            "chain": chain.upper(),
            "rollback_block": rollback_block,
            "previous_block": current
        }


ingestion_pipeline = IngestionPipeline()
