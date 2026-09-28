# backend/adapters/bip39_validator.py
"""
CryptoTrace LEA - BIP-39 and Private Key Security Safeguard
Validates input narratives against the full official 2,048 BIP-39 wordlist
and 64-character hexadecimal private keys to prevent credential leakage into evidence.
"""

import os
import re
from typing import Set

WORDLIST_PATH = os.path.join(os.path.dirname(__file__), "bip39_english.txt")

try:
    with open(WORDLIST_PATH, "r", encoding="utf-8") as f:
        BIP39_WORDS: Set[str] = {line.strip().lower() for line in f if line.strip()}
except Exception:
    BIP39_WORDS = set()

HEX_PRIVATE_KEY_PATTERN = re.compile(r"\b(?:0x)?[a-fA-F0-9]{64}\b")

def detect_private_key(text: str) -> bool:
    if not text:
        return False
    return bool(HEX_PRIVATE_KEY_PATTERN.search(text))

def detect_mnemonic(text: str, threshold: int = 12) -> bool:
    if not text:
        return False
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    consecutive = 0
    max_consecutive = 0
    total_matches = 0
    for w in words:
        if w in BIP39_WORDS:
            consecutive += 1
            total_matches += 1
            if consecutive > max_consecutive:
                max_consecutive = consecutive
        else:
            consecutive = 0
    return max_consecutive >= threshold or total_matches >= threshold
