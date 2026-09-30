"""
TraceX — Graph Forensics Engine
Unified Graph Interface: Defaults to local embedded KùzuDB (Zero Rate Limits, High Performance)
with optional fallback to cloud-hosted Neo4j Aura if explicitly requested.
"""

import os
import time
import logging
import re
from typing import Dict, Any, List, Optional
from engine.kuzu_engine import (
    check_kuzu_status,
    sync_trace_to_kuzu,
    execute_cypher as kuzu_execute_cypher,
    init_kuzu_schema,
    get_subgraph as kuzu_get_subgraph
)

logger = logging.getLogger("tracex.graph")

GRAPH_ENGINE = os.getenv("GRAPH_ENGINE", "kuzu").lower()

# Legacy Neo4j Credentials (Optional fallback)
NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
AURA_INSTANCEID = os.getenv("AURA_INSTANCEID", "local-kuzu")
AURA_INSTANCENAME = os.getenv("AURA_INSTANCENAME", "KùzuDB-Forensic-Graph")
VINI_FULL_NAME = os.getenv("VINI_FULL_NAME", "Virtual Asset Investigation & Network Intelligence (KùzuDB Local)")

_neo4j_driver = None


def get_driver():
    """Obtain Neo4j driver only if explicitly configured in neo4j mode."""
    global _neo4j_driver
    if GRAPH_ENGINE != "neo4j":
        return None
    if _neo4j_driver is not None:
        return _neo4j_driver
    if not NEO4J_URI or not NEO4J_PASSWORD:
        return None
    try:
        from neo4j import GraphDatabase
        _neo4j_driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
            max_connection_lifetime=30 * 60,
            max_connection_pool_size=50,
            connection_acquisition_timeout=15.0
        )
        return _neo4j_driver
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j driver: {e}")
        return None


def init_neo4j_schema() -> bool:
    """Initialize graph schema constraints and tables."""
    if GRAPH_ENGINE != "neo4j":
        return init_kuzu_schema()

    driver = get_driver()
    if not driver:
        # Fall back to KùzuDB schema if Neo4j driver is unavailable
        return init_kuzu_schema()
    try:
        with driver.session() as session:
            session.run("CREATE CONSTRAINT wallet_addr_unique IF NOT EXISTS FOR (w:Wallet) REQUIRE w.address IS UNIQUE")
            session.run("CREATE CONSTRAINT vasp_name_unique IF NOT EXISTS FOR (v:VASP) REQUIRE v.name IS UNIQUE")
            session.run("CREATE CONSTRAINT case_id_unique IF NOT EXISTS FOR (c:Case) REQUIRE c.case_id IS UNIQUE")
        return True
    except Exception as e:
        logger.warning(f"Neo4j schema initialization warning: {e}. Defaulting to KùzuDB.")
        return init_kuzu_schema()


def check_neo4j_status() -> Dict[str, Any]:
    """Verify connectivity and fetch graph telemetry (defaults to KùzuDB)."""
    if GRAPH_ENGINE != "neo4j":
        return check_kuzu_status()

    driver = get_driver()
    if not driver:
        # Gracefully return Kùzu telemetry if Neo4j is offline or not configured
        kuzu_stat = check_kuzu_status()
        kuzu_stat["neo4j_fallback"] = "Neo4j driver inactive; active on local KùzuDB"
        return kuzu_stat

    t0 = time.time()
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            res_nodes = session.run("MATCH (n) RETURN count(n) AS node_count")
            node_count = res_nodes.single()["node_count"]
            res_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS rel_count")
            rel_count = res_rels.single()["rel_count"]

        latency_ms = round((time.time() - t0) * 1000, 1)
        return {
            "status": "connected",
            "engine": "Neo4j Aura Cloud",
            "instance_name": AURA_INSTANCENAME,
            "full_name": VINI_FULL_NAME,
            "instance_id": AURA_INSTANCEID,
            "uri": NEO4J_URI.split("@")[-1],
            "node_count": node_count,
            "relationship_count": rel_count,
            "latency_ms": latency_ms,
            "cloud": "Neo4j Aura Cloud",
        }
    except Exception as e:
        logger.warning(f"Neo4j connectivity failed ({e}). Returning local KùzuDB status.")
        kuzu_stat = check_kuzu_status()
        kuzu_stat["neo4j_error"] = str(e)
        return kuzu_stat


