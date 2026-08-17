"""Audit Statistics analytics summarizing audit trail event types and actors."""

from typing import List
import pandas as pd
from src.core.logger import get_logger
from src.models.audit_record import AuditRecord

logger = get_logger(__name__)


class AuditStatistics:
    """Enterprise analytics engine computing audit trail event counts."""

    def compute_audit_summary_df(self, records: List[AuditRecord]) -> pd.DataFrame:
        """Compute summary DataFrame of audit trail entries.

        Args:
            records: List of AuditRecord instances.

        Returns:
            DataFrame containing aggregated audit records.
        """
        rows = []
        for r in records:
            rows.append({
                "audit_id": r.audit_id,
                "portfolio_id": r.portfolio_id,
                "decision_id": r.decision_id,
                "event_type": r.event_type.value if hasattr(r.event_type, "value") else str(r.event_type),
                "event_summary": r.event_summary,
                "actor": r.actor,
                "timestamp": r.timestamp,
            })

        if not rows:
            return pd.DataFrame(columns=["audit_id", "portfolio_id", "decision_id", "event_type", "event_summary", "actor"])

        return pd.DataFrame(rows)
