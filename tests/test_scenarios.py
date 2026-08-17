"""Unit tests for ScenarioEngine and StressTestEngine."""

import pytest
from src.backtesting.scenario_engine import ScenarioEngine
from src.backtesting.stress_testing import StressTestEngine
from src.models.scenario_result import ScenarioResult, ScenarioType


def test_scenario_and_stress_testing() -> None:
    """Test scenario simulation and stress test crash evaluations."""
    engine = ScenarioEngine()
    res_bull = engine.run_scenario("PORT_001", 100000.0, ScenarioType.BULL_MARKET)
    res_bear = engine.run_scenario("PORT_001", 100000.0, ScenarioType.BEAR_MARKET)

    assert isinstance(res_bull, ScenarioResult)
    assert res_bull.portfolio_return > res_bear.portfolio_return

    stress_engine = StressTestEngine(scenario_engine=engine)
    stress_results = stress_engine.run_stress_tests("PORT_001", 100000.0)

    assert len(stress_results) == 4
    assert any(r.scenario_type == ScenarioType.BLACK_SWAN for r in stress_results)
