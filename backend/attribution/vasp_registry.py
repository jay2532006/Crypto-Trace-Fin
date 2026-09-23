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
}
