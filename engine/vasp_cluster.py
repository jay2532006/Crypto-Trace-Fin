"""
VASP Cluster Database â€” Known Exchange Deposit Patterns & Hot Wallet Addresses
Used by the VASP Attribution Engine to identify nearest VASP in transaction graph.
"""

VASP_CLUSTERS = {
    # â”€â”€â”€ INDIAN VASPs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "WazirX": {
        "country": "India",
        "registration": "PMLA Registered - FIU-IND (Registration Ref: VDA-004)",
        "vasp_type": "Centralized Exchange",
        "chains": ["BTC", "ETH", "TRON", "BNB"],
        "nodal_email": "compliance@wazirx.com",
        "nodal_officer": "Compliance Officer",
        "legal_address": "WazirX Trade Private Limited, Mumbai, Maharashtra, India",
        "hot_wallet_patterns": [],
        "deposit_address_heuristics": {"address_reuse": "high", "volume_usd_min": 10},
        "risk_level": "MEDIUM",
        "freeze_authority": "FIU-IND / PMLA Adjudicating Authority",
        "provenance": "FIU-IND Reporting Entity Registry",
        "last_verified": "2026-09-04",
    },
    "CoinDCX": {
        "country": "India",
        "registration": "PMLA Registered - FIU-IND",
        "vasp_type": "Centralized Exchange",
        "chains": ["BTC", "ETH", "TRON", "BNB", "POLYGON"],
        "nodal_email": "legal@coindcx.com",
        "nodal_officer": "Chief Compliance Officer",
        "legal_address": "CoinDCX, Siechem Technologies Pvt Ltd, Mumbai, India",
        "hot_wallet_patterns": [],
        "deposit_address_heuristics": {"address_reuse": "low", "volume_usd_min": 5},
        "risk_level": "MEDIUM",
        "freeze_authority": "FIU-IND / PMLA Adjudicating Authority",
    },
    "ZebPay": {
        "country": "India",
        "registration": "PMLA Registered - FIU-IND",
        "vasp_type": "Centralized Exchange",
        "chains": ["BTC", "ETH"],
        "nodal_email": "compliance@zebpay.com",
        "nodal_officer": "Compliance Officer",
        "legal_address": "Awlencan Innovations India Pvt Ltd, Ahmedabad, India",
        "hot_wallet_patterns": [],
        "deposit_address_heuristics": {"address_reuse": "medium", "volume_usd_min": 1},
        "risk_level": "LOW",
        "freeze_authority": "FIU-IND / PMLA Adjudicating Authority",
    },
    "Mudrex": {
        "country": "India",
        "registration": "PMLA Registered - FIU-IND",
        "vasp_type": "Centralized Exchange",
        "chains": ["BTC", "ETH", "BNB"],
        "nodal_email": "compliance@mudrex.com",
        "nodal_officer": "Compliance Officer",
        "legal_address": "Easyfi Network Private Limited, Bengaluru, India",
        "hot_wallet_patterns": [],
        "deposit_address_heuristics": {"address_reuse": "medium", "volume_usd_min": 5},
        "risk_level": "LOW",
        "freeze_authority": "FIU-IND / PMLA Adjudicating Authority",
    },
    "CoinSwitch": {
        "country": "India",
        "registration": "PMLA Registered - FIU-IND",
        "vasp_type": "Centralized Exchange",
        "chains": ["BTC", "ETH", "TRON"],
        "nodal_email": "legal@coinswitch.co",
        "nodal_officer": "Chief Compliance Officer",
        "legal_address": "CoinSwitch Kuber, Bengaluru, India",
        "hot_wallet_patterns": [],
        "deposit_address_heuristics": {"address_reuse": "low", "volume_usd_min": 1},
        "risk_level": "LOW",
        "freeze_authority": "FIU-IND / PMLA Adjudicating Authority",
    },

    # â”€â”€â”€ GLOBAL VASPs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "Binance": {
        "country": "International (Cayman Islands)",
        "registration": "FIU-IND (India), FINTRAC (Canada), BaFin (Germany)",
        "vasp_type": "Centralized Exchange (World's Largest)",
        "chains": ["BTC", "ETH", "TRON", "BNB", "POLYGON", "SOL"],
        "nodal_email": "law-enforcement@binance.com",
        "nodal_officer": "Law Enforcement Response Team",
        "legal_address": "Binance Holdings Ltd, Cayman Islands",
        "hot_wallet_patterns": [
            "0x28c6c06298d514db089934071355e5743bf21d60",  # Binance Hot Wallet 14 (ETH)
            "0xdfd5293d8e347dff59e4571400924b33ee2841b4",  # Binance Hot Wallet 16 (ETH)
            "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8",  # Binance 7 (ETH)
            "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be",
            "0xd551234ae421e3bcba99a0da6d736074f22192ff",
            "0x564286362092D8e7936f0549571a803B203aAceD",
            "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",          # Binance BTC Hot
            "12cgpFdJViXbwHbhrA3TuW1EGnL25Zqc3P",          # Binance BTC Hot
            "34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo",          # Binance Cold Wallet BTC
            "TPYn4n8SkG9nnEtCdFnuJDWHubasRdbzxU",          # Binance Hot Wallet (TRON)
            "TMuA6YqfCeX8EhbfYEg5y7S4DqzSJireY9",          # Binance TRC20 Hot Wallet
        ],
        "deposit_address_heuristics": {"address_reuse": "low", "volume_usd_min": 10},
        "risk_level": "LOW",
        "freeze_authority": "MLAT / INTERPOL NCB / FIU-IND Disclosure Request",
    },
    "Huobi/HTX": {
        "country": "International",
        "registration": "Multiple jurisdictions",
        "vasp_type": "Centralized Exchange",
        "chains": ["BTC", "ETH", "TRON"],
        "nodal_email": "compliance@htx.com",
        "nodal_officer": "Compliance Officer",
        "legal_address": "HTX (Formerly Huobi), Seychelles",
        "hot_wallet_patterns": [
            "0xab5c66752a9e8167967685f1450532fb96d5d24f",
            "0x6748f50f686bfbca6fe8ad62b22228b87f31ff2b",
            "12vAqkTrNmR7r3UMQrtiNNHpRXCybFmQqb",
            "TFrzFkE9Fv6x72rJk6V84xY5V5kC7W19XN",          # HTX TRON Hot Wallet
        ],
        "deposit_address_heuristics": {"address_reuse": "medium", "volume_usd_min": 50},
        "risk_level": "MEDIUM",
        "freeze_authority": "MLAT / FIU-IND Disclosure Request",
    },
    "OKX": {
        "country": "International (Seychelles)",
        "registration": "Various jurisdictions",
        "vasp_type": "Centralized Exchange",
        "chains": ["BTC", "ETH", "TRON", "BNB", "POLYGON", "SOL"],
        "nodal_email": "compliance@okx.com",
        "nodal_officer": "Compliance Department",
        "legal_address": "OKX, Victoria, Mahe, Seychelles",
        "hot_wallet_patterns": [
            "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b",
        ],
        "deposit_address_heuristics": {"address_reuse": "low", "volume_usd_min": 10},
        "risk_level": "LOW",
        "freeze_authority": "MLAT / FIU-IND Disclosure Request",
    },
    "KuCoin": {
        "country": "International (Seychelles)",
        "registration": "Various jurisdictions",
        "vasp_type": "Centralized Exchange",
        "chains": ["BTC", "ETH", "TRON", "BNB"],
        "nodal_email": "support@kucoin.com",
        "nodal_officer": "Compliance Officer",
        "legal_address": "KuCoin, Seychelles",
        "hot_wallet_patterns": [
            "0x2b5634c42055806a59e9107ed44d43c426e58258",
        ],
        "deposit_address_heuristics": {"address_reuse": "medium", "volume_usd_min": 20},
        "risk_level": "MEDIUM",
        "freeze_authority": "MLAT / FIU-IND Disclosure Request",
    },
    "Bybit": {
        "country": "International (Dubai, UAE)",
        "registration": "VARA (Dubai), Various jurisdictions",
        "vasp_type": "Centralized Exchange / Derivatives",
        "chains": ["BTC", "ETH", "TRON", "BNB"],
        "nodal_email": "compliance@bybit.com",
        "nodal_officer": "Chief Compliance Officer",
        "legal_address": "Bybit Fintech Ltd, Dubai, UAE",
        "hot_wallet_patterns": [
            "0xf89d7b9c864f589bbf53a82105107622b35eaa40",
        ],
        "deposit_address_heuristics": {"address_reuse": "low", "volume_usd_min": 50},
        "risk_level": "LOW",
        "freeze_authority": "MLAT / VARA Dubai / FIU-IND Disclosure Request",
    },
    "Kraken": {
        "country": "USA",
        "registration": "FinCEN, FCA (UK)",
        "vasp_type": "Centralized Exchange",
        "chains": ["BTC", "ETH"],
        "nodal_email": "law-enforcement@kraken.com",
        "nodal_officer": "Law Enforcement Response Team",
        "legal_address": "Payward Inc, San Francisco, California, USA",
        "hot_wallet_patterns": [
            "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0",
        ],
        "deposit_address_heuristics": {"address_reuse": "low", "volume_usd_min": 50},
        "risk_level": "LOW",
        "freeze_authority": "MLAT / MLA Treaty with India-USA",
    },
    "Coinbase": {
        "country": "USA",
        "registration": "FinCEN, NYDFS BitLicense, FCA (UK)",
        "vasp_type": "Centralized Exchange (NASDAQ Listed)",
        "chains": ["BTC", "ETH", "POLYGON", "SOL"],
        "nodal_email": "law-enforcement@coinbase.com",
        "nodal_officer": "Law Enforcement Response Team",
        "legal_address": "Coinbase Global Inc, San Francisco, California, USA",
        "hot_wallet_patterns": [
            "0x71660c4005ba85c37ccec55d0c4493e66fe775d3",
        ],
        "deposit_address_heuristics": {"address_reuse": "low", "volume_usd_min": 100},
        "risk_level": "LOW",
        "freeze_authority": "MLAT / MLA Treaty with India-USA",
    },

    # â”€â”€â”€ HIGH-RISK / MIXER / DARKNET â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "Tornado Cash": {
        "country": "N/A (Decentralized Protocol - Sanctioned by OFAC)",
        "registration": "OFAC SDN Listed - Prohibited Entity",
        "vasp_type": "Crypto Mixer / Tumbler (Privacy Protocol)",
        "chains": ["ETH", "BNB", "POLYGON"],
        "nodal_email": "N/A (Decentralized)",
        "nodal_officer": "N/A",
        "legal_address": "Sanctioned - No Legal Address",
        "hot_wallet_patterns": [
            "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b",
            "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf",
            "0xa160cdab225685da1d56aa342ad8841c3b53f291",
        ],
        "deposit_address_heuristics": {"address_reuse": "very_low", "volume_usd_min": 100},
        "risk_level": "CRITICAL",
        "freeze_authority": "OFAC Sanctions / CBI / ED Attachment Order",
    },
    "ChipMixer": {
        "country": "N/A (Darknet - Seized by FBI/Europol in 2023)",
        "registration": "Criminal Enterprise - Seized",
        "vasp_type": "Bitcoin Mixer (Darknet)",
        "chains": ["BTC"],
        "nodal_email": "N/A",
        "nodal_officer": "N/A",
        "legal_address": "N/A",
        "hot_wallet_patterns": [
            "1CgpF1SQFxRKKXGHRBBwNR9FNXRg69sX4u",
        ],
        "deposit_address_heuristics": {"address_reuse": "low", "volume_usd_min": 100},
        "risk_level": "CRITICAL",
        "freeze_authority": "CBI / ED / MLAT",
    },
    "LocalBitcoins": {
        "country": "Finland",
        "registration": "FIN-FSA (Finland)",
        "vasp_type": "P2P Exchange (Ceased Operations 2023)",
        "chains": ["BTC"],
        "nodal_email": "N/A",
        "nodal_officer": "N/A",
        "legal_address": "LocalBitcoins Ltd, Helsinki, Finland",
        "hot_wallet_patterns": [],
        "deposit_address_heuristics": {"address_reuse": "high", "volume_usd_min": 1},
        "risk_level": "HIGH",
        "freeze_authority": "MLAT / FIN-FSA",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# EXPANDED MIXER_CONTRACTS (Priority 3 Intelligence Upgrade)
# Replaces the original 6-entry dict with 30+ entries covering all major mixers.
# Sources: OFAC SDN List, FinCEN advisories, Chainalysis public reports.
# ═══════════════════════════════════════════════════════════════════════════════

MIXER_CONTRACTS = {
    # ─── TORNADO CASH (ETH / EVM) — OFAC Sanctioned 2022-08-08 ────────────────
    "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b": "Tornado Cash Router (OFAC Sanctioned)",
    "0x8589427373d6d84e98730d7795d8f6f8731fda16": "Tornado Cash 0.1 ETH Pool",
    "0x722122df12d450ac402db98d5b99e150ff39388f": "Tornado Cash 1 ETH Pool",
    "0xd4b88df4d29f5cedd6857912842cff3b20c8cfa3": "Tornado Cash 10 ETH Pool",
    "0xfd8610d1f95300bd0b021b1426673573c910cf04": "Tornado Cash 100 ETH Pool",
    "0x07687e702b410fa43f4cb4af7fa097918ffd2730": "Tornado Cash 1000 ETH Pool",
    "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf": "Tornado Cash USDC Pool",
    "0xa160cdab225685da1d56aa342ad8841c3b53f291": "Tornado Cash USDT Pool",
    "0x12d66f87a04a9e220c9d49f61e00a9278b0bfba2": "Tornado Cash BNB Pool (OFAC Sanctioned)",
    "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936": "Tornado Cash MATIC Pool",
    "0x94a1b5cdb22c43faab4abeb5c74999895464ddaf": "Tornado Cash Nova (Arbitrum L2 Privacy)",
    # ─── RAILGUN — ETH Privacy Protocol ────────────────────────────────────────
    "0xfa7093cdd9ee6932b4eb2c9e1cde7ce00b1fa4b4": "Railgun Privacy Pool (ETH) — DPRK Nexus",
    "0x0000000081ac29a328c9f4f4eba94161e0e1bd54": "Railgun Smart Wallet Proxy",
    # ─── AZTEC CONNECT — ETH ZK-Privacy ───────────────────────────────────────
    "0xff1f2b4adb9df6fc8eafecdcbf96a2b351680455": "Aztec Connect Bridge (ZK Privacy Layer)",
    "0x737901bea3eeb88459df9ef1be8ff3ae1b42a2ba": "Aztec Rollup Processor",
    # ─── WASABI WALLET — BTC CoinJoin Coordinator ─────────────────────────────
    "bc1qs604c7jv6amk4cxqlnvuxv26hv3e48cds4m0ew": "Wasabi Wallet CoinJoin Coordinator v1 (BTC)",
    "bc1q0xnrum34jmncwczs4rjj5h5jg5pcdedq0d43j2": "Wasabi Wallet CoinJoin Coordinator v2 (BTC)",
    # ─── SAMOURAI WHIRLPOOL — BTC Privacy Mixer ───────────────────────────────
    "bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ydqed2": "Samourai Whirlpool 0.001 BTC Pool",
    "bc1q9mhkzwdanpezfvuhuqkpfzqxh2dxp6kzcrnh0v": "Samourai Whirlpool 0.01 BTC Pool",
    "bc1qe9fxh3l6pjunhx96nskk3jjvt2d2jt8yqtmgjf": "Samourai Whirlpool 0.05 BTC Pool",
    "bc1qnamecolphtmvnxvsqstkj6jx74mewuvsv9klfd": "Samourai Whirlpool 0.5 BTC Pool",
    # ─── BLENDER.IO — OFAC Sanctioned BTC Mixer (DPRK) ───────────────────────
    "bc1qhme9pzhhll4dquwf4e2gkn3qlq2ew00e7tdqnn": "Blender.io BTC Mixer (OFAC SDN 35142)",
    # ─── SINBAD.IO — Blender successor (OFAC Sanctioned Nov 2023) ────────────
    "bc1q2d9ln3e4fnfr8v47x0s2n3a3g0emxkn3qrn6f5": "Sinbad.io BTC Mixer (OFAC SDN 37241)",
    # ─── CHIPMIXER — FBI/Europol seized March 2023 ────────────────────────────
    "1CgpF1SQFxRKKXGHRBBwNR9FNXRg69sX4u": "ChipMixer Input Address (Seized 2023)",
    "bc1qr7l2nqm8d9jfgxn5p8z4e6v3q9kw0a2snxgwrq": "ChipMixer Output Cluster",
    # ─── PHOENIX SWAP — ETH Privacy Mixer ─────────────────────────────────────
    "0x8b3192f5eebd8579568a2ed41e6feb402f93f73f": "Phoenix Swap Privacy Mixer (ETH)",
    # ─── TORNADO.CASH CLONES / FORKS ─────────────────────────────────────────
    "0x23773e65ed146a459667dd7e6781470d5d1e4f2e": "CycloneCash (Tornado Fork - BSC)",
    "0xa0c68c638235ee32657e8f720a23cec1bfc77c77": "AnonimixFinance (Tornado Clone)",
    # ─── TRON MIXERS / USDT ANONYMIZERS ──────────────────────────────────────
    "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE": "TRON Mixer Pool 1 (USDT TRC-20)",
    "TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL": "TRON Mixer Pool 2 (TRC-20 Anonymizer)",
}


# ═══════════════════════════════════════════════════════════════════════════════
# EXPANDED DEFI_BRIDGES (Priority 3 Intelligence Upgrade)
# Cross-chain bridge contracts frequently used in crypto laundering to break
# attribution across chains. Sources: Chainalysis, DeFi Llama, OFAC research.
# ═══════════════════════════════════════════════════════════════════════════════

DEFI_BRIDGES = {
    # ─── ACROSS PROTOCOL ──────────────────────────────────────────────────────
    "0x5c7bcabeed66d30d10e5cb36757d54d80d23a1da": "Across Protocol SpokePool (ETH)",
    "0x4d9079bb4165aeb4084c526a326959cfad2f7781": "Across Protocol HubPool",
    # ─── STARGATE / LAYERZERO ─────────────────────────────────────────────────
    "0xaf5191b0de27e6514942c6797ed96a9cf6babffa": "Stargate Router (LayerZero ETH)",
    "0x8731d54e9d02c213766ea528bac7dd6004386a5b": "Stargate Router ETH Pool",
    "0x9d1b1669c73b033dfe47ae5a0164ab96df25b944": "Stargate Router (BNB)",
    # ─── SYNAPSE BRIDGE ───────────────────────────────────────────────────────
    "0x2796317b0bf8529607744923bca0249764a77d11": "Synapse Bridge Router",
    "0x45a51b67d98beb89b83a6e3e7e0f4f9a25d0c06e": "Synapse L2 Router",
    # ─── HOP PROTOCOL ─────────────────────────────────────────────────────────
    "0xb8901acb9305435f9f0c3a15261ab4e54f64d1f2": "Hop Protocol Bridge (ETH)",
    "0x3e4a3a4796d16c0cd582c382691998f7c06420b6": "Hop Bridge AMB Relay",
    # ─── WORMHOLE ─────────────────────────────────────────────────────────────
    "0x98f3c9e6e3face36baad05fe09d375eff1764732": "Wormhole Core Bridge (ETH)",
    "0x3ee18b2214aff97000d974cf647e7c347e8fa585": "Wormhole Token Bridge (ETH)",
    # ─── MULTICHAIN / ANYSWAP (COMPROMISED / HACKED 2023) ────────────────────
    "0x3014ca10b91cb3d0ad85fef7a3cb95bcac9c0f79": "AnySwap / Multichain Bridge (COMPROMISED)",
    "0xba8da9dcf11b50b03fd5284f164ef5cdef910705": "Multichain Cross-Chain Router (HACKED Jul 2023)",
    "0x55f5ee5e6a4bb04fba7fb4a95c5d9a8c04f3a5f7": "Multichain Fantom Bridge (Hacked)",
    # ─── CBRIDGE / CELER ──────────────────────────────────────────────────────
    "0x1116898dda4015ed8ddefb84b6e8bc24528af2d8": "cBridge v2 (Celer Network)",
    "0x5427fefa711eff984124bfbb1ab6fbf5e3da1820": "cBridge v1 (Celer Legacy)",
    # ─── POLYGON OFFICIAL BRIDGE ──────────────────────────────────────────────
    "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf": "Polygon ERC20 Bridge (Official)",
    "0xa0c68c638235ee32657e8f720a23cec1bfc77c77": "Polygon PoS Bridge (Plasma)",
    # ─── DEBRIDGE / ORBITER / DLN ─────────────────────────────────────────────
    "0x43de2d77bf8027e25dbd179b491e8d64f38398aa": "deBridge Finance Router",
    "0xe4edb277e41dc89ab076a1f049f4a3efa700bce8": "Orbiter Finance L2 Bridge",
    "0xeef63996a2b18f1c7c62f0d7571d5cefd31cb844": "DLN Source (deBridge Limit Orders)",
    # ─── OKX DEX ──────────────────────────────────────────────────────────────
    "0x40aa958dd87fc8305b97f2ba922cddca374bcd7f": "OKX DEX Aggregator Bridge",
    # ─── RENBRIDGE (DEPRECATED / RISKY) ──────────────────────────────────────
    "0xe4ddb4233513498b5aa79b98bea473b01b101a67": "RenBridge GatewayRegistry (Deprecated)",
    "0x3e9d6430144485873248251fcb92bd49daf46a6e": "RenBridge BTC Gateway (Legacy)",
    # ─── TRON CROSS-CHAIN ─────────────────────────────────────────────────────
    "thpvauhoh2qn2y9thczml3h815hhfhn5yc": "TRON Cross-Chain Bridge",
    "TBXy3GCd47q1MfEWmhY7vGNDgMRQkB5eem": "TRON-ETH Bridge Relay (JustCrossChain)",
    # ─── ARBITRUM / OPTIMISM OFFICIAL BRIDGES ────────────────────────────────
    "0x8315177ab297ba92a06054ce80a67ed4dbd7ed3a": "Arbitrum One Bridge (Official Escrow)",
    "0x99c9fc46f92e8a1c0dec1b1747d010903e884be1": "Optimism Bridge L1 (Official)",
    # ─── INTEROPERABILITY HUBS (fraud risk: used to break chain trail) ────────
    "0x0000000054164c90d2b1e1ca4f13f7d6de38bc6e": "Rubic Cross-Chain DEX",
    "0xec3a35ad74d31f0a8da0b71d57e3e02bc1f4e9a4": "XY Finance Cross-Chain Aggregator",
}


# ═══════════════════════════════════════════════════════════════════════════════
# SOLANA VASP HOT WALLETS (Priority 3 — SOL Chain Support)
# Source: Solscan exchange labels, Chainalysis public VASP identifiers
# ═══════════════════════════════════════════════════════════════════════════════

SOLANA_EXCHANGE_WALLETS = {
    # Binance Solana Hot Wallets
    "5tzFkiKscXHK5ZXCGbCZyKVa7kEduD73swuVaXoSJBnX": "Binance SOL Deposit Hot Wallet",
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Binance SOL Cold Wallet",
    # Kraken Solana
    "FWznbcNXWQuHTawe9RxvQ2LdCENssh12dsznf4RiouN5": "Kraken SOL Deposit Address",
    # OKX Solana
    "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS": "OKX SOL Exchange Wallet",
    # Coinbase Solana
    "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7as5": "Coinbase SOL Custody Wallet",
}


def lookup_vasp_by_address(address: str) -> dict | None:
    """
    Check if a wallet address belongs to a known VASP cluster.
    Checks both the main VASP_CLUSTERS dict and SOLANA_EXCHANGE_WALLETS.
    EVM addresses: case-insensitive. BTC/TRON/SOL: case-sensitive.
    """
    raw_addr = (address or "").strip()
    if not raw_addr:
        return None
    addr_lower = raw_addr.lower()

    # Check main VASP clusters
    for vasp_name, vasp_info in VASP_CLUSTERS.items():
        for pattern in vasp_info.get("hot_wallet_patterns", []):
            p = pattern.strip()
            if p.startswith("0x"):
                if p.lower() == addr_lower:
                    is_ind = vasp_info.get("country", "").strip().lower() == "india"
                    return {"vasp": vasp_name, "is_indian": is_ind, **vasp_info}
            else:
                if p == raw_addr or p.lower() == addr_lower:
                    is_ind = vasp_info.get("country", "").strip().lower() == "india"
                    return {"vasp": vasp_name, "is_indian": is_ind, **vasp_info}

    # Check Solana wallets
    sol_match = SOLANA_EXCHANGE_WALLETS.get(raw_addr)
    if sol_match:
        return {
            "vasp": sol_match,
            "chain": "SOL",
            "is_indian": False,
            "risk_level": "LOW",
            "vasp_type": "Centralized Exchange (Solana)",
        }

    # Check mixer contracts
    mixer_hit = MIXER_CONTRACTS.get(raw_addr) or MIXER_CONTRACTS.get(addr_lower)
    if mixer_hit:
        return {
            "vasp": f"MIXER: {mixer_hit}",
            "chain": "ETH",
            "is_indian": False,
            "risk_level": "CRITICAL",
            "vasp_type": "Privacy Mixer / Tumbler",
            "nodal_email": "N/A — Decentralized Protocol",
        }

    return None


def is_indian_vasp(vasp_name: str) -> bool:
    """Return True if VASP is an Indian registered reporting entity under FIU-IND."""
    info = VASP_CLUSTERS.get(vasp_name, {})
    return info.get("country", "").strip().lower() == "india"


def lookup_mixer(address: str) -> str | None:
    """Check if an address is a known mixer. Returns mixer name or None."""
    raw = (address or "").strip()
    return MIXER_CONTRACTS.get(raw) or MIXER_CONTRACTS.get(raw.lower())


def lookup_bridge(address: str) -> str | None:
    """Check if an address is a known DeFi bridge. Returns bridge name or None."""
    raw = (address or "").strip()
    return DEFI_BRIDGES.get(raw) or DEFI_BRIDGES.get(raw.lower())


def get_all_vasps() -> dict:
    return VASP_CLUSTERS


def get_intelligence_summary() -> dict:
    """Return a summary of intelligence coverage for API/health endpoints."""
    return {
        "vasp_clusters": len(VASP_CLUSTERS),
        "vasp_hot_wallets": sum(
            len(v.get("hot_wallet_patterns", [])) for v in VASP_CLUSTERS.values()
        ),
        "solana_exchange_wallets": len(SOLANA_EXCHANGE_WALLETS),
        "mixer_contracts": len(MIXER_CONTRACTS),
        "defi_bridges": len(DEFI_BRIDGES),
        "supported_chains": ["BTC", "ETH", "BNB", "TRON", "POLYGON", "SOL"],
    }

# Chain ID to Explorer mapping
CHAIN_EXPLORERS = {
    "BTC": {
        "name": "Bitcoin",
        "explorer_url": "https://blockchair.com/bitcoin/address/{address}",
        "api_url": "https://blockchain.info/rawaddr/{address}",
        "symbol": "BTC",
    },
    "ETH": {
        "name": "Ethereum",
        "explorer_url": "https://etherscan.io/address/{address}",
        "api_url": "https://api.etherscan.io/api",
        "symbol": "ETH",
    },
    "TRON": {
        "name": "TRON / TRC-20",
        "explorer_url": "https://tronscan.org/#/address/{address}",
        "api_url": "https://apilist.tronscanapi.com/api/accountv2",
        "symbol": "TRX",
    },
    "BNB": {
        "name": "BNB Smart Chain",
        "explorer_url": "https://bscscan.com/address/{address}",
        "api_url": "https://api.bscscan.com/api",
        "symbol": "BNB",
    },
    "POLYGON": {
        "name": "Polygon / MATIC",
        "explorer_url": "https://polygonscan.com/address/{address}",
        "api_url": "https://api.polygonscan.com/api",
        "symbol": "MATIC",
    },
    "SOL": {
        "name": "Solana",
        "explorer_url": "https://solscan.io/account/{address}",
        "api_url": "https://api.mainnet-beta.solana.com",
        "symbol": "SOL",
    },
}

