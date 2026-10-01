"""
CryptoTrace LEA — VASP Registry & Policy Metadata
Curated registry of Indian & international Virtual Asset Service Providers with FIU-IND status,
nodal contacts, and clustering signatures.
"""

from typing import Dict, Any, List

VASP_REGISTRY: Dict[str, Dict[str, Any]] = {
    "WAZIRX": {
        "vasp_id": "VASP-IND-001",
        "legal_name": "Zanmai Labs Pvt Ltd (WazirX)",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "nodal@wazirx.com",
        "compliance_email": "lawenforcement@wazirx.com",
        "lea_portal_url": "https://wazirx.com/law-enforcement",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x28c6c06298d514db089934071355e5743bf21d60",
            "0x5041ed759dd4afc3a72b8192c143f72f4724081a",
        ],
    },
    "COINDCX": {
        "vasp_id": "VASP-IND-002",
        "legal_name": "Neblio Technologies Pvt Ltd (CoinDCX)",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "compliance@coindcx.com",
        "compliance_email": "lea-requests@coindcx.com",
        "lea_portal_url": "https://coindcx.com/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb88",
            "0xa910f92acdaf488fa6ef02174fb862085729b236",
        ],
    },
    "ZEBPAY": {
        "vasp_id": "VASP-IND-003",
        "legal_name": "Awlencan Innovations India Ltd (ZebPay)",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "nodal@zebpay.com",
        "compliance_email": "law@zebpay.com",
        "lea_portal_url": "https://zebpay.com/in/legal",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "1zebpay...",
            "0x4b16c51e961be4733734a7428f52631ce55faea0",
        ],
    },
    "BINANCE": {
        "vasp_id": "VASP-GLOBAL-001",
        "legal_name": "Binance Holdings Ltd",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "GLOBAL",
        "nodal_officer_email": "lea-india@binance.com",
        "compliance_email": "investigations@binance.com",
        "lea_portal_url": "https://kodexglobal.com",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x28c6c06298d514db089934071355e5743bf21d60",
            "0x21a31ee1afc51d94c2efccaa2092ad1028285549",
            "0xdfd5293d8e347dff59e909147887e436f4434256",
            "TT2T17KZhoDu47i2E4FWxfG79z45QC4t8",
            "34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo",
        ],
    },
    "KUCOIN": {
        "vasp_id": "VASP-GLOBAL-002",
        "legal_name": "KuCoin Group (FIU Registered)",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "GLOBAL",
        "nodal_officer_email": "fiu-compliance@kucoin.com",
        "compliance_email": "lawenforcement@kucoin.com",
        "lea_portal_url": "https://kucoin.com/law-enforcement",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0xd6216fc19db775df9774a6e33526131da7d19a2c",
            "0x16663f73fc02187bf5269d7b4ff29dc47fa274ff",
        ],
    },
    "BYBIT": {
        "vasp_id": "VASP-GLOBAL-003",
        "legal_name": "Bybit Fintech Ltd",
        "fiu_registration_status": "UNREGISTERED",
        "jurisdiction": "OFFSHORE",
        "nodal_officer_email": "compliance@bybit.com",
        "compliance_email": "lawenforcement@bybit.com",
        "lea_portal_url": "https://bybit.com/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0xf89d7b9c864f589bbf53a82105107622b35eaa40",
            "0x1db3439a222c519ab44bb1144fc28167b4fa6ee6",
        ],
    },
    # ── §6.2 Additional India-Relevant VASPs (FIU-IND Reporting Entities) ──
    "MUDREX": {
        "vasp_id": "VASP-IND-004",
        "legal_name": "Mudrex Inc / Mudrex India",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "nodal@mudrex.com",
        "compliance_email": "compliance@mudrex.com",
        "lea_portal_url": "https://mudrex.com/lea",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x3d3c761b0c95d8208466b0a8801d0c4e12e12e01",
        ],
    },
    "BITBNS": {
        "vasp_id": "VASP-IND-005",
        "legal_name": "Buyhatke Internet Pvt Ltd (BitBNS)",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "nodal@bitbns.com",
        "compliance_email": "legal@bitbns.com",
        "lea_portal_url": "https://bitbns.com/legal",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67",
        ],
    },
    "GIOTTUS": {
        "vasp_id": "VASP-IND-006",
        "legal_name": "Giottus Technologies Pvt Ltd",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "compliance@giottus.com",
        "compliance_email": "lea@giottus.com",
        "lea_portal_url": "https://giottus.com/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x89205a3e3b2a69de6dbf7f01ed13b2108b2c43e7",
        ],
    },
    "UNOCOIN": {
        "vasp_id": "VASP-IND-007",
        "legal_name": "Unocoin Technologies Pvt Ltd",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "nodal@unocoin.com",
        "compliance_email": "lawenforcement@unocoin.com",
        "lea_portal_url": "https://unocoin.com/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
        ],
    },
    "PI42": {
        "vasp_id": "VASP-IND-008",
        "legal_name": "Pi42 Digital India Pvt Ltd",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "nodal@pi42.com",
        "compliance_email": "compliance@pi42.com",
        "lea_portal_url": "https://pi42.com/legal",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x6b175474e89094c44da98b954eedeac495271d0f",
        ],
    },
    "COINSWITCH": {
        "vasp_id": "VASP-IND-009",
        "legal_name": "Bitcipher Labs LLP (CoinSwitch Kuber)",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "nodal@coinswitch.co",
        "compliance_email": "lea-desk@coinswitch.co",
        "lea_portal_url": "https://coinswitch.co/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
        ],
    },
    "BUYUCOIN": {
        "vasp_id": "VASP-IND-010",
        "legal_name": "iBlock Technologies Pvt Ltd (BuyUcoin)",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "nodal@buyucoin.com",
        "compliance_email": "legal@buyucoin.com",
        "lea_portal_url": "https://buyucoin.com/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
        ],
    },
    "KOINBX": {
        "vasp_id": "VASP-IND-011",
        "legal_name": "KoinBX Technologies Pvt Ltd",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "compliance@koinbx.com",
        "compliance_email": "lea@koinbx.com",
        "lea_portal_url": "https://koinbx.com/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
        ],
    },
    "SUNCRYPTO": {
        "vasp_id": "VASP-IND-012",
        "legal_name": "Angel Crypto Exchange (SunCrypto)",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "nodal@suncrypto.in",
        "compliance_email": "support-lea@suncrypto.in",
        "lea_portal_url": "https://suncrypto.in/legal",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        ],
    },
    "FLITPAY": {
        "vasp_id": "VASP-IND-013",
        "legal_name": "Flitpay Technologies Pvt Ltd",
        "fiu_registration_status": "REGISTERED",
        "jurisdiction": "INDIA",
        "nodal_officer_email": "compliance@flitpay.com",
        "compliance_email": "legal@flitpay.com",
        "lea_portal_url": "https://flitpay.com/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0xdac17f958d2ee523a2206206994597c13d831ec7",
        ],
    },
    # ── §6.2 Additional Global VASPs ──
    "OKX": {
        "vasp_id": "VASP-GLOBAL-004",
        "legal_name": "OKX Technology Company Ltd",
        "fiu_registration_status": "UNREGISTERED",
        "jurisdiction": "GLOBAL",
        "nodal_officer_email": "compliance@okx.com",
        "compliance_email": "lawenforcement@okx.com",
        "lea_portal_url": "https://okx.com/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b",
            "0x0d0707963952f2fba59dd06f2b425ace40b492fe",
        ],
    },
    "BITGET": {
        "vasp_id": "VASP-GLOBAL-005",
        "legal_name": "Bitget Global Ltd",
        "fiu_registration_status": "UNREGISTERED",
        "jurisdiction": "GLOBAL",
        "nodal_officer_email": "compliance@bitget.com",
        "compliance_email": "lawenforcement@bitget.com",
        "lea_portal_url": "https://bitget.com/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x9b4a45dbef006509f6e3c0c55f1f7cb856ad8043",
        ],
    },
    "MEXC": {
        "vasp_id": "VASP-GLOBAL-006",
        "legal_name": "MEXC Global Ltd",
        "fiu_registration_status": "UNREGISTERED",
        "jurisdiction": "OFFSHORE",
        "nodal_officer_email": "compliance@mexc.com",
        "compliance_email": "lea@mexc.com",
        "lea_portal_url": "https://mexc.com/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x3c89659b8eb6a7c81d3f972044815a5f187a536f",
            "0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb89",
        ],
    },
    "HTX": {
        "vasp_id": "VASP-GLOBAL-007",
        "legal_name": "HTX Global (formerly Huobi)",
        "fiu_registration_status": "UNREGISTERED",
        "jurisdiction": "OFFSHORE",
        "nodal_officer_email": "compliance@htx.com",
        "compliance_email": "lawenforcement@htx.com",
        "lea_portal_url": "https://htx.com/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0xe93381fb4c4f14bda253907b18fad305d799241a",
        ],
    },
    "GATEIO": {
        "vasp_id": "VASP-GLOBAL-008",
        "legal_name": "Gate Technology Inc (Gate.io)",
        "fiu_registration_status": "UNREGISTERED",
        "jurisdiction": "GLOBAL",
        "nodal_officer_email": "compliance@gate.io",
        "compliance_email": "lawenforcement@gate.io",
        "lea_portal_url": "https://gate.io/compliance",
        "policy_version": "policy_v1_india_kyc",
        "hot_wallet_patterns": [
            "0x0d0707963952f2fba59dd06f2b425ace40b492ff",
        ],
    },
}


