"""
CryptoTrace LEA — KùzuDB Local Embedded Graph Engine
High-Performance, Zero-Rate-Limit Embedded Property Graph Database
Replaces cloud-hosted Neo4j Aura with a local, in-process C++ graph engine.
Storage Location: ./data/kuzu_db
"""

import os
import re
import time
import logging
from typing import Dict, Any, List, Optional
import kuzu

logger = logging.getLogger("tracex.kuzu")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
KUZU_DB_PATH = os.getenv("KUZU_DB_PATH", os.path.join(DATA_DIR, "kuzu.db"))

_db: Optional[kuzu.Database] = None
_conn: Optional[kuzu.Connection] = None


def get_kuzu_connection() -> kuzu.Connection:
    """Obtain or initialize singleton Kùzu database and connection."""
    global _db, _conn
    if _conn is not None:
        return _conn

    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        # Buffer pool size: 256MB default for fast in-memory execution on local machines
        _db = kuzu.Database(KUZU_DB_PATH, buffer_pool_size=256 * 1024 * 1024)
        _conn = kuzu.Connection(_db)
        logger.info(f"Initialized KùzuDB local graph at {KUZU_DB_PATH}")
        init_kuzu_schema(_conn)
        return _conn
    except Exception as e:
        logger.error(f"Failed to initialize KùzuDB: {e}")
        # In case already opened by another connection in same process
        if _db is not None:
            _conn = kuzu.Connection(_db)
            return _conn
        raise e


def init_kuzu_schema(conn: Optional[kuzu.Connection] = None) -> bool:
    """Initialize node and relationship tables in KùzuDB."""
    c = conn or get_kuzu_connection()
    try:
        # 1. Node tables
        c.execute("""
            CREATE NODE TABLE IF NOT EXISTS InvestigationCase(
                case_id STRING,
                chain STRING,
                suspect_address STRING,
                risk_score DOUBLE,
                terminal_vasp STRING,
                updated_at STRING,
                PRIMARY KEY (case_id)
            )
        """)
        c.execute("""
            CREATE NODE TABLE IF NOT EXISTS Wallet(
                address STRING,
                chain STRING,
                label STRING,
                type STRING,
                hop INT64,
                balance STRING,
                risk_score DOUBLE,
                last_seen STRING,
                PRIMARY KEY (address)
            )
        """)
        c.execute("""
            CREATE NODE TABLE IF NOT EXISTS VASP(
                name STRING,
                vasp_type STRING,
                country STRING,
                nodal_email STRING,
                is_fiu_compliant BOOLEAN,
                registration STRING,
                last_updated STRING,
                PRIMARY KEY (name)
            )
        """)

        # 2. Relationship tables
        c.execute("""
            CREATE REL TABLE IF NOT EXISTS TRANSFERRED(
                FROM Wallet TO Wallet,
                tx_hash STRING,
                amount DOUBLE,
                asset STRING,
                hop INT64,
                timestamp STRING
            )
        """)
        c.execute("CREATE REL TABLE IF NOT EXISTS CONTAINS_NODE(FROM InvestigationCase TO Wallet)")
        c.execute("CREATE REL TABLE IF NOT EXISTS ATTRIBUTED_TO(FROM InvestigationCase TO VASP)")
        c.execute("CREATE REL TABLE IF NOT EXISTS DEPOSIT_GATEWAY_FOR(FROM Wallet TO VASP)")
        return True
    except Exception as e:
        logger.warning(f"KùzuDB schema initialization notice: {e}")
        return False


def check_kuzu_status() -> Dict[str, Any]:
    """Verify local KùzuDB connectivity and return graph statistics."""
    t0 = time.time()
    try:
        conn = get_kuzu_connection()
        
        # Count wallets and cases
        res_wallets = conn.execute("MATCH (w:Wallet) RETURN count(w) AS cnt")
        wallet_count = res_wallets.get_next()[0] if res_wallets.has_next() else 0

        res_vasps = conn.execute("MATCH (v:VASP) RETURN count(v) AS cnt")
        vasp_count = res_vasps.get_next()[0] if res_vasps.has_next() else 0

        res_cases = conn.execute("MATCH (c:InvestigationCase) RETURN count(c) AS cnt")
        case_count = res_cases.get_next()[0] if res_cases.has_next() else 0

        total_nodes = wallet_count + vasp_count + case_count

        res_rels = conn.execute("MATCH ()-[r:TRANSFERRED]->() RETURN count(r) AS cnt")
        rel_count = res_rels.get_next()[0] if res_rels.has_next() else 0

        latency_ms = round((time.time() - t0) * 1000, 2)
        return {
            "status": "connected",
            "engine": "KùzuDB (Embedded Local Property Graph)",
            "instance_name": "Local-Forensic-Graph",
            "full_name": "KùzuDB Embedded Graph Engine (Zero Rate Limits)",
            "cloud": "Local Storage (Zero Cloud Overhead)",
            "database_path": KUZU_DB_PATH,
            "node_count": total_nodes,
            "wallet_count": wallet_count,
            "vasp_count": vasp_count,
            "case_count": case_count,
            "relationship_count": rel_count,
            "latency_ms": latency_ms,
            "rate_limits": "None (Unlimited Local Storage & Queries)"
        }
    except Exception as e:
        return {
            "status": "error",
            "engine": "KùzuDB",
            "error": str(e),
            "latency_ms": round((time.time() - t0) * 1000, 2)
        }


