"""
CryptoTrace LEA — Automated Alerts & Notifications Package
Dispatches push alerts on CRITICAL risk, sanctions hits, or high-value mule transfers.
"""

from .alert_dispatcher import AlertDispatcher, alert_dispatcher

__all__ = ["AlertDispatcher", "alert_dispatcher"]
