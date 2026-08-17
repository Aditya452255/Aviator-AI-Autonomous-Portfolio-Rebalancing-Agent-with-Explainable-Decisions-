"""Convex Portfolio Optimizer utilizing CVXPY with SciPy quadratic programming fallback."""

from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import minimize

try:
    import cvxpy as cp
    HAS_CVXPY = True
except ImportError:
    HAS_CVXPY = False

from src.core.constants import AssetCategory
from src.core.logger import get_logger
from src.models.optimization_result import OptimizationStrategy
from src.models.portfolio import Portfolio
from src.models.risk_category import RiskCategory

logger = get_logger(__name__)


class PortfolioOptimizer:
    """Enterprise convex portfolio optimizer implementing multi-objective portfolio rebalancing."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}
        opt_cfg = self.config.get("optimization", {})
        self.max_turnover = opt_cfg.get("max_turnover", 0.25)
        self.max_pos_weight = opt_cfg.get("max_position_weight", 0.15)
        self.cash_reserve_pct = opt_cfg.get("cash_reserve_pct", 0.05)

        # Objective weights
        self.w_te = opt_cfg.get("tracking_error_weight", 0.30)
        self.w_drift = opt_cfg.get("drift_penalty_weight", 0.40)
        self.w_cost = opt_cfg.get("cost_penalty_weight", 0.15)
        self.w_tax = opt_cfg.get("tax_penalty_weight", 0.15)

    def optimize_portfolio(
        self,
        portfolio: Portfolio,
        risk_category: Optional[RiskCategory] = None,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    ) -> Tuple[Dict[str, float], Dict[str, float], str]:
        """Run convex optimization for a portfolio according to specified strategy.

        Args:
            portfolio: Portfolio domain model.
            risk_category: Target RiskCategory definition.
            strategy: OptimizationStrategy enum choice.

        Returns:
            Tuple of (category_weights_map, security_weights_map, solver_status_string).
        """
        # Determine target category weights
        if risk_category:
            tgt_cat_w = {
                AssetCategory.EQUITY.value: risk_category.target_equity,
                AssetCategory.FIXED_INCOME.value: risk_category.target_fixed_income,
                AssetCategory.ALTERNATIVES.value: risk_category.target_alternatives,
                AssetCategory.CASH.value: risk_category.target_cash,
            }
        else:
            tgt_cat_w = portfolio.target_weights.copy()

        # Adjust objective coefficients according to selected strategy
        if strategy == OptimizationStrategy.MIN_DRIFT:
            alpha_drift, alpha_cost, alpha_tax = 0.85, 0.05, 0.10
        elif strategy == OptimizationStrategy.MIN_COST:
            alpha_drift, alpha_cost, alpha_tax = 0.20, 0.70, 0.10
        elif strategy == OptimizationStrategy.TAX_OPTIMIZED:
            alpha_drift, alpha_cost, alpha_tax = 0.20, 0.10, 0.70
        else:  # BALANCED
            alpha_drift, alpha_cost, alpha_tax = 0.45, 0.25, 0.30

        # Attempt CVXPY optimization if available
        if HAS_CVXPY:
            try:
                cat_w, sec_w, status = self._solve_cvxpy(
                    portfolio=portfolio,
                    target_category_weights=tgt_cat_w,
                    alpha_drift=alpha_drift,
                    alpha_cost=alpha_cost,
                    alpha_tax=alpha_tax,
                )
                if status in ("OPTIMAL", "OPTIMAL_INACCURATE"):
                    return cat_w, sec_w, status
            except Exception as e:
                logger.debug(f"CVXPY solve fallback to SciPy for {portfolio.portfolio_id}: {e}")

        # SciPy Quadratic Optimization Fallback
        return self._solve_scipy(
            portfolio=portfolio,
            target_category_weights=tgt_cat_w,
            alpha_drift=alpha_drift,
            alpha_cost=alpha_cost,
            alpha_tax=alpha_tax,
        )

    def _solve_cvxpy(
        self,
        portfolio: Portfolio,
        target_category_weights: Dict[str, float],
        alpha_drift: float,
        alpha_cost: float,
        alpha_tax: float,
    ) -> Tuple[Dict[str, float], Dict[str, float], str]:
        """Solve using CVXPY convex solver."""
        n_secs = len(portfolio.holdings)
        w = cp.Variable(n_secs)
        w_curr = np.array([h.current_weight for h in portfolio.holdings])
        w_tgt = np.array([h.target_weight for h in portfolio.holdings])

        # Quadratic Drift Penalty: sum((w - w_tgt)^2)
        obj_drift = cp.sum_squares(w - w_tgt)

        # Turnover Penalty: sum(|w - w_curr|)
        obj_turnover = cp.norm1(w - w_curr)

        # Objective Function
        objective = cp.Minimize(alpha_drift * obj_drift + alpha_cost * 0.1 * obj_turnover)

        # Constraints
        constraints = [
            cp.sum(w) == 1.0 - target_category_weights.get(AssetCategory.CASH.value, 0.05),  # Budget constraint minus cash
            w >= 0.0,  # Long only
            w <= self.max_pos_weight,  # Max position weight
            cp.norm1(w - w_curr) <= self.max_turnover,  # Max turnover constraint
        ]

        prob = cp.Problem(objective, constraints)
        prob.solve(solver=cp.ECOS, verbose=False)

        if prob.status not in ("optimal", "optimal_inaccurate"):
            return {}, {}, f"FAILED_{prob.status.upper()}"

        sec_weights = {h.ticker: round(float(w.value[i]), 6) for i, h in enumerate(portfolio.holdings)}
        cat_weights = self._aggregate_category_weights(portfolio, sec_weights, target_category_weights)

        return cat_weights, sec_weights, "OPTIMAL"

    def _solve_scipy(
        self,
        portfolio: Portfolio,
        target_category_weights: Dict[str, float],
        alpha_drift: float,
        alpha_cost: float,
        alpha_tax: float,
    ) -> Tuple[Dict[str, float], Dict[str, float], str]:
        """Solve using SciPy SLSQP optimization algorithm."""
        n_secs = len(portfolio.holdings)
        w_curr = np.array([h.current_weight for h in portfolio.holdings])
        w_tgt = np.array([h.target_weight for h in portfolio.holdings])
        target_cash_w = target_category_weights.get(AssetCategory.CASH.value, 0.05)
        target_sec_budget = 1.0 - target_cash_w

        def objective_fn(w: np.ndarray) -> float:
            drift_loss = np.sum((w - w_tgt) ** 2)
            turnover_loss = np.sum(np.abs(w - w_curr))
            return alpha_drift * drift_loss + alpha_cost * 0.1 * turnover_loss

        # Equality constraint: sum(w) = target_sec_budget
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - target_sec_budget}]

        # Bounds: 0 <= w_i <= max_pos_weight
        bounds = [(0.0, self.max_pos_weight) for _ in range(n_secs)]

        # Initial guess: current weights normalized to target_sec_budget
        curr_sum = np.sum(w_curr)
        w0 = (w_curr / curr_sum) * target_sec_budget if curr_sum > 0 else np.full(n_secs, target_sec_budget / n_secs)

        res = minimize(objective_fn, w0, method="SLSQP", bounds=bounds, constraints=constraints)

        if not res.success:
            # Fallback to normalized target weights if solver fails
            sec_weights = {h.ticker: round(float(w_tgt[i]), 6) for i, h in enumerate(portfolio.holdings)}
            status = "FEASIBLE_FALLBACK"
        else:
            sec_weights = {h.ticker: round(float(res.x[i]), 6) for i, h in enumerate(portfolio.holdings)}
            status = "OPTIMAL"

        cat_weights = self._aggregate_category_weights(portfolio, sec_weights, target_category_weights)
        return cat_weights, sec_weights, status

    def _aggregate_category_weights(
        self,
        portfolio: Portfolio,
        sec_weights: Dict[str, float],
        target_category_weights: Dict[str, float],
    ) -> Dict[str, float]:
        """Aggregate security weights up to top-level asset categories."""
        cat_weights = {cat.value: 0.0 for cat in AssetCategory}
        for h in portfolio.holdings:
            cat_weights[h.asset_category] += sec_weights.get(h.ticker, 0.0)

        # Cash weight is remaining budget
        cat_weights[AssetCategory.CASH.value] = round(1.0 - sum(sec_weights.values()), 4)
        for k in cat_weights:
            cat_weights[k] = round(cat_weights[k], 4)

        return cat_weights
