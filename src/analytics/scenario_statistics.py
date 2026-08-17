"""Scenario Statistics analytics reporting regime shocks and stress test drawdowns."""

from typing import List
import pandas as pd
from src.core.logger import get_logger
from src.models.scenario_result import ScenarioResult

logger = get_logger(__name__)


class ScenarioStatistics:
    """Enterprise Scenario Statistics analytics engine."""

    def compute_scenario_summary_df(self, results: List[ScenarioResult]) -> pd.DataFrame:
        """Compute scenario stress test summary DataFrame.

        Args:
            results: List of ScenarioResult objects.

        Returns:
            DataFrame summarizing scenario drawdowns and survival status.
        """
        rows = []
        for r in results:
            rows.append({
                "scenario_id": r.scenario_id,
                "portfolio_id": r.portfolio_id,
                "scenario_type": r.scenario_type.value if hasattr(r.scenario_type, "value") else str(r.scenario_type),
                "portfolio_return_pct": round(r.portfolio_return * 100.0, 2),
                "max_drawdown_pct": round(r.max_drawdown * 100.0, 2),
                "var_95_pct": r.var_95,
                "cvar_95_pct": r.cvar_95,
                "recovery_days": r.recovery_days,
                "survival_status": r.survival_status,
            })

        if not rows:
            return pd.DataFrame(columns=["scenario_id", "portfolio_id", "scenario_type", "max_drawdown_pct", "survival_status"])

        return pd.DataFrame(rows)
