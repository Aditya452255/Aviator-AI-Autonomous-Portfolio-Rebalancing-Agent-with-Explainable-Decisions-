"""Override Statistics analytics reporting breakdown by override reason category."""

from typing import List
import pandas as pd
from src.core.logger import get_logger
from src.models.override import OverrideRecord

logger = get_logger(__name__)


class OverrideStatistics:
    """Enterprise analytics engine summarizing advisor override reasons and actions."""

    def compute_override_summary_df(self, records: List[OverrideRecord]) -> pd.DataFrame:
        """Compute summary DataFrame of manual advisor overrides.

        Args:
            records: List of OverrideRecord instances.

        Returns:
            DataFrame containing aggregated override categories and actions.
        """
        rows = []
        for r in records:
            rows.append({
                "override_id": r.override_id,
                "decision_id": r.decision_id,
                "portfolio_id": r.portfolio_id,
                "advisor_id": r.advisor_id,
                "action": r.action.value if hasattr(r.action, "value") else str(r.action),
                "original_recommendation": r.original_recommendation,
                "modified_recommendation": r.modified_recommendation,
                "reason_category": r.reason_category,
                "timestamp": r.timestamp,
                "comments": r.comments,
            })

        if not rows:
            return pd.DataFrame(columns=["override_id", "decision_id", "portfolio_id", "advisor_id", "action", "reason_category"])

        return pd.DataFrame(rows)
