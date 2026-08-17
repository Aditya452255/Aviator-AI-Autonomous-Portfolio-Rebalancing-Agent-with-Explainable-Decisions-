"""Liquidity Manager analyzing volume, participation rate, market impact, and execution strategy."""

from typing import Dict, Optional
import numpy as np

from src.core.logger import get_logger
from src.models.execution_plan import ExecutionStrategy
from src.models.trade import Trade

logger = get_logger(__name__)


class LiquidityManager:
    """Enterprise liquidity manager computing market impact, participation rates, and algorithmic execution strategy."""

    def __init__(self, execution_rules: Optional[Dict] = None) -> None:
        cfg = execution_rules or {}
        rules = cfg.get("execution_rules", {})
        self.max_adv_participation = rules.get("max_adv_participation_rate", 0.10)

    def evaluate_trade_liquidity(
        self,
        trade: Trade,
        avg_daily_volume: float = 1e7,
        liquidity_score: float = 80.0,
    ) -> Dict[str, float | str]:
        """Evaluate liquidity metrics and recommend execution strategy.

        Args:
            trade: Trade order instance.
            avg_daily_volume: Security average daily volume in base currency.
            liquidity_score: Liquidity rating (1-100).

        Returns:
            Dictionary containing participation rate, slippage, impact, and strategy.
        """
        participation_rate = trade.market_value / max(1.0, avg_daily_volume)

        # Slippage estimation: square root of participation rate
        slippage_bps = float(np.clip(15.0 * np.sqrt(participation_rate) * (100.0 / max(1.0, liquidity_score)), 1.0, 300.0))
        slippage_cost = trade.market_value * (slippage_bps / 10000.0)

        # Determine execution strategy based on participation rate
        if participation_rate > 0.25:
            rec_strategy = ExecutionStrategy.MULTI_DAY
            risk = "HIGH"
        elif participation_rate > 0.10:
            rec_strategy = ExecutionStrategy.VWAP
            risk = "MEDIUM"
        elif participation_rate > 0.03:
            rec_strategy = ExecutionStrategy.TWAP
            risk = "LOW"
        else:
            rec_strategy = ExecutionStrategy.SINGLE_IMMEDIATE
            risk = "LOW"

        return {
            "participation_rate": round(participation_rate, 4),
            "slippage_bps": round(slippage_bps, 2),
            "slippage_cost": round(slippage_cost, 2),
            "recommended_strategy": rec_strategy.value,
            "risk_rating": risk,
        }
