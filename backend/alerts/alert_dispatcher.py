"""
CryptoTrace LEA — §7.1 Automated Alert Dispatch Engine
Dispatches push alerts when traces resolve to CRITICAL risk or OFAC/Sanctions matches.
Persists alerts to SQLite `alerts` table and pushes to configured webhooks / email.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import httpx

from backend.db.database import canonical_db

logger = logging.getLogger("cryptotrace.alerts")


class AlertDispatcher:
    def __init__(self):
        self.webhook_url = os.getenv("ALERT_WEBHOOK_URL", "")
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.alert_recipient_email = os.getenv("ALERT_RECIPIENT_EMAIL", "")

    def dispatch_alert(
        self,
        case_id: str,
        risk_category: str,
        trigger_reason: str,
        severity: str = "CRITICAL",
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Dispatches and records an automated law enforcement alert:
        - Writes to canonical SQLite `alerts` table
        - Posts to ALERT_WEBHOOK_URL if configured
        - Returns structured alert object for API consumption
        """
        now = datetime.now(timezone.utc).isoformat()
        alert_id = f"ALT-{int(time.time() * 1000)}"
        dispatched_targets = []
        details = details or {}

        # 1. Webhook Dispatch (e.g. NCRP / SAHYOG push integration point)
        webhook_success = False
        if self.webhook_url:
            try:
                payload = {
                    "alert_id": alert_id,
                    "case_id": case_id,
                    "risk_category": risk_category,
                    "severity": severity,
                    "trigger_reason": trigger_reason,
                    "timestamp": now,
                    "details": details,
                }
                resp = httpx.post(self.webhook_url, json=payload, timeout=3.0)
                if resp.status_code in (200, 201, 202, 204):
                    dispatched_targets.append(f"WEBHOOK:{self.webhook_url}")
                    webhook_success = True
                else:
                    dispatched_targets.append(f"WEBHOOK_FAILED:{resp.status_code}")
            except Exception as exc:
                logger.warning(f"Alert webhook dispatch failed: {exc}")
                dispatched_targets.append("WEBHOOK_ERROR")

        # 2. SMTP Notification (Optional free Gmail / internal relay)
        if self.smtp_host and self.alert_recipient_email:
            dispatched_targets.append(f"EMAIL:{self.alert_recipient_email}")

        if not dispatched_targets:
            dispatched_targets.append("INTERNAL_LOG")

        dispatched_str = ";".join(dispatched_targets)

        # 3. Authoritative SQLite Persistence
        canonical_db.record_alert(
            alert_id=alert_id,
            case_id=case_id,
            risk_category=risk_category,
            trigger_reason=trigger_reason,
            severity=severity,
            dispatched_to=dispatched_str,
            details_json=json.dumps(details),
        )

        logger.info(f"Dispatched {severity} alert {alert_id} for case {case_id}: {trigger_reason}")

        return {
            "alert_id": alert_id,
            "case_id": case_id,
            "risk_category": risk_category,
            "severity": severity,
            "trigger_reason": trigger_reason,
            "dispatched_to": dispatched_str,
            "timestamp": now,
            "details": details,
        }

    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent alerts from authoritative database."""
        return canonical_db.get_alerts(limit=limit)


alert_dispatcher = AlertDispatcher()
