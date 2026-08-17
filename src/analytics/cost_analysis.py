"""Cost Analysis analytics reporting transaction fee breakdowns across generated trades."""

from typing import List
import pandas as pd

from src.core.logger import get_logger
from src.models.optimization_result import OptimizationResult

logger = get_logger(__name__)


class CostAnalysis:
    """Enterprise cost analysis engine summarizing fee structures and execution slippage."""

    def compute_cost_summary(self, results: List[OptimizationResult]) -> pd.DataFrame:
        """Compute detailed transaction cost breakdown across all optimized portfolio trade lists.

        Args:
            results: List of OptimizationResult instances.

        Returns:
            DataFrame containing aggregated cost components.
        """
        all_trades = []
        for r in results:
            for t in r.trades:
                all_trades.append({
                    "portfolio_id": t.portfolio_id,
                    "trade_id": t.trade_id,
                    "ticker": t.ticker,
                    "action": t.action.value if hasattr(t.action, "value") else str(t.action),
                    "market_value": t.market_value,
                    "estimated_cost": t.estimated_cost,
                    "brokerage_pct": 0.10,
                    "stt_tax": t.market_value * 0.0010 if t.action == "SELL" else 0.0,
                    "tax_impact": t.tax_impact,
                })

        if not all_trades:
            return pd.DataFrame(columns=["portfolio_id", "trade_id", "ticker", "action", "market_value", "estimated_cost"])

        return pd.DataFrame(all_trades)
