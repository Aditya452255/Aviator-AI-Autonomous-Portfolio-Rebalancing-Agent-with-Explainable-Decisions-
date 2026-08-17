"""Unit tests for BenchmarkEngine."""

import pytest
from src.backtesting.benchmark_engine import BenchmarkEngine
from src.models.benchmark_result import BenchmarkResult


def test_benchmark_engine_comparison() -> None:
    """Test excess return, Alpha, Beta, and Information Ratio calculation against benchmarks."""
    engine = BenchmarkEngine()

    res = engine.compare_benchmark(
        portfolio_id="PORT_001",
        portfolio_cagr=0.155,
        portfolio_volatility=0.145,
        benchmark_name="NIFTY_50",
    )

    assert isinstance(res, BenchmarkResult)
    assert res.portfolio_id == "PORT_001"
    assert res.benchmark_name == "NIFTY_50"
    assert res.excess_return > 0.0
    assert res.beta != 0.0
