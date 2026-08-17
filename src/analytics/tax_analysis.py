"""Tax Analysis analytics reporting capital gains, tax loss harvesting, and net tax impacts."""

from typing import List
import pandas as pd

from src.core.logger import get_logger
from src.models.optimization_result import OptimizationResult

logger = get_logger(__name__)


class TaxAnalysis:
    """Enterprise tax analysis engine reporting realized capital gains and tax optimization metrics."""

    def compute_tax_summary(self, results: List[OptimizationResult]) -> pd.DataFrame:
        """Compute portfolio-level tax liability and tax loss harvesting summary.

        Args:
            results: List of OptimizationResult instances.

        Returns:
            DataFrame containing tax impact breakdown per portfolio.
        """
        rows = []
        for r in results:
            total_trade_val = sum(t.market_value for t in r.trades)
            rows.append({
                "portfolio_id": r.portfolio_id,
                "strategy": r.strategy.value if hasattr(r.strategy, "value") else str(r.strategy),
                "total_trades_count": len(r.trades),
                "total_trade_volume": round(total_trade_val, 2),
                "total_tax_impact": r.total_tax_impact,
                "estimated_transaction_cost": r.total_estimated_cost,
            })

        return pd.DataFrame(rows)
