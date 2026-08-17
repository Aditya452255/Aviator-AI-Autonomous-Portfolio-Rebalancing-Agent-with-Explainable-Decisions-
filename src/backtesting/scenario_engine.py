"""Scenario Engine executing market regime simulations and generating ScenarioResult models."""

from typing import Dict, List, Optional
from src.backtesting.market_simulator import ScenarioMarketSimulator
from src.backtesting.performance_calculator import PerformanceCalculator
from src.backtesting.risk_metrics import RiskMetricsCalculator
from src.core.logger import get_logger
from src.models.scenario_result import ScenarioResult, ScenarioType

logger = get_logger(__name__)


class ScenarioEngine:
    """Enterprise Scenario Engine running regime simulations."""

    def __init__(
        self,
        market_sim: Optional[ScenarioMarketSimulator] = None,
        perf_calc: Optional[PerformanceCalculator] = None,
        risk_calc: Optional[RiskMetricsCalculator] = None,
    ) -> None:
        self.sim = market_sim or ScenarioMarketSimulator()
        self.perf_calc = perf_calc or PerformanceCalculator()
        self.risk_calc = risk_calc or RiskMetricsCalculator()

    def run_scenario(
        self,
        portfolio_id: str,
        portfolio_value: float,
        scenario_type: ScenarioType,
        trading_days: int = 252,
    ) -> ScenarioResult:
        """Run specific scenario regime simulation.

        Args:
            portfolio_id: Target portfolio ID.
            portfolio_value: Initial capital.
            scenario_type: ScenarioType enum choice.
            trading_days: Number of trading days.

        Returns:
            ScenarioResult domain model.
        """
        sc_name = scenario_type.value if hasattr(scenario_type, "value") else str(scenario_type)
        sc_id = f"SCEN_{portfolio_id}_{sc_name}"

        annual_ret = 0.12
        annual_vol = 0.16
        shock = 0.0

        if scenario_type == ScenarioType.BULL_MARKET:
            annual_ret = 0.28
            annual_vol = 0.12
        elif scenario_type == ScenarioType.BEAR_MARKET:
            annual_ret = -0.22
            annual_vol = 0.26
        elif scenario_type == ScenarioType.SIDEWAYS:
            annual_ret = 0.02
            annual_vol = 0.10
        elif scenario_type == ScenarioType.HIGH_INFLATION:
            annual_ret = -0.05
            annual_vol = 0.20
        elif scenario_type == ScenarioType.INTEREST_RATE_SHOCK:
            annual_ret = -0.08
            annual_vol = 0.18
        elif scenario_type == ScenarioType.LIQUIDITY_CRISIS:
            annual_ret = -0.15
            annual_vol = 0.28
        elif scenario_type == ScenarioType.SECTOR_CRASH:
            annual_ret = -0.12
            annual_vol = 0.24
        elif scenario_type == ScenarioType.BLACK_SWAN:
            annual_ret = -0.30
            annual_vol = 0.35
            shock = -0.30

        path = self.sim.simulate_regime_path(
            initial_value=portfolio_value,
            days=trading_days,
            annual_return=annual_ret,
            annual_volatility=annual_vol,
            shock_pct=shock,
        )

        daily_returns = np.diff(path) / path[:-1]
        final_ret = float((path[-1] - portfolio_value) / portfolio_value)
        max_dd, rec_days = self.perf_calc.calculate_max_drawdown_and_recovery(path)
        var_95, cvar_95 = self.risk_calc.calculate_var_and_cvar(daily_returns)

        survival = "PASSED" if max_dd < 0.40 else "CRITICAL"

        return ScenarioResult(
            scenario_id=sc_id,
            portfolio_id=portfolio_id,
            scenario_type=scenario_type,
            portfolio_return=round(final_ret, 4),
            max_drawdown=round(max_dd, 4),
            var_95=var_95,
            cvar_95=cvar_95,
            recovery_days=rec_days,
            survival_status=survival,
        )


import numpy as np