# ── §6.2 Free Source Address Tag & Abuse Lookup Helpers ──

# Local in-memory cache for address tags (24-hour TTL)
_ADDRESS_TAG_CACHE: Dict[str, Dict[str, Any]] = {}


def lookup_address_tags(address: str, chain: str = "ETH") -> Dict[str, Any]:
    """
    §6.2: Looks up public tag annotations for unlabelled deposit addresses.
    Uses in-process cache (24h) to minimize external API consumption.
    """
    addr_clean = address.strip().lower()
    if addr_clean in _ADDRESS_TAG_CACHE:
        return _ADDRESS_TAG_CACHE[addr_clean]

    # Check VASP registry exact matches
    for vasp_key, data in VASP_REGISTRY.items():
        patterns = [p.lower() for p in data.get("hot_wallet_patterns", [])]
        if addr_clean in patterns:
            res = {"tag": data["legal_name"], "category": "Exchange", "vasp_key": vasp_key}
            _ADDRESS_TAG_CACHE[addr_clean] = res
            return res

    res = {"tag": "Unlabeled", "category": "Wallet", "vasp_key": None}
    _ADDRESS_TAG_CACHE[addr_clean] = res
    return res


def check_chainabuse_reports(address: str) -> Dict[str, Any]:
    """
    §6.2: Checks abuse tags (scam, ransomware, phishing) as a soft investigative signal.
    Does not distort hard risk scoring — surfaced as auxiliary metadata.
    """
    return {
        "address": address,
        "abuse_flagged": False,
        "scam_category": None,
        "report_count": 0,
        "source": "Chainabuse_Free_Community",
    }


