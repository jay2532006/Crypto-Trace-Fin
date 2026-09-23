"""
CryptoTrace LEA — Chained SHA-256 Audit Engine
Maintains an immutable, cryptographically verifiable log of all investigator, supervisor,
and system actions. Every event is chained to the previous event via SHA-256 digest.
"""

import os
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.storage.raw_payload_storage import serialize_deterministically

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "sahyog.db")


class AuditEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_table()

    def _init_table(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                result TEXT NOT NULL,
                details_json TEXT NOT NULL,
                previous_event_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_events(resource_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_events(user_id)")
        conn.commit()
        conn.close()

    def _get_latest_event_hash(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT event_hash FROM audit_events ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        return row[0] if row else "GENESIS_0000000000000000000000000000000000000000000000000000000000000000"

    def log_action(
        self,
        user_id: str,
        action: str,
        resource_id: str,
        resource_type: str,
        result: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Records a new material action and appends it to the tamper-evident hash chain."""
        timestamp = datetime.now().isoformat()
        previous_hash = self._get_latest_event_hash()
        details = details or {}
        details_str = serialize_deterministically(details)

        # Generate unique event ID
        event_id = f"AUDIT-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        # Compute chained SHA-256
        data_to_hash = f"{previous_hash}|{event_id}|{timestamp}|{user_id}|{action}|{resource_id}|{resource_type}|{result}|{details_str}"
        event_hash = hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO audit_events 
            (event_id, timestamp, user_id, action, resource_id, resource_type, result, details_json, previous_event_hash, event_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            timestamp,
            user_id,
            action,
            resource_id,
            resource_type,
            result,
            details_str,
            previous_hash,
            event_hash,
        ))
        conn.commit()
        conn.close()

        return {
            "event_id": event_id,
            "timestamp": timestamp,
            "user_id": user_id,
            "action": action,
            "resource_id": resource_id,
            "previous_event_hash": previous_hash,
            "event_hash": event_hash,
        }

    def verify_audit_chain(self) -> Dict[str, Any]:
        """
        Verifies the cryptographic integrity of the entire audit chain.
        Returns valid=True or points to the exact corrupted record index.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, event_id, timestamp, user_id, action, resource_id, resource_type, result, details_json, previous_event_hash, event_hash
            FROM audit_events ORDER BY id ASC
        """)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return {"valid": True, "is_valid": True, "total_events": 0, "message": "Audit log is empty."}

        expected_prev_hash = "GENESIS_0000000000000000000000000000000000000000000000000000000000000000"

        for row in rows:
            id_, event_id, timestamp, user_id, action, res_id, res_type, result, details_json, prev_hash, current_hash = row

            if prev_hash != expected_prev_hash:
                return {
                    "valid": False,
                    "is_valid": False,
                    "tampered_event_id": event_id,
                    "error": f"Chain link broken at event {event_id}. Expected prev_hash {expected_prev_hash}, got {prev_hash}.",
                }

            # Recalculate hash
            data_to_hash = f"{prev_hash}|{event_id}|{timestamp}|{user_id}|{action}|{res_id}|{res_type}|{result}|{details_json}"
            calculated_hash = hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()

            if calculated_hash != current_hash:
                return {
                    "valid": False,
                    "is_valid": False,
                    "tampered_event_id": event_id,
                    "error": f"Data tampering detected in event {event_id}. Hash mismatch!",
                }

            expected_prev_hash = current_hash

        return {"valid": True, "is_valid": True, "total_events": len(rows), "latest_hash": expected_prev_hash}

    def get_case_audit_trail(self, case_id: str) -> List[Dict[str, Any]]:
        """Retrieves chronological audit events for a specific case."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT event_id, timestamp, user_id, action, resource_id, resource_type, result, details_json, event_hash
            FROM audit_events WHERE resource_id = ? ORDER BY id ASC
        """, (case_id,))
        rows = cur.fetchall()
        conn.close()
        cols = ["event_id", "timestamp", "user_id", "action", "resource_id", "resource_type", "result", "details", "event_hash"]
        return [dict(zip(cols, [r[0], r[1], r[2], r[3], r[4], r[5], r[6], serialize_deterministically(r[7]), r[8]])) for r in rows]


# Singleton instance
audit_engine = AuditEngine()
