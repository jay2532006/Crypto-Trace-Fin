"""
CryptoTrace LEA — §1.9 DeFi / Decentralized Exchange (DEX) Registry
Curated registry of production DEX routers and liquidity pools (Uniswap, SushiSwap, PancakeSwap, Curve, SunSwap).
Enables detection of asset swaps that break BFS asset continuity.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class DEXContractEntry(BaseModel):
    protocol: str
    chain: str
    contract_addresses: List[str]
    category: str
    description: str
    source_url: str


DEX_REGISTRY: Dict[str, Dict[str, Any]] = {
    # 1. Uniswap V3 SwapRouters (Ethereum)
    "UNISWAP_V3_ETH": {
        "protocol": "Uniswap V3",
        "chain": "ETH",
        "contract_addresses": [
            "0xe592427a0aece92de3edee1f18e0157c05861564",  # SwapRouter
            "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",  # SwapRouter02
        ],
        "category": "DEX_ROUTER",
        "description": "Uniswap V3 Automated Market Maker Router",
        "source_url": "https://docs.uniswap.org/contracts/v3/reference/deployments",
    },
    # 2. Uniswap V2 Router (Ethereum)
    "UNISWAP_V2_ETH": {
        "protocol": "Uniswap V2",
        "chain": "ETH",
        "contract_addresses": [
            "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # UniswapV2Router02
        ],
        "category": "DEX_ROUTER",
        "description": "Uniswap V2 Router",
        "source_url": "https://docs.uniswap.org/contracts/v2/reference/smart-contracts/router-02",
    },
    # 3. Uniswap Universal Router (Ethereum & Multi-chain)
    "UNISWAP_UNIVERSAL_ETH": {
        "protocol": "Uniswap Universal Router",
        "chain": "ETH",
        "contract_addresses": [
            "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad",  # UniversalRouter
            "0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b",
        ],
        "category": "DEX_ROUTER",
        "description": "Uniswap Universal Router (ERC20 + NFT Batch Swaps)",
        "source_url": "https://docs.uniswap.org/contracts/universal-router/overview",
    },
    # 4. SushiSwap Router (Ethereum)
    "SUSHISWAP_ETH": {
        "protocol": "SushiSwap",
        "chain": "ETH",
        "contract_addresses": [
            "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",  # SushiSwap Router
        ],
        "category": "DEX_ROUTER",
        "description": "SushiSwap AMM Router",
        "source_url": "https://docs.sushi.com/docs/Products/Classic%20AMM/Deployment%20Addresses",
    },
    # 5. PancakeSwap V2 Router (BSC)
    "PANCAKESWAP_V2_BSC": {
        "protocol": "PancakeSwap V2",
        "chain": "BSC",
        "contract_addresses": [
            "0x10ed43c718714eb63d5aa57b78b54704e256024e",  # PancakeRouter V2
        ],
        "category": "DEX_ROUTER",
        "description": "PancakeSwap V2 Router on BNB Chain",
        "source_url": "https://docs.pancakeswap.finance/developers/smart-contracts/pancakeswap-exchange/v2-exchange/router-v2",
    },
    # 6. Curve Finance 3pool (Ethereum StableSwap)
    "CURVE_3POOL_ETH": {
        "protocol": "Curve Finance",
        "chain": "ETH",
        "contract_addresses": [
            "0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7",  # 3pool (DAI/USDC/USDT)
        ],
        "category": "DEX_STABLESWAP",
        "description": "Curve Finance Stablecoin Pool",
        "source_url": "https://docs.curve.fi/references/deployed-contracts/",
    },
    # 7. SunSwap Router (TRON)
    "SUNSWAP_V2_TRON": {
        "protocol": "SunSwap V2",
        "chain": "TRON",
        "contract_addresses": [
            "TKzxdSv2xUmFFFiTeQgDUXKUSPdjWNwyW5",  # SunSwap V2 Router
        ],
        "category": "DEX_ROUTER",
        "description": "SunSwap V2 Router on TRON Network",
        "source_url": "https://sunswap.com",
    },
}


def is_dex_contract(address: str) -> bool:
    """Returns True if the address matches a verified DEX router contract."""
    if not address or not isinstance(address, str):
        return False
    addr = address.strip().lower()
    for entry in DEX_REGISTRY.values():
        if any(c.lower() == addr for c in entry["contract_addresses"]):
            return True
    return False


def get_dex_info(address: str) -> Optional[Dict[str, Any]]:
    """Returns metadata for the matching DEX contract if found, else None."""
    if not address or not isinstance(address, str):
        return None
    addr = address.strip().lower()
    for entry in DEX_REGISTRY.values():
        if any(c.lower() == addr for c in entry["contract_addresses"]):
            return entry
    return None
