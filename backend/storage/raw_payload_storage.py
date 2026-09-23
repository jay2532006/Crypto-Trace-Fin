"""
CryptoTrace LEA — Deterministic Raw Payload Storage & Evidence Manifest
Ensures complete forensic provenance and cryptographically tamper-evident evidence.
Rules:
- Alphabetically sorted JSON keys
- Compact encoding (no extra whitespace)
- SHA-256 of serialized string is the permanent identifier
- Storage path: raw/{chain_id}/{block_height}/{tx_hash}/{provider}/{type}/{hash}.json
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_BASE_DIR = os.path.join(BASE_DIR, "data", "raw")


def serialize_deterministically(payload: Any) -> str:
    """Serializes any dictionary or structure into canonical compact JSON with sorted keys."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_sha256(content: str) -> str:
    """Computes SHA-256 hexadecimal digest of a UTF-8 string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class RawPayloadStorage:
    def __init__(self, base_dir: str = RAW_BASE_DIR):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self._index_file = os.path.join(self.base_dir, "manifest_index.json")
        self._manifest_index = self._load_index()

    def _load_index(self) -> Dict[str, str]:
        if os.path.exists(self._index_file):
            try:
                with open(self._index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_index(self):
        try:
            with open(self._index_file, "w", encoding="utf-8") as f:
                json.dump(self._manifest_index, f, indent=2)
        except Exception:
            pass

    def store_payload(
        self,
        payload_dict: Dict[str, Any],
        chain_id: str = "eth",
        block_height: int = 0,
        tx_hash: str = "genesis",
        provider: str = "rpc",
        payload_type: str = "tx",
    ) -> str:
        """
        Stores payload with deterministic serialization and returns SHA-256 hash.
        Idempotent: Identical payload produces identical file and hash.
        """
        serialized = serialize_deterministically(payload_dict)
        payload_hash = compute_sha256(serialized)

        # Build hierarchical path
        dir_path = os.path.join(
            self.base_dir,
            str(chain_id).lower(),
            str(block_height),
            str(tx_hash).lower(),
            str(provider).lower(),
            str(payload_type).lower(),
        )
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, f"{payload_hash}.json")

        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(serialized)

        self._manifest_index[payload_hash] = os.path.relpath(file_path, self.base_dir)
        self._save_index()
        return payload_hash

    def retrieve_payload(self, payload_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieves raw JSON payload by SHA-256 hash."""
        rel_path = self._manifest_index.get(payload_hash)
        if not rel_path:
            return None
        full_path = os.path.join(self.base_dir, rel_path)
        if not os.path.exists(full_path):
            return None
        with open(full_path, "r", encoding="utf-8") as f:
            return json.loads(f.read())

    def verify_integrity(self, payload_hash: str) -> bool:
        """Recalculates SHA-256 hash of on-disk serialized file to detect tampering."""
        rel_path = self._manifest_index.get(payload_hash)
        if not rel_path:
            return False
        full_path = os.path.join(self.base_dir, rel_path)
        if not os.path.exists(full_path):
            return False
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return compute_sha256(content) == payload_hash


# Singleton instance
raw_storage = RawPayloadStorage()
