"""
CryptoTrace LEA — Chain Adapter Base Class
Abstract interface for blockchain data harvesters with cryptographic provenance.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from backend.models.domain_models import Transaction, Transfer
from backend.models.confidence_types import FinalityState


class ChainAdapterBase(ABC):
    def __init__(self, chain_id: str):
        self.chain_id = chain_id.upper()

    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """Validates network-specific address syntax and checksum."""
        pass

    @abstractmethod
    def fetch_transfers(self, address: str, limit: int = 50) -> List[Transfer]:
        """
        Fetches transfers involving address, computes canonical event identity,
        stores raw provider payload with SHA-256 hash, and normalizes into Transfers.
        """
        pass

    @abstractmethod
    def get_finality_state(self, tx_hash: str) -> FinalityState:
        """Returns the finality state of a transaction (PENDING, CONFIRMED, FINALIZED, REORGANIZED)."""
        pass