def sync_trace_to_neo4j(trace_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest a complete cryptographic trace into the active graph engine.
    Routes to KùzuDB by default, or Neo4j if configured.
    """
    if GRAPH_ENGINE != "neo4j":
        return sync_trace_to_kuzu(trace_data)

    driver = get_driver()
    if not driver:
        return sync_trace_to_kuzu(trace_data)

    case_id = trace_data.get("case_id") or f"TRACE-{int(time.time())}"
    chain = trace_data.get("chain", "ETH")
    suspect_address = trace_data.get("suspect_address", "")
    nearest_vasp = trace_data.get("nearest_vasp", {})
    vasp_name = nearest_vasp.get("name", "Unknown VASP")
    nodes = trace_data.get("nodes", [])
    edges = trace_data.get("edges", [])

    try:
        with driver.session() as session:
            session.run("""
                MERGE (c:Case {case_id: $case_id})
                SET c.chain = $chain,
                    c.suspect_address = $suspect_address,
                    c.updated_at = datetime(),
                    c.risk_score = $risk_score,
                    c.terminal_vasp = $vasp_name
            """, {
                "case_id": case_id,
                "chain": chain,
                "suspect_address": suspect_address,
                "risk_score": trace_data.get("composite_risk_score", 0),
                "vasp_name": vasp_name
            })

            for n in nodes:
                addr = n.get("id") or n.get("address")
                if not addr:
                    continue
                session.run("""
                    MERGE (w:Wallet {address: $address})
                    SET w.chain = $chain,
                        w.label = $label,
                        w.type = $type,
                        w.hop = $hop,
                        w.balance = $balance,
                        w.risk_score = $risk_score,
                        w.last_seen = datetime()
                    WITH w
                    MATCH (c:Case {case_id: $case_id})
                    MERGE (c)-[:CONTAINS_NODE]->(w)
                """, {
                    "address": addr,
                    "chain": chain,
                    "label": n.get("label", ""),
                    "type": n.get("type", "wallet"),
                    "hop": n.get("hop", 0),
                    "balance": str(n.get("balance", "0")),
                    "risk_score": n.get("risk_score", 0),
                    "case_id": case_id
                })

            for e in edges:
                src = e.get("source") or e.get("from")
                tgt = e.get("target") or e.get("to")
                if not src or not tgt:
                    continue
                session.run("""
                    MATCH (s:Wallet {address: $src})
                    MATCH (t:Wallet {address: $tgt})
                    MERGE (s)-[r:TRANSFERRED {tx_hash: $tx_hash}]->(t)
                    SET r.amount = $amount,
                        r.asset = $asset,
                        r.hop = $hop,
                        r.timestamp = datetime()
                """, {
                    "src": src,
                    "tgt": tgt,
                    "tx_hash": e.get("tx_hash") or f"tx_{int(time.time())}_{src[:6]}_{tgt[:6]}",
                    "amount": float(re.sub(r'[^0-9.]', '', str(e.get("amount", 0))) or 0),
                    "asset": e.get("asset") or chain,
                    "hop": int(e.get("hop", 1))
                })

            if vasp_name and nearest_vasp:
                deposit_addr = nearest_vasp.get("deposit_address")
                session.run("""
                    MERGE (v:VASP {name: $name})
                    SET v.vasp_type = $vasp_type,
                        v.country = $country,
                        v.nodal_email = $nodal_email,
                        v.is_fiu_compliant = $is_fiu_compliant,
                        v.registration = $registration,
                        v.last_updated = datetime()
                    WITH v
                    MATCH (c:Case {case_id: $case_id})
                    MERGE (c)-[:ATTRIBUTED_TO]->(v)
                """, {
                    "name": vasp_name,
                    "vasp_type": nearest_vasp.get("vasp_type", "Centralized Exchange"),
                    "country": nearest_vasp.get("country", "India"),
                    "nodal_email": nearest_vasp.get("nodal_email", "compliance@vasp.com"),
                    "is_fiu_compliant": bool(nearest_vasp.get("is_indian", True)),
                    "registration": nearest_vasp.get("registration", "PMLA Registered"),
                    "case_id": case_id
                })

                if deposit_addr:
                    session.run("""
                        MATCH (w:Wallet {address: $deposit_addr})
                        MATCH (v:VASP {name: $name})
                        MERGE (w)-[:DEPOSIT_GATEWAY_FOR]->(v)
                    """, {
                        "deposit_addr": deposit_addr,
                        "name": vasp_name
                    })

        return {
            "success": True,
            "engine": "Neo4j Aura Cloud",
            "case_id": case_id,
            "nodes_ingested": len(nodes),
            "edges_ingested": len(edges),
            "vasp_attributed": vasp_name,
            "cloud_status": "synced_to_neo4j_aura"
        }
    except Exception as e:
        logger.error(f"Neo4j sync error: {e}. Falling back to KùzuDB.")
        return sync_trace_to_kuzu(trace_data)


def execute_cypher(query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute raw Cypher query against the active graph engine."""
    if GRAPH_ENGINE != "neo4j":
        return kuzu_execute_cypher(query, params)

    driver = get_driver()
    if not driver:
        return kuzu_execute_cypher(query, params)

    params = params or {}
    t0 = time.time()
    try:
        with driver.session() as session:
            result = session.run(query, params)
            keys = result.keys()
            records = []
            for record in result:
                row = {}
                for k in keys:
                    val = record[k]
                    if hasattr(val, "id") and hasattr(val, "items"):
                        row[k] = dict(val.items())
                    elif hasattr(val, "nodes") and hasattr(val, "relationships"):
                        row[k] = f"Path(nodes={len(val.nodes)}, rels={len(val.relationships)})"
                    else:
                        row[k] = str(val)
                records.append(row)

        return {
            "success": True,
            "engine": "Neo4j Aura",
            "columns": list(keys),
            "count": len(records),
            "data": records[:100],
            "execution_ms": round((time.time() - t0) * 1000, 1)
        }
    except Exception as e:
        return {
            "success": False,
            "engine": "Neo4j Aura",
            "error": str(e),
            "execution_ms": round((time.time() - t0) * 1000, 1)
        }