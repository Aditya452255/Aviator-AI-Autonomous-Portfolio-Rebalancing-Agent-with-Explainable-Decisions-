"""Execution Planner constructing TWAP, VWAP, and Multi-Day algorithmic execution plans."""

from typing import Dict, List, Optional
from src.core.logger import get_logger
from src.models.execution_plan import ExecutionPlan, ExecutionSlice, ExecutionStrategy
from src.models.portfolio import Portfolio
from src.models.trade import Trade
from src.optimization.liquidity_manager import LiquidityManager

logger = get_logger(__name__)


class ExecutionPlanner:
    """Enterprise execution planner constructing algorithmic trade execution plans."""

    def __init__(self, liquidity_manager: Optional[LiquidityManager] = None) -> None:
        self.liquidity_manager = liquidity_manager or LiquidityManager()

    def generate_execution_plan(
        self,
        portfolio: Portfolio,
        trades: List[Trade],
        priority: str = "High",
        securities_map: Optional[Dict] = None,
    ) -> ExecutionPlan:
        """Construct execution plan with algorithmic strategy selection and order slicing.

        Args:
            portfolio: Target portfolio instance.
            trades: Generated Trade list.
            priority: Overall rebalancing priority level.
            securities_map: Optional map of ticker to Security objects.

        Returns:
            Validated ExecutionPlan domain model object.
        """
        plan_id = f"PLAN_{portfolio.portfolio_id}"

        if not trades:
            return ExecutionPlan(
                plan_id=plan_id,
                portfolio_id=portfolio.portfolio_id,
                strategy=ExecutionStrategy.SINGLE_IMMEDIATE,
                execution_window="Immediate",
                trade_priority=priority,
                estimated_completion_minutes=0.0,
                execution_risk_rating="LOW",
                total_estimated_cost=0.0,
                slices=[],
            )

        total_trade_value = sum(t.market_value for t in trades)
        total_cost = sum(t.estimated_cost for t in trades)

        # Determine highest risk / strategy among trades
        max_part_rate = 0.0
        for t in trades:
            sec = securities_map.get(t.ticker) if securities_map else None
            adv = sec.average_daily_volume if sec else 1e7
            liq_info = self.liquidity_manager.evaluate_trade_liquidity(t, avg_daily_volume=adv)
            part_rate = float(liq_info["participation_rate"])
            if part_rate > max_part_rate:
                max_part_rate = part_rate

        if max_part_rate > 0.20:
            strategy = ExecutionStrategy.MULTI_DAY
            window_str = "3 Days"
            completion_mins = 1080.0  # 18 hours market time
            risk_rating = "HIGH"
            slice_count = 10
        elif max_part_rate > 0.08:
            strategy = ExecutionStrategy.VWAP
            window_str = "1 Trading Day"
            completion_mins = 360.0  # 6 hours
            risk_rating = "MEDIUM"
            slice_count = 6
        elif max_part_rate > 0.02:
            strategy = ExecutionStrategy.TWAP
            window_str = "2 Hours"
            completion_mins = 120.0
            risk_rating = "LOW"
            slice_count = 4
        else:
            strategy = ExecutionStrategy.SINGLE_IMMEDIATE
            window_str = "15 Minutes"
            completion_mins = 15.0
            risk_rating = "LOW"
            slice_count = 1

        # Generate order slices
        slices: List[ExecutionSlice] = []
        pct_per_slice = 1.0 / slice_count

        for s_idx in range(1, slice_count + 1):
            slice_id = f"SLC_{plan_id}_{s_idx:02d}"
            start_m = (s_idx - 1) * (completion_mins / slice_count)
            end_m = s_idx * (completion_mins / slice_count)
            time_win = f"{start_m:.0f}m-{end_m:.0f}m"

            slice_obj = ExecutionSlice(
                slice_id=slice_id,
                slice_index=s_idx,
                time_window=time_win,
                quantity_pct=round(pct_per_slice, 4),
                target_shares=round(sum(t.shares for t in trades) * pct_per_slice, 4),
                estimated_impact_bps=round(max_part_rate * 10.0, 2),
            )
            slices.append(slice_obj)

        return ExecutionPlan(
            plan_id=plan_id,
            portfolio_id=portfolio.portfolio_id,
            strategy=strategy,
            execution_window=window_str,
            trade_priority=priority,
            estimated_completion_minutes=round(completion_mins, 1),
            execution_risk_rating=risk_rating,
            total_estimated_cost=round(total_cost, 2),
            slices=slices,
        )
