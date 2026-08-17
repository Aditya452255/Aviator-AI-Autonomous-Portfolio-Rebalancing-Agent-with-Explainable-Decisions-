"""Performance Statistics analytics reporting strategy performance comparison tables."""

from typing import Dict, List
import pandas as pd
from src.core.logger import get_logger
from src.models.backtest_result import StrategyPerformance

logger = get_logger(__name__)


class PerformanceStatistics:
    """Enterprise Performance Statistics analytics engine."""

    def compute_strategy_comparison_df(self, perfs: List[StrategyPerformance]) -> pd.DataFrame:
        """Compute strategy performance summary DataFrame.

        Args:
            perfs: List of StrategyPerformance objects.

        Returns:
            DataFrame comparing strategies.
        """
        rows = []
        for p in perfs:
            rows.append({
                "strategy_name": p.strategy_name,
                "cagr_pct": round(p.cagr * 100.0, 2),
                "volatility_pct": round(p.volatility * 100.0, 2),
                "sharpe_ratio": p.sharpe_ratio,
                "sortino_ratio": p.sortino_ratio,
                "calmar_ratio": p.calmar_ratio,
                "max_drawdown_pct": round(p.max_drawdown * 100.0, 2),
                "recovery_time_days": p.recovery_time_days,
                "total_trades": p.total_trades_count,
                "transaction_costs": p.total_transaction_costs,
                "net_after_tax_cagr_pct": round(p.net_after_tax_return * 100.0, 2),
            })

        if not rows:
            return pd.DataFrame(columns=["strategy_name", "cagr_pct", "sharpe_ratio", "max_drawdown_pct"])

        return pd.DataFrame(rows)
