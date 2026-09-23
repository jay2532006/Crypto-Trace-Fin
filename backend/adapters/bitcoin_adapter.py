"""
CryptoTrace LEA — Bitcoin Chain Adapter (Mempool.space Canonical Backbone)
Integrates with Mempool.space API (Primary) and Blockstream Esplora (Fallback).
Extracts confirmed UTXOs and raw transaction events.
"""

import os
import requests
from typing import List, Dict, Any
from .chain_adapter_base import ChainAdapterBase
from backend.models.domain_models import Transfer
from backend.models.confidence_types import FinalityState
from backend.storage.raw_payload_storage import raw_storage

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CryptoTrace-LEA/2.0"
}
TIMEOUT = 8


class BitcoinAdapter(ChainAdapterBase):
    def __init__(self, primary_url: str = "", fallback_url: str = ""):
        super().__init__("BTC")
        self.primary_url = primary_url or os.getenv("MEMPOOL_SPACE_URL", "https://mempool.space/api")
        self.fallback_url = fallback_url or os.getenv("BLOCKSTREAM_BASE_URL", "https://blockstream.info/api")

    def validate_address(self, address: str) -> bool:
        """Validates Bitcoin Legacy (1...), P2SH (3...), and Native SegWit (bc1...)."""
        if not address or not isinstance(address, str):
            return False
        addr = address.strip()
        if addr.startswith("1") and 26 <= len(addr) <= 35:
            return True
        if addr.startswith("3") and 26 <= len(addr) <= 35:
            return True
        if addr.startswith("bc1") and 40 <= len(addr) <= 90:
            return True
        return False

    def fetch_transfers(self, address: str, limit: int = 50) -> List[Transfer]:
        """Fetches transactions via Mempool.space with fallback to Esplora."""
        if not self.validate_address(address):
            return []

        transfers: List[Transfer] = []
        urls_to_try = [
            (f"{self.primary_url}/address/{address}/txs", "MEMPOOL_SPACE"),
            (f"{self.fallback_url}/address/{address}/txs", "BLOCKSTREAM_ESPLORA"),
        ]

        for url, provider_name in urls_to_try:
            try:
                resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
                if resp.status_code == 200:
                    tx_list = resp.json()
                    if isinstance(tx_list, list) and tx_list:
                        # Store raw payload
                        first_tx = tx_list[0]
                        block_height = first_tx.get("status", {}).get("block_height", 0)
                        tx_hash = first_tx.get("txid", "summary")
                        payload_hash = raw_storage.store_payload(
                            payload_dict=tx_list,
                            chain_id="BTC",
                            block_height=block_height,
                            tx_hash=tx_hash,
                            provider=provider_name.lower(),
                            payload_type="txlist",
                        )

                        for idx, tx in enumerate(tx_list[:limit]):
                            txid = tx.get("txid", "")
                            status = tx.get("status", {})
                            block_time = str(status.get("block_time", ""))

                            # Parse outputs to find transfers
                            vout_list = tx.get("vout", [])
                            for v_idx, vout in enumerate(vout_list):
                                to_addr = vout.get("scriptpubkey_address", "unknown")
                                satoshis = vout.get("value", 0)
                                btc_amount = satoshis / 1e8

                                transfers.append(
                                    Transfer(
                                        chain_id="BTC",
                                        tx_hash=txid,
                                        log_index=0,
                                        transfer_index=idx * 100 + v_idx,
                                        event_type="NATIVE",
                                        from_addr=address,
                                        to_addr=to_addr,
                                        amount=round(btc_amount, 8),
                                        asset="BTC",
                                        direction="OUT" if to_addr != address else "IN",
                                        raw_payload_hash=payload_hash,
                                        finality_state="CONFIRMED" if status.get("confirmed") else "PENDING",
                                        timestamp=block_time,
                                        provider_source=provider_name,
                                    )
                                )
                        return transfers
            except Exception:
                continue

        return transfers

    def get_finality_state(self, tx_hash: str) -> FinalityState:
        return "CONFIRMED"
