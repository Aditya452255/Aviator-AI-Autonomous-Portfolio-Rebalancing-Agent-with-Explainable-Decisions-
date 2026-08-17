"""Portfolio Rebalancer orchestrator combining optimization, constraints, tax, costs, and execution planning."""

import time
from typing import Dict, List, Optional
import numpy as np

from src.core.logger import get_logger
from src.models.client import ClientProfile
from src.models.optimization_result import OptimizationResult, OptimizationStrategy
from src.models.portfolio import Portfolio
from src.models.risk_category import RiskCategory
from src.models.security import Security
from src.optimization.constraint_manager import ConstraintManager
from src.optimization.cost_estimator import CostEstimator
from src.optimization.execution_planner import ExecutionPlanner
from src.optimization.liquidity_manager import LiquidityManager
from src.optimization.portfolio_optimizer import PortfolioOptimizer
from src.optimization.tax_lot_manager import TaxLotManager
from src.optimization.tax_optimizer import TaxOptimizer
from src.optimization.trade_generator import TradeGenerator
from src.optimization.trade_validator import TradeValidator

logger = get_logger(__name__)


class PortfolioRebalancer:
    """Master portfolio rebalancing orchestrator executing full Phase 3 trade optimization workflow."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.optimizer = PortfolioOptimizer(config=self.config)
        self.constraint_manager = ConstraintManager()
        self.cost_estimator = CostEstimator(execution_rules=self.config)
        self.tax_lot_manager = TaxLotManager()
        self.tax_optimizer = TaxOptimizer(tax_rules=self.config)
        self.liquidity_manager = LiquidityManager(execution_rules=self.config)
        self.trade_generator = TradeGenerator(cost_estimator=self.cost_estimator)
        self.trade_validator = TradeValidator()
        self.execution_planner = ExecutionPlanner(liquidity_manager=self.liquidity_manager)

    def rebalance_portfolio(
        self,
        portfolio: Portfolio,
        risk_category: Optional[RiskCategory] = None,
        client: Optional[ClientProfile] = None,
        securities_map: Optional[Dict[str, Security]] = None,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        priority: str = "High",
    ) -> OptimizationResult:
        """Run full portfolio optimization, constraint validation, tax evaluation, and execution planning.

        Args:
            portfolio: Target portfolio domain model.
            risk_category: Target RiskCategory definition.
            client: Optional ClientProfile.
            securities_map: Map of ticker to Security objects.
            strategy: OptimizationStrategy enum choice.
            priority: Priority level string.

        Returns:
            Validated OptimizationResult domain model.
        """
        start_time = time.perf_counter()
        opt_id = f"OPT_{portfolio.portfolio_id}"

        # 1. Pre-Optimization Metrics
        w_curr = np.array([h.current_weight for h in portfolio.holdings])
        w_tgt = np.array([h.target_weight for h in portfolio.holdings])

        drift_score_before = float(np.sqrt(np.mean((w_curr - w_tgt) ** 2)))
        te_before = float(np.std(w_curr - w_tgt))

        # 2. Run Convex Optimization
        opt_cat_w, opt_sec_w, solver_status = self.optimizer.optimize_portfolio(
            portfolio=portfolio,
            risk_category=risk_category,
            strategy=strategy,
        )

        # 3. Generate Trades
        trades = self.trade_generator.generate_trades(
            portfolio=portfolio,
            optimized_sec_weights=opt_sec_w,
            securities_map=securities_map,
        )

        # 4. Tax Evaluation & Lot Matching
        tax_lots_map = self.tax_lot_manager.generate_synthetic_tax_lots(portfolio)
        total_tax_impact = 0.0
        for trade in trades:
            lots = tax_lots_map.get(trade.ticker, [])
            tax_imp, _ = self.tax_optimizer.evaluate_trade_tax_impact(trade, lots)
            trade.tax_impact = tax_imp
            total_tax_impact += tax_imp

        # 5. Validate Trades
        if trades:
            self.trade_validator.validate_trades(trades=trades, portfolio=portfolio)

        # 6. Generate Execution Plan
        exec_plan = self.execution_planner.generate_execution_plan(
            portfolio=portfolio,
            trades=trades,
            priority=priority,
            securities_map=securities_map,
        )

        # 7. Post-Optimization Metrics
        opt_sec_array = np.array([opt_sec_w.get(h.ticker, h.current_weight) for h in portfolio.holdings])
        drift_score_after = float(np.sqrt(np.mean((opt_sec_array - w_tgt) ** 2)))
        te_after = float(np.std(opt_sec_array - w_tgt))
        turnover = float(np.sum(np.abs(opt_sec_array - w_curr)))

        # 8. Constraint Validation
        violations = self.constraint_manager.validate_constraints(
            portfolio=portfolio,
            proposed_weights=opt_sec_w,
            client=client,
            securities_map=securities_map,
        )

        elapsed = time.perf_counter() - start_time
        total_cost = sum(t.estimated_cost for t in trades)

        return OptimizationResult(
            optimization_id=opt_id,
            portfolio_id=portfolio.portfolio_id,
            strategy=strategy,
            solver_status=solver_status,
            optimization_time_seconds=round(elapsed, 4),
            tracking_error_before=round(te_before, 4),
            tracking_error_after=round(te_after, 4),
            drift_score_before=round(drift_score_before, 4),
            drift_score_after=round(drift_score_after, 4),
            turnover=round(turnover, 4),
            total_estimated_cost=round(total_cost, 2),
            total_tax_impact=round(total_tax_impact, 2),
            optimized_weights=opt_cat_w,
            security_target_weights=opt_sec_w,
            trades=trades,
            execution_plan=exec_plan,
            constraint_violations=violations,
        )
