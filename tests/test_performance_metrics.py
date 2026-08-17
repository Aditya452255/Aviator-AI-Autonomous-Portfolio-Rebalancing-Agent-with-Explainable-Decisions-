"""Unit tests for PerformanceCalculator and RiskMetricsCalculator."""

import numpy as np
import pytest
from src.backtesting.performance_calculator import PerformanceCalculator
from src.backtesting.risk_metrics import RiskMetricsCalculator


def test_performance_and_risk_metrics() -> None:
    """Test CAGR, Sharpe, Sortino, Calmar, Max Drawdown, and VaR calculation."""
    perf_calc = PerformanceCalculator(risk_free_rate=0.065)

    cagr = perf_calc.calculate_cagr(100000.0, 115000.0, 252)
    assert 0.14 <= cagr <= 0.16

    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.01, 252)
    vol = perf_calc.calculate_volatility(returns)
    assert vol > 0.0

    sharpe = perf_calc.calculate_sharpe_ratio(cagr, vol)
    sortino = perf_calc.calculate_sortino_ratio(returns, cagr)
    assert sharpe != 0.0
    assert sortino != 0.0

    path = np.cumprod(1.0 + returns) * 100000.0
    max_dd, rec = perf_calc.calculate_max_drawdown_and_recovery(path)
    assert max_dd >= 0.0

    risk_calc = RiskMetricsCalculator()
    var_95, cvar_95 = risk_calc.calculate_var_and_cvar(returns)
    assert var_95 > 0.0
    assert cvar_95 >= var_95