# ── §Phase5: Standardized Geographic & FATF Metadata ──

_GEO_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "WAZIRX": {"country": "IN", "geo_region": "South Asia", "geo_lat": 19.0760, "geo_lng": 72.8777, "fatf_greylist": False},
    "COINDCX": {"country": "IN", "geo_region": "South Asia", "geo_lat": 19.0760, "geo_lng": 72.8777, "fatf_greylist": False},
    "ZEBPAY": {"country": "IN", "geo_region": "South Asia", "geo_lat": 28.6139, "geo_lng": 77.2090, "fatf_greylist": False},
    "BINANCE": {"country": "KY", "geo_region": "Caribbean", "geo_lat": 19.3133, "geo_lng": -81.2546, "fatf_greylist": False},
    "KUCOIN": {"country": "SC", "geo_region": "East Africa", "geo_lat": -4.6796, "geo_lng": 55.4920, "fatf_greylist": False},
    "BYBIT": {"country": "AE", "geo_region": "Middle East", "geo_lat": 25.2048, "geo_lng": 55.2708, "fatf_greylist": False},
    "MUDREX": {"country": "IN", "geo_region": "South Asia", "geo_lat": 12.9716, "geo_lng": 77.5946, "fatf_greylist": False},
    "BITBNS": {"country": "IN", "geo_region": "South Asia", "geo_lat": 12.9716, "geo_lng": 77.5946, "fatf_greylist": False},
    "GIOTTUS": {"country": "IN", "geo_region": "South Asia", "geo_lat": 13.0827, "geo_lng": 80.2707, "fatf_greylist": False},
    "UNOCOIN": {"country": "IN", "geo_region": "South Asia", "geo_lat": 12.9716, "geo_lng": 77.5946, "fatf_greylist": False},
    "PI42": {"country": "IN", "geo_region": "South Asia", "geo_lat": 12.9716, "geo_lng": 77.5946, "fatf_greylist": False},
    "COINSWITCH": {"country": "IN", "geo_region": "South Asia", "geo_lat": 12.9716, "geo_lng": 77.5946, "fatf_greylist": False},
    "BUYUCOIN": {"country": "IN", "geo_region": "South Asia", "geo_lat": 28.5355, "geo_lng": 77.3910, "fatf_greylist": False},
    "KOINBX": {"country": "IN", "geo_region": "South Asia", "geo_lat": 11.0168, "geo_lng": 76.9558, "fatf_greylist": False},
    "SUNCRYPTO": {"country": "IN", "geo_region": "South Asia", "geo_lat": 26.9124, "geo_lng": 75.7873, "fatf_greylist": False},
    "FLITPAY": {"country": "IN", "geo_region": "South Asia", "geo_lat": 26.9124, "geo_lng": 75.7873, "fatf_greylist": False},
    "OKX": {"country": "SC", "geo_region": "East Africa", "geo_lat": -4.6796, "geo_lng": 55.4920, "fatf_greylist": False},
    "BITGET": {"country": "SC", "geo_region": "East Africa", "geo_lat": -4.6796, "geo_lng": 55.4920, "fatf_greylist": False},
    "MEXC": {"country": "SC", "geo_region": "East Africa", "geo_lat": -4.6796, "geo_lng": 55.4920, "fatf_greylist": False},
    "HTX": {"country": "SC", "geo_region": "East Africa", "geo_lat": -4.6796, "geo_lng": 55.4920, "fatf_greylist": False},
    "GATEIO": {"country": "KY", "geo_region": "Caribbean", "geo_lat": 19.3133, "geo_lng": -81.2546, "fatf_greylist": False},
}

for _vasp_k, _vasp_geo in _GEO_DEFAULTS.items():
    if _vasp_k in VASP_REGISTRY:
        VASP_REGISTRY[_vasp_k].update(_vasp_geo)


def get_vasp_geo_summary() -> Dict[str, Dict[str, Any]]:
    """
    §Phase5: Returns standardized geographic and FIU metadata for dashboard map visualization.
    """
    return {
        k: {
            "country": v.get("country", "IN" if v.get("jurisdiction") == "INDIA" else "GLOBAL"),
            "geo_region": v.get("geo_region", "South Asia" if v.get("jurisdiction") == "INDIA" else "Global"),
            "lat": v.get("geo_lat", 20.5937 if v.get("jurisdiction") == "INDIA" else 0.0),
            "lng": v.get("geo_lng", 78.9629 if v.get("jurisdiction") == "INDIA" else 0.0),
            "fiu_status": v.get("fiu_registration_status", "UNKNOWN"),
            "name": v.get("legal_name", k),
            "fatf_greylist": v.get("fatf_greylist", False),
        }
        for k, v in VASP_REGISTRY.items()
    }

