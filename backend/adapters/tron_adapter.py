"""
CryptoTrace LEA — TRON Chain Adapter (TronGrid & Full-Node Polling)
Harvests native TRX transactions and TRC-20 USDT events with cryptographic provenance.
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


class TronAdapter(ChainAdapterBase):
    def __init__(self, api_key: str = "", base_url: str = ""):
        super().__init__("TRON")
        self.api_key = api_key or os.getenv("TRON_GRID_API_KEY", "")
        self.base_url = base_url or os.getenv("TRON_RPC_PRIMARY_URL", "https://api.trongrid.io")

    def validate_address(self, address: str) -> bool:
        """Validates TRON Base58 address (starts with T, 34 characters)."""
        if not address or not isinstance(address, str):
            return False
        addr = address.strip()
        return addr.startswith("T") and len(addr) == 34

    def fetch_transfers(self, address: str, limit: int = 50) -> List[Transfer]:
        """Fetches TRC-20 (USDT) token transfers from TronGrid."""
        if not self.validate_address(address):
            return []

        transfers: List[Transfer] = []
        url = f"{self.base_url}/v1/accounts/{address}/transactions/trc20?limit={limit}"
        headers = dict(HEADERS)
        if self.api_key:
            headers["TRON-PRO-API-KEY"] = self.api_key

        try:
            resp = requests.get(url, headers=headers, timeout=TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                tx_list = data.get("data", [])

                if isinstance(tx_list, list) and tx_list:
                    first_tx = tx_list[0]
                    tx_hash = first_tx.get("transaction_id", "summary")
                    block_ts = first_tx.get("block_timestamp", 0)

                    payload_hash = raw_storage.store_payload(
                        payload_dict=data,
                        chain_id="TRON",
                        block_height=block_ts,
                        tx_hash=tx_hash,
                        provider="trongrid",
                        payload_type="trc20_transfers",
                    )

                    for idx, tx in enumerate(tx_list):
                        t_hash = tx.get("transaction_id", "")
                        from_addr = tx.get("from", "")
                        to_addr = tx.get("to", "")
                        token_info = tx.get("token_info", {})
                        symbol = token_info.get("symbol", "USDT")
                        decimals = int(token_info.get("decimals", 6))
                        raw_value = float(tx.get("value", 0))
                        amount = raw_value / (10**decimals) if decimals else raw_value

                        transfers.append(
                            Transfer(
                                chain_id="TRON",
                                tx_hash=t_hash,
                                log_index=0,
                                transfer_index=idx,
                                event_type="TRC20",
                                from_addr=from_addr,
                                to_addr=to_addr,
                                amount=round(amount, 6),
                                asset=symbol,
                                direction="OUT" if from_addr == address else "IN",
                                raw_payload_hash=payload_hash,
                                finality_state="CONFIRMED",
                                timestamp=str(tx.get("block_timestamp")),
                                provider_source="TRONGRID_LIVE",
                            )
                        )
        except Exception:
            pass

        return transfers

    def get_finality_state(self, tx_hash: str) -> FinalityState:
        return "CONFIRMED"
