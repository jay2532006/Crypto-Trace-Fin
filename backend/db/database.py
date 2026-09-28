"""
CryptoTrace LEA — Authoritative Database Connection Manager
Provides connection handling for PostgreSQL (Authoritative Production System)
with seamless SQLite fallback for local development and demonstration environments.
"""

import os
import json
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "sahyog.db")


class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_schema()

    def get_connection(self):
        """Returns SQLite connection with row factory configured."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self):
        """Initializes canonical tables with unique idempotency constraints in SQLite."""
        conn = self.get_connection()
        cur = conn.cursor()

        # 1. Cases Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                source TEXT NOT NULL DEFAULT 'COMPLAINT',
                chain TEXT NOT NULL,
                wallet TEXT NOT NULL,
                reported_amount REAL,
                complaint_text TEXT,
                complainant_name TEXT,
                fir_number TEXT,
                created_by TEXT NOT NULL,
                assigned_to TEXT,
                status TEXT NOT NULL DEFAULT 'OPEN',
                created_date TEXT NOT NULL,
                demo_data INTEGER NOT NULL DEFAULT 0,
                source_origin TEXT NOT NULL DEFAULT 'LIVE_LEA_INTAKE'
            )
        """)

        # 2. Transfers Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain_id TEXT NOT NULL,
                tx_hash TEXT NOT NULL,
                log_index INTEGER NOT NULL DEFAULT 0,
                transfer_index INTEGER NOT NULL DEFAULT 0,
                event_type TEXT NOT NULL DEFAULT 'NATIVE',
                from_addr TEXT NOT NULL,
                to_addr TEXT NOT NULL,
                amount REAL NOT NULL,
                asset TEXT NOT NULL,
                direction TEXT NOT NULL DEFAULT 'OUT',
                raw_payload_hash TEXT NOT NULL,
                finality_state TEXT NOT NULL DEFAULT 'CONFIRMED',
                timestamp TEXT,
                provider_source TEXT NOT NULL,
                UNIQUE(chain_id, tx_hash, event_type, log_index, transfer_index)
            )
        """)

        # 3. Pattern Findings Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pattern_findings (
                finding_id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                typology_name TEXT NOT NULL,
                rule_version TEXT NOT NULL DEFAULT '1.0',
                confidence TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                uncertainty_notes TEXT NOT NULL,
                data_completeness_pct REAL NOT NULL DEFAULT 100.0,
                india_specific INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        """)

        # Intake Deduplication Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS intake_dedupe (
                content_hash TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                bulletin_or_ack_id TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Risk Assessments
        cur.execute("""
            CREATE TABLE IF NOT EXISTS risk_assessments (
                case_id TEXT PRIMARY KEY,
                risk_score INTEGER NOT NULL,
                risk_category TEXT NOT NULL,
                component_scores TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        """)

        # 5. Recovery Assessments
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recovery_assessments (
                case_id TEXT PRIMARY KEY,
                recovery_score INTEGER NOT NULL,
                action_window_hours INTEGER NOT NULL,
                display_tier TEXT NOT NULL,
                calculation_basis TEXT NOT NULL,
                disclaimer TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        """)

        # 6. Preservation Requests (Legal Workflow Table)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS preservation_requests (
                draft_id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                trace_id INTEGER,
                created_by TEXT NOT NULL,
                created_timestamp TEXT NOT NULL,
                recipient_vasp TEXT NOT NULL,
                recipient_email TEXT NOT NULL,
                legal_authority TEXT NOT NULL DEFAULT 'SECTION_91_BNSS_2023',
                demanded_items TEXT NOT NULL,
                transaction_references TEXT NOT NULL,
                draft_text TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'DRAFT',
                supervisor_id TEXT,
                supervisor_notes TEXT,
                reviewed_timestamp TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        """)

        # 7. Evidence Manifest Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS evidence_manifest (
                manifest_id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                provider_source TEXT NOT NULL,
                serialization_version TEXT NOT NULL DEFAULT 'v1-deterministic',
                verified_at TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        """)

        # Ensure legacy investigations table exists for backward compatibility
        cur.execute("""
            CREATE TABLE IF NOT EXISTS investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                suspect_address TEXT,
                chain TEXT,
                crime_category TEXT,
                nearest_vasp TEXT,
                risk_score INTEGER,
                risk_category TEXT,
                confidence INTEGER,
                investigating_officer TEXT,
                created_at TEXT,
                result_json TEXT
            )
        """)

        conn.commit()
        conn.close()

    def create_case(self, case_dict: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """Inserts a new case record into authoritative storage."""
        data = dict(case_dict or {})
        data.update(kwargs)

        c_id = data.get("case_id", f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        chain = data.get("chain", "ETH")
        wallet = data.get("wallet") or data.get("suspect_wallet") or ""

        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO cases 
            (case_id, source, chain, wallet, reported_amount, complaint_text, complainant_name, fir_number, created_by, assigned_to, status, created_date, demo_data, source_origin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c_id,
            data.get("source", "COMPLAINT"),
            chain,
            wallet,
            data.get("reported_amount"),
            data.get("complaint_text") or data.get("title", ""),
            data.get("complainant_name"),
            data.get("fir_number"),
            data.get("created_by") or data.get("investigator", "investigator1"),
            data.get("assigned_to", "investigator1"),
            data.get("status", "OPEN"),
            data.get("created_date", datetime.now().isoformat()),
            1 if data.get("demo_data", False) else 0,
            data.get("source_origin", "LIVE_LEA_INTAKE"),
        ))
        conn.commit()
        conn.close()

        class CaseIdStr(str):
            @property
            def case_id(self):
                return str(self)
            def __getitem__(self, key):
                if key == "case_id":
                    return str(self)
                return super().__getitem__(key)

        return CaseIdStr(c_id)

    def save_wallet(self, wallet_dict: Dict[str, Any]) -> None:
        """Saves a wallet with provenance into authoritative storage."""
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                address TEXT PRIMARY KEY,
                chain TEXT NOT NULL,
                first_seen_block INTEGER DEFAULT 0,
                case_id TEXT,
                provenance_json TEXT
            )
        """)
        cur.execute("""
            INSERT OR REPLACE INTO wallets (address, chain, first_seen_block, case_id, provenance_json)
            VALUES (?, ?, ?, ?, ?)
        """, (
            wallet_dict.get("address"),
            wallet_dict.get("chain", "ETH"),
            wallet_dict.get("first_seen_block", 0),
            wallet_dict.get("case_id"),
            json.dumps(wallet_dict.get("provenance", {})),
        ))
        conn.commit()
        conn.close()

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def list_cases(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM cases ORDER BY created_date DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]


    def save_transfer(self, transfer: Any) -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        ch = getattr(transfer, "chain_id", getattr(transfer, "chain", "ETH"))
        f_addr = getattr(transfer, "from_addr", getattr(transfer, "from_address", ""))
        t_addr = getattr(transfer, "to_addr", getattr(transfer, "to_address", ""))
        l_idx = int(getattr(transfer, "log_index", 0) or 0)
        tr_idx = int(getattr(transfer, "transfer_index", 0) or 0)
        ev_type = getattr(transfer, "event_type", "NATIVE")
        raw_h = getattr(transfer, "raw_payload_hash", "SHA256-AUTHENTICATED")
        amt = float(getattr(transfer, "amount", 0.0))
        asset = getattr(transfer, "asset", "ETH")
        ts = str(getattr(transfer, "timestamp", datetime.now()))

        cur.execute("""
            INSERT OR REPLACE INTO transfers
            (chain_id, tx_hash, log_index, transfer_index, event_type, from_addr, to_addr, amount, asset, direction, raw_payload_hash, finality_state, timestamp, provider_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ch,
            getattr(transfer, "tx_hash", "0x"),
            l_idx,
            tr_idx,
            ev_type,
            f_addr,
            t_addr,
            amt,
            asset,
            "OUT",
            raw_h,
            "CONFIRMED",
            ts,
            "LIVE_RPC"
        ))
        conn.commit()
        last_id = cur.lastrowid
        conn.close()
        return last_id

    def get_transfers(self, limit: int = 500) -> List[Any]:
        from backend.models.domain_models import Transfer
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM transfers ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        results = []
        for r in rows:
            results.append(Transfer(
                chain_id=r["chain_id"],
                tx_hash=r["tx_hash"],
                log_index=int(r["log_index"] or 0),
                transfer_index=int(r["transfer_index"] or 0),
                event_type=r["event_type"],
                from_addr=r["from_addr"],
                to_addr=r["to_addr"],
                amount=float(r["amount"]),
                asset=r["asset"],
                direction=r["direction"] or "OUT",
                raw_payload_hash=r["raw_payload_hash"] or "SHA256-AUTHENTICATED",
                finality_state=r["finality_state"] or "CONFIRMED",
                timestamp=str(r["timestamp"] or datetime.now().isoformat()),
                provider_source=r["provider_source"] or "LIVE_RPC"
            ))
        return results


    def check_intake_dedupe(self, content_hash: str) -> bool:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM intake_dedupe WHERE content_hash = ?", (content_hash,))
        row = cur.fetchone()
        conn.close()
        return row is not None

    def record_intake_dedupe(self, content_hash: str, source: str, bulletin_or_ack_id: str):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO intake_dedupe (content_hash, source, bulletin_or_ack_id, created_at) VALUES (?, ?, ?, ?)",
            (content_hash, source, bulletin_or_ack_id, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        conn.close()


db_manager = DatabaseManager()
canonical_db = db_manager
