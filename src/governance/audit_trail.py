"""Audit Trail recorder producing immutable, event-sourced regulatory audit logs."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from src.core.logger import get_logger
from src.models.audit_record import AuditEventType, AuditRecord

logger = get_logger(__name__)


class AuditTrail:
    """Enterprise Audit Trail event sourcing recorder."""

    def __init__(self) -> None:
        self.records: List[AuditRecord] = []

    def record_event(
        self,
        portfolio_id: str,
        decision_id: str,
        event_type: AuditEventType,
        event_summary: str,
        details: Optional[Dict[str, Any]] = None,
        actor: str = "SYSTEM",
    ) -> AuditRecord:
        """Record an immutable audit event.

        Args:
            portfolio_id: Target portfolio ID.
            decision_id: Decision ID.
            event_type: AuditEventType enum value.
            event_summary: Event description string.
            details: Optional payload dictionary.
            actor: Actor triggering event (System, Agent, Advisor).

        Returns:
            AuditRecord instance.
        """
        audit_id = f"AUD_{portfolio_id}_{len(self.records)+1:04d}"
        rec = AuditRecord(
            audit_id=audit_id,
            portfolio_id=portfolio_id,
            decision_id=decision_id,
            event_type=event_type,
            event_summary=event_summary,
            details=details or {},
            actor=actor,
            timestamp=datetime.now().isoformat(),
        )
        self.records.append(rec)
        logger.debug(f"Audit record logged [{audit_id}] | Type: {event_type.value} | Summary: {event_summary}")
        return rec

    def get_audit_trail_for_portfolio(self, portfolio_id: str) -> List[AuditRecord]:
        """Get complete event history for a portfolio.

        Args:
            portfolio_id: Portfolio ID.

        Returns:
            List of matching AuditRecord objects.
        """
        return [r for r in self.records if r.portfolio_id == portfolio_id]
