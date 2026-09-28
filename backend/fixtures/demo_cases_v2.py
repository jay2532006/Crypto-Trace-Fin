"""
CryptoTrace LEA — Dedicated Test & Demonstration Fixtures (SIH 26183)
All fixture cases are strictly tagged with demo_data=True and source_origin='DEMO_CASE_SIH26183'.
These are reproducible deterministic scenarios for testing and evaluation walkthroughs.
"""

from typing import List, Dict, Any

CRYPTO_TRACE_FIXTURES: List[Dict[str, Any]] = [
    {
        "case_id": "CR-2026-MULE-IND-01",
        "demo_data": True,
        "source_origin": "DEMO_CASE_SIH26183",
        "title": "NCRP Case: High-Impact Cyber Mule Network (Fake Investment Fraud)",
        "chain": "TRON",
        "suspect_wallet": "TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6",
        "reported_amount": 54200.0,
        "reported_asset": "USDT",
        "crime_category": "Investment Syndicate Fraud (NCRP Portal)",
        "documented_pattern": (
            "Victim reported fraudulent transfer of 54,200 USDT. Funds passed through 3 distinct intermediary "
            "single-in/single-out pass-through mule wallets within 45 minutes, consolidating into a verified WazirX / Binance deposit cluster."
        ),
        "expected_typology": "MULE_NETWORK",
        "expected_vasp": "WAZIRX",
        "expected_vasp_confidence": "HIGH",
        "expected_recovery_eligibility": "eligible",
        "investigating_officer": "Inspector R. Sharma",
        "unit": "Cyber Crime Police Station, Mumbai",
    },
    {
        "case_id": "CR-2026-MIXER-BOUND-02",
        "demo_data": True,
        "source_origin": "DEMO_CASE_SIH26183",
        "title": "Ransomware Extortion Corridor with Tornado Cash Boundary",
        "chain": "ETH",
        "suspect_wallet": "0x1da5821544e25c636c1417ba96ade4cf6d2f9b5a",
        "reported_amount": 30.0,
        "reported_asset": "ETH",
        "crime_category": "Hospital Ransomware Attack",
        "documented_pattern": (
            "Extortion payout in ETH routed through an intermediary address directly into Tornado Cash 10 ETH pool. "
            "Evaluates strict +14,400s search window and enforces fixed 0.25 confidence ceiling on mixer exit leads."
        ),
        "expected_typology": "MIXER_BOUNDARY",
        "expected_vasp": "UNKNOWN",
        "expected_vasp_confidence": "LOW",
        "expected_recovery_eligibility": "ineligible",
        "investigating_officer": "DSP A. Patil",
        "unit": "State Cyber Cell",
    },
    {
        "case_id": "CR-2026-BRIDGE-XCHAIN-03",
        "demo_data": True,
        "source_origin": "DEMO_CASE_SIH26183",
        "title": "Cross-Chain Bridge Layering (EVM Ethereum to TRON)",
        "chain": "ETH",
        "suspect_wallet": "0x4b16c51e961be4733734a7428f52631ce55faea0",
        "reported_amount": 75000.0,
        "reported_asset": "USDT",
        "crime_category": "DEX Bridge Arbitrage Theft",
        "documented_pattern": (
            "Cross-chain fund routing from Ethereum ERC-20 USDT across a bridge contract to TRON TRC-20 USDT. "
            "Distinguishes PROVEN smart contract bridge events from HEURISTIC correlation."
        ),
        "expected_typology": "RAPID_HOP",
        "expected_vasp": "COINDCX",
        "expected_vasp_confidence": "MEDIUM",
        "expected_recovery_eligibility": "eligible",
        "investigating_officer": "Inspector S. Mehta",
        "unit": "I4C Special Operations",
    },
    {
        "case_id": "CR-2026-BRIDGE-XCHAIN-04",
        "demo_data": True,
        "source_origin": "DEMO_CASE_SIH26183",
        "title": "Cross-Chain Stargate Liquidity Bridge Routing (ETH -> Polygon)",
        "chain": "ETH",
        "suspect_wallet": "0x296f55f7730e201b1bc283b474a005b1e63ccffe",
        "reported_amount": 68000.0,
        "reported_asset": "USDT",
        "crime_category": "Decentralized Finance Siphoning",
        "documented_pattern": (
            "Cross-chain transfer originating on Ethereum mainnet, passing through Stargate Router bridge contract "
            "(0x8731d54e9d02c286767d56ac03e8037c07e01e98) with deterministic LayerZero event emission into Polygon."
        ),
        "expected_typology": "CROSS_CHAIN_BRIDGE",
        "expected_vasp": "COINDCX",
        "expected_vasp_confidence": "HIGH",
        "expected_recovery_eligibility": "eligible",
        "investigating_officer": "Inspector V. Nair",
        "unit": "Cyber Crime Division, Bengaluru",
    },
    {
        "case_id": "CR-2026-OFAC-SDN-05",
        "demo_data": True,
        "source_origin": "DEMO_CASE_SIH26183",
        "title": "State-Sponsored APT Cyber Theft (Lazarus Group OFAC SDN Designation)",
        "chain": "ETH",
        "suspect_wallet": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
        "reported_amount": 125.0,
        "reported_asset": "ETH",
        "crime_category": "Critical Infrastructure Cyber Extortion",
        "documented_pattern": (
            "On-chain asset trace directly intersects official US Treasury OFAC Specially Designated Nationals (SDN) "
            "digital currency entry (Lazarus Group Ronin Bridge exploiter, SDN ID 34991). Immediate mandatory asset freeze."
        ),
        "expected_typology": "OFAC_SANCTION_HIT",
        "expected_vasp": "UNKNOWN",
        "expected_vasp_confidence": "LOW",
        "expected_recovery_eligibility": "ineligible",
        "investigating_officer": "Special Director A. Sengupta",
        "unit": "National Cyber Threat Analysis Centre",
    },
    {
        "case_id": "CR-2026-MULE-FANIN-06",
        "demo_data": True,
        "source_origin": "DEMO_CASE_SIH26183",
        "title": "Multi-Victim Telegram Task Scam Syndicate (4-to-1 Mule Fan-In)",
        "chain": "ETH",
        "suspect_wallet": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
        "reported_amount": 110000.0,
        "reported_asset": "USDT",
        "crime_category": "Multi-Complainant Coordinated Fraud",
        "documented_pattern": (
            "Consolidation of defrauded proceeds from 4 separate victim reports into a centralized intermediary "
            "layering wallet before routing into an FIU-IND registered domestic exchange cluster."
        ),
        "expected_typology": "MULE_NETWORK",
        "expected_vasp": "WAZIRX",
        "expected_vasp_confidence": "HIGH",
        "expected_recovery_eligibility": "eligible",
        "investigating_officer": "ACP K. Deshmukh",
        "unit": "Economic Offences Wing, Pune",
    },
]


def get_crypto_trace_fixtures() -> List[Dict[str, Any]]:
    return CRYPTO_TRACE_FIXTURES
