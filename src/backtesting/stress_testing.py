"""Stress Testing Engine evaluating extreme market crashes and liquidity freezes."""

from typing import Dict, List, Optional
from src.backtesting.scenario_engine import ScenarioEngine
from src.core.logger import get_logger
from src.models.scenario_result import ScenarioResult, ScenarioType

logger = get_logger(__name__)


class StressTestEngine:
    """Enterprise Stress Testing Engine running portfolio crash simulations."""

    def __init__(self, scenario_engine: Optional[ScenarioEngine] = None) -> None:
        self.sc_engine = scenario_engine or ScenarioEngine()

    def run_stress_tests(self, portfolio_id: str, portfolio_value: float) -> List[ScenarioResult]:
        """Run battery of extreme stress test scenarios for a portfolio.

        Args:
            portfolio_id: Target portfolio ID.
            portfolio_value: Initial market value.

        Returns:
            List of ScenarioResult objects.
        """
        stress_types = [
            ScenarioType.CRASH_20_PCT,
            ScenarioType.CRASH_35_PCT,
            ScenarioType.BLACK_SWAN,
            ScenarioType.LIQUIDITY_CRISIS,
        ]

        results: List[ScenarioResult] = []
        for st in stress_types:
            res = self.sc_engine.run_scenario(
                portfolio_id=portfolio_id,
                portfolio_value=portfolio_value,
                scenario_type=st,
            )
            results.append(res)

        return results
