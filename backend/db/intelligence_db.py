"""
Intelligence DB - TraceX SIH 26183
DB-driven store for VASP hot-wallet clusters, mixer contracts, and DeFi bridges.
Seeds from static dicts in engine/vasp_cluster.py on first run.
Subsequent additions/updates go directly into SQLite without code changes.

Tables:
  vasp_entries      - known exchange deposit / hot-wallet addresses
  mixer_contracts   - on-chain privacy mixers / tumblers
  defi_bridges      - cross-chain bridge contracts used in laundering
  intelligence_meta - refresh metadata and version tracking
"""

import sqlite3
import json
import os
import time
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INTEL_DB_PATH = os.path.join(_BASE, "data", "intelligence.db")


def init_intelligence_db() -> None:
    """Create intelligence tables and seed from static dicts if empty. Idempotent."""
    os.makedirs(os.path.dirname(INTEL_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(INTEL_DB_PATH)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS vasp_entries (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            vasp_name     TEXT NOT NULL,
            hot_wallet    TEXT UNIQUE NOT NULL COLLATE NOCASE,
            chain         TEXT,
            country       TEXT,
            risk_level    TEXT DEFAULT 'MEDIUM',
            nodal_email   TEXT,
            fiu_status    TEXT DEFAULT 'UNREGISTERED',
            vasp_type     TEXT,
            freeze_auth   TEXT,
            metadata_json TEXT DEFAULT '{}',
            source        TEXT DEFAULT 'STATIC_SEED',
            updated_at    TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS mixer_contracts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            address    TEXT UNIQUE NOT NULL COLLATE NOCASE,
            name       TEXT,
            chain      TEXT,
            risk_level TEXT DEFAULT 'CRITICAL',
            category   TEXT DEFAULT 'MIXER',
            notes      TEXT,
            source     TEXT DEFAULT 'STATIC_SEED',
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS defi_bridges (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            address    TEXT UNIQUE NOT NULL COLLATE NOCASE,
            name       TEXT,
            chain      TEXT DEFAULT 'ETH',
            status     TEXT DEFAULT 'ACTIVE',
            notes      TEXT,
            source     TEXT DEFAULT 'STATIC_SEED',
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS intelligence_meta (
            key   TEXT PRIMARY KEY,
            value TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_vasp_wallet ON vasp_entries(hot_wallet COLLATE NOCASE);
        CREATE INDEX IF NOT EXISTS idx_mixer_addr  ON mixer_contracts(address COLLATE NOCASE);
        CREATE INDEX IF NOT EXISTS idx_bridge_addr ON defi_bridges(address COLLATE NOCASE);
    """)
    conn.commit()
    _seed_if_empty(conn, cur)
    conn.close()
    logger.info("Intelligence DB initialised at %s", INTEL_DB_PATH)


def _seed_if_empty(conn, cur):
    """Seed tables from static engine/vasp_cluster.py dicts when tables are empty."""
    cur.execute("SELECT COUNT(*) FROM vasp_entries"); vc = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM mixer_contracts"); mc = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM defi_bridges"); bc = cur.fetchone()[0]

    if vc > 0 and mc > 0 and bc > 0:
        return

    try:
        from engine.vasp_cluster import VASP_CLUSTERS, MIXER_CONTRACTS, DEFI_BRIDGES
    except ImportError:
        logger.warning("Could not import vasp_cluster for seeding.")
        return

    if vc == 0:
        for vasp_name, info in VASP_CLUSTERS.items():
            for wallet in info.get("hot_wallet_patterns", []):
                if wallet:
                    fiu = "REGISTERED" if info.get("country", "").lower() == "india" else "UNREGISTERED"
                    norm = wallet.lower() if wallet.startswith("0x") else wallet
                    cur.execute("""
                        INSERT OR IGNORE INTO vasp_entries
                          (vasp_name, hot_wallet, chain, country, risk_level,
                           nodal_email, fiu_status, vasp_type, freeze_auth, metadata_json, source)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)
                    """, (vasp_name, norm, ",".join(info.get("chains", [])),
                          info.get("country",""), info.get("risk_level","MEDIUM"),
                          info.get("nodal_email",""), fiu,
                          info.get("vasp_type","Exchange"),
                          info.get("freeze_authority",""),
                          json.dumps({"legal_address": info.get("legal_address","")}),
                          "STATIC_SEED"))
        logger.info("Seeded vasp_entries.")

    if mc == 0:
        for addr, name in MIXER_CONTRACTS.items():
            cur.execute("""
                INSERT OR IGNORE INTO mixer_contracts (address, name, chain, source)
                VALUES (?, ?, 'ETH', 'STATIC_SEED')
            """, (addr.lower(), name))
        logger.info("Seeded mixer_contracts.")

    if bc == 0:
        for addr, name in DEFI_BRIDGES.items():
            chain = "TRON" if addr.startswith("T") else "ETH"
            cur.execute("""
                INSERT OR IGNORE INTO defi_bridges (address, name, chain, source)
                VALUES (?, ?, ?, 'STATIC_SEED')
            """, (addr.lower(), name, chain))
        logger.info("Seeded defi_bridges.")

    cur.execute("INSERT OR REPLACE INTO intelligence_meta (key,value) VALUES ('seeded_at', ?)",
                (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),))
    conn.commit()


# ─── READ FUNCTIONS ────────────────────────────────────────────────────────────

def lookup_vasp_db(address: str) -> Optional[Dict[str, Any]]:
    """Look up wallet address in intelligence DB. Returns VASP record or None."""
    if not address:
        return None
    norm = address.lower() if address.startswith("0x") else address
    conn = sqlite3.connect(INTEL_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM vasp_entries WHERE LOWER(hot_wallet) = LOWER(?)", (norm,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {k: row[k] for k in row.keys()}
    return None


def lookup_mixer_db(address: str) -> Optional[Dict[str, Any]]:
    """Check if address is a known mixer in intelligence DB."""
    if not address:
        return None
    conn = sqlite3.connect(INTEL_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM mixer_contracts WHERE LOWER(address) = LOWER(?)", (address.lower(),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def lookup_bridge_db(address: str) -> Optional[Dict[str, Any]]:
    """Check if address is a known DeFi bridge in intelligence DB."""
    if not address:
        return None
    conn = sqlite3.connect(INTEL_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM defi_bridges WHERE LOWER(address) = LOWER(?)", (address.lower(),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def list_all_vasps(risk_level: Optional[str] = None, chain: Optional[str] = None) -> List[Dict]:
    conn = sqlite3.connect(INTEL_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q, params = "SELECT * FROM vasp_entries WHERE 1=1", []
    if risk_level:
        q += " AND UPPER(risk_level) = UPPER(?)"; params.append(risk_level)
    if chain:
        q += " AND chain LIKE ?"; params.append(f"%{chain.upper()}%")
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_all_mixers(chain: Optional[str] = None) -> List[Dict]:
    conn = sqlite3.connect(INTEL_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if chain:
        cur.execute("SELECT * FROM mixer_contracts WHERE UPPER(chain) = UPPER(?)", (chain,))
    else:
        cur.execute("SELECT * FROM mixer_contracts ORDER BY risk_level")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_all_bridges(chain: Optional[str] = None) -> List[Dict]:
    conn = sqlite3.connect(INTEL_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if chain:
        cur.execute("SELECT * FROM defi_bridges WHERE UPPER(chain) = UPPER(?)", (chain,))
    else:
        cur.execute("SELECT * FROM defi_bridges")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_intelligence_stats() -> Dict[str, Any]:
    conn = sqlite3.connect(INTEL_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM vasp_entries"); v = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM mixer_contracts"); m = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM defi_bridges"); b = cur.fetchone()[0]
    cur.execute("SELECT value FROM intelligence_meta WHERE key='seeded_at'")
    seeded = cur.fetchone()
    cur.execute("SELECT value FROM intelligence_meta WHERE key='last_updated'")
    updated = cur.fetchone()
    conn.close()
    return {
        "vasp_wallets": v, "mixer_contracts": m, "defi_bridges": b,
        "seeded_at": seeded[0] if seeded else None,
        "last_updated": updated[0] if updated else None,
    }


# ─── WRITE FUNCTIONS (Admin / Integration Use) ─────────────────────────────────

def _touch_updated(cur):
    cur.execute("INSERT OR REPLACE INTO intelligence_meta (key,value) VALUES ('last_updated', ?)",
                (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),))


def add_vasp_wallet(vasp_name: str, hot_wallet: str, chain: str, country: str,
                    risk_level: str = "MEDIUM", nodal_email: str = "",
                    fiu_status: str = "UNREGISTERED", vasp_type: str = "Exchange",
                    freeze_auth: str = "", metadata: Optional[Dict] = None,
                    source: str = "MANUAL") -> bool:
    try:
        conn = sqlite3.connect(INTEL_DB_PATH)
        cur = conn.cursor()
        norm = hot_wallet.lower() if hot_wallet.startswith("0x") else hot_wallet
        cur.execute("""
            INSERT INTO vasp_entries
              (vasp_name, hot_wallet, chain, country, risk_level, nodal_email,
               fiu_status, vasp_type, freeze_auth, metadata_json, source, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
            ON CONFLICT(hot_wallet) DO UPDATE SET
              vasp_name=excluded.vasp_name, risk_level=excluded.risk_level,
              nodal_email=excluded.nodal_email, fiu_status=excluded.fiu_status,
              source=excluded.source, updated_at=excluded.updated_at
        """, (vasp_name, norm, chain.upper(), country, risk_level.upper(),
              nodal_email, fiu_status, vasp_type, freeze_auth,
              json.dumps(metadata or {}), source))
        _touch_updated(cur)
        conn.commit(); conn.close()
        return True
    except Exception as e:
        logger.error("add_vasp_wallet failed: %s", e)
        return False


def add_mixer_contract(address: str, name: str, chain: str = "ETH",
                       risk_level: str = "CRITICAL", category: str = "MIXER",
                       notes: str = "", source: str = "MANUAL") -> bool:
    try:
        conn = sqlite3.connect(INTEL_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO mixer_contracts (address, name, chain, risk_level, category, notes, source, updated_at)
            VALUES (?,?,?,?,?,?,?,datetime('now'))
            ON CONFLICT(address) DO UPDATE SET
              name=excluded.name, risk_level=excluded.risk_level, updated_at=excluded.updated_at
        """, (address.lower(), name, chain.upper(), risk_level.upper(), category, notes, source))
        _touch_updated(cur)
        conn.commit(); conn.close()
        return True
    except Exception as e:
        logger.error("add_mixer_contract failed: %s", e)
        return False


def add_defi_bridge(address: str, name: str, chain: str = "ETH",
                    status: str = "ACTIVE", notes: str = "",
                    source: str = "MANUAL") -> bool:
    try:
        conn = sqlite3.connect(INTEL_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO defi_bridges (address, name, chain, status, notes, source, updated_at)
            VALUES (?,?,?,?,?,?,datetime('now'))
            ON CONFLICT(address) DO UPDATE SET
              name=excluded.name, status=excluded.status, updated_at=excluded.updated_at
        """, (address.lower(), name, chain.upper(), status, notes, source))
        _touch_updated(cur)
        conn.commit(); conn.close()
        return True
    except Exception as e:
        logger.error("add_defi_bridge failed: %s", e)
        return False