def sync_trace_to_kuzu(trace_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest a complete cryptographic trace into KùzuDB.
    Creates InvestigationCase, Wallet, VASP nodes and TRANSFERRED relationships.
    """
    conn = get_kuzu_connection()
    case_id = trace_data.get("case_id") or f"TRACE-{int(time.time())}"
    chain = trace_data.get("chain", "ETH")
    suspect_address = trace_data.get("suspect_address", "")
    nearest_vasp = trace_data.get("nearest_vasp", {})
    vasp_name = nearest_vasp.get("name", "Unknown VASP")
    nodes = trace_data.get("nodes", [])
    edges = trace_data.get("edges", [])
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        # 1. Upsert InvestigationCase node
        risk_score = float(trace_data.get("composite_risk_score", 0) or 0)
        conn.execute(
            """
            MERGE (c:InvestigationCase {case_id: $case_id})
            ON CREATE SET c.chain = $chain, c.suspect_address = $suspect_addr, c.risk_score = $risk, c.terminal_vasp = $vasp, c.updated_at = $updated
            ON MATCH SET c.chain = $chain, c.suspect_address = $suspect_addr, c.risk_score = $risk, c.terminal_vasp = $vasp, c.updated_at = $updated
            """,
            {
                "case_id": case_id,
                "chain": chain,
                "suspect_addr": suspect_address,
                "risk": risk_score,
                "vasp": vasp_name,
                "updated": now_str
            }
        )

        # 2. Ingest Wallet nodes and link to Case
        for n in nodes:
            addr = n.get("id") or n.get("address")
            if not addr:
                continue
            w_chain = n.get("chain", chain)
            w_label = n.get("label", "") or ""
            w_type = n.get("type", "wallet") or "wallet"
            w_hop = int(n.get("hop", 0) or 0)
            w_balance = str(n.get("balance", "0"))
            w_risk = float(n.get("risk_score", 0) or 0)

            conn.execute(
                """
                MERGE (w:Wallet {address: $addr})
                ON CREATE SET w.chain = $chain, w.label = $label, w.type = $type, w.hop = $hop, w.balance = $balance, w.risk_score = $risk, w.last_seen = $now
                ON MATCH SET w.chain = $chain, w.label = $label, w.type = $type, w.hop = $hop, w.balance = $balance, w.risk_score = $risk, w.last_seen = $now
                """,
                {
                    "addr": addr,
                    "chain": w_chain,
                    "label": w_label,
                    "type": w_type,
                    "hop": w_hop,
                    "balance": w_balance,
                    "risk": w_risk,
                    "now": now_str
                }
            )

            # Link Case -> Wallet
            try:
                conn.execute(
                    """
                    MATCH (c:InvestigationCase {case_id: $case_id}), (w:Wallet {address: $addr})
                    CREATE (c)-[:CONTAINS_NODE]->(w)
                    """,
                    {"case_id": case_id, "addr": addr}
                )
            except Exception:
                pass  # Ignore if relation already exists

        # 3. Ingest Transaction Relationships
        for e in edges:
            src = e.get("source") or e.get("from")
            tgt = e.get("target") or e.get("to")
            if not src or not tgt:
                continue
            amt_val = float(re.sub(r'[^0-9.]', '', str(e.get("amount", 0))) or 0)
            tx_hash = e.get("tx_hash") or f"tx_{int(time.time())}_{src[:6]}_{tgt[:6]}"
            tx_asset = e.get("asset") or chain
            tx_hop = int(e.get("hop", 1) or 1)

            try:
                conn.execute(
                    """
                    MATCH (s:Wallet {address: $src}), (t:Wallet {address: $tgt})
                    CREATE (s)-[:TRANSFERRED {tx_hash: $tx_hash, amount: $amount, asset: $asset, hop: $hop, timestamp: $now}]->(t)
                    """,
                    {
                        "src": src,
                        "tgt": tgt,
                        "tx_hash": tx_hash,
                        "amount": amt_val,
                        "asset": tx_asset,
                        "hop": tx_hop,
                        "now": now_str
                    }
                )
            except Exception as edge_err:
                logger.debug(f"Edge creation note: {edge_err}")

        # 4. Ingest Terminal VASP Entity and Link
        if vasp_name and nearest_vasp:
            v_type = nearest_vasp.get("vasp_type", "Centralized Exchange")
            v_country = nearest_vasp.get("country", "India")
            v_email = nearest_vasp.get("nodal_email", "compliance@vasp.com")
            v_fiu = bool(nearest_vasp.get("is_indian", True))
            v_reg = nearest_vasp.get("registration", "PMLA Registered")

            conn.execute(
                """
                MERGE (v:VASP {name: $name})
                ON CREATE SET v.vasp_type = $v_type, v.country = $country, v.nodal_email = $email, v.is_fiu_compliant = $fiu, v.registration = $reg, v.last_updated = $now
                ON MATCH SET v.vasp_type = $v_type, v.country = $country, v.nodal_email = $email, v.is_fiu_compliant = $fiu, v.registration = $reg, v.last_updated = $now
                """,
                {
                    "name": vasp_name,
                    "v_type": v_type,
                    "country": v_country,
                    "email": v_email,
                    "fiu": v_fiu,
                    "reg": v_reg,
                    "now": now_str
                }
            )

            try:
                conn.execute(
                    """
                    MATCH (c:InvestigationCase {case_id: $case_id}), (v:VASP {name: $name})
                    CREATE (c)-[:ATTRIBUTED_TO]->(v)
                    """,
                    {"case_id": case_id, "name": vasp_name}
                )
            except Exception:
                pass

            deposit_addr = nearest_vasp.get("deposit_address")
            if deposit_addr:
                try:
                    conn.execute(
                        """
                        MATCH (w:Wallet {address: $deposit_addr}), (v:VASP {name: $name})
                        CREATE (w)-[:DEPOSIT_GATEWAY_FOR]->(v)
                        """,
                        {"deposit_addr": deposit_addr, "name": vasp_name}
                    )
                except Exception:
                    pass

        return {
            "success": True,
            "engine": "KùzuDB",
            "case_id": case_id,
            "nodes_ingested": len(nodes),
            "edges_ingested": len(edges),
            "vasp_attributed": vasp_name,
            "cloud_status": "synced_to_local_kuzu_graph"
        }
    except Exception as e:
        logger.error(f"KùzuDB sync error: {e}")
        return {"success": False, "error": str(e), "engine": "KùzuDB"}


def execute_cypher(query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute Cypher queries against local KùzuDB engine.
    Returns column metadata, record count, serialized rows, and execution latency.
    """
    conn = get_kuzu_connection()
    params = params or {}
    t0 = time.time()
    try:
        result = conn.execute(query, params)
        cols = result.get_column_names()
        rows = []
        count = 0
        while result.has_next() and count < 100:
            raw_row = result.get_next()
            row_dict = {}
            for i, col in enumerate(cols):
                val = raw_row[i]
                row_dict[col] = str(val) if val is not None else None
            rows.append(row_dict)
            count += 1

        return {
            "success": True,
            "engine": "KùzuDB",
            "columns": cols,
            "count": len(rows),
            "data": rows,
            "execution_ms": round((time.time() - t0) * 1000, 2)
        }
    except Exception as e:
        return {
            "success": False,
            "engine": "KùzuDB",
            "error": str(e),
            "execution_ms": round((time.time() - t0) * 1000, 2)
        }


def get_subgraph(case_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    """Retrieve graph nodes and edges formatted for Cytoscape.js visualization."""
    conn = get_kuzu_connection()
    try:
        # Get wallets
        res_wallets = conn.execute(
            "MATCH (w:Wallet) RETURN w.address, w.chain, w.label, w.type, w.hop, w.risk_score LIMIT $limit",
            {"limit": limit}
        )
        nodes = []
        while res_wallets.has_next():
            row = res_wallets.get_next()
            nodes.append({
                "data": {
                    "id": row[0],
                    "address": row[0],
                    "chain": row[1],
                    "label": row[2] or row[0][:8],
                    "type": row[3],
                    "hop": row[4],
                    "risk_score": row[5]
                }
            })

        # Get transfers
        res_transfers = conn.execute(
            """
            MATCH (s:Wallet)-[r:TRANSFERRED]->(t:Wallet)
            RETURN s.address, t.address, r.tx_hash, r.amount, r.asset, r.hop
            LIMIT $limit
            """,
            {"limit": limit}
        )
        edges = []
        while res_transfers.has_next():
            row = res_transfers.get_next()
            edges.append({
                "data": {
                    "id": row[2] or f"{row[0][:6]}_{row[1][:6]}",
                    "source": row[0],
                    "target": row[1],
                    "tx_hash": row[2],
                    "amount": row[3],
                    "asset": row[4],
                    "hop": row[5]
                }
            })

        return {"nodes": nodes, "edges": edges, "count_nodes": len(nodes), "count_edges": len(edges)}
    except Exception as e:
        logger.error(f"Failed to fetch subgraph from Kùzu: {e}")
        return {"nodes": [], "edges": [], "error": str(e)}
