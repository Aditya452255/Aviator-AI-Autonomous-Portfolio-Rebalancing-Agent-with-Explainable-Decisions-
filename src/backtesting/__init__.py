"""Backtesting package containing historical replay, strategy runner, benchmarks, scenario engine, and metrics."""

from src.backtesting.historical_replay import HistoricalReplayEngine
from src.backtesting.strategy_runner import StrategyRunner
from src.backtesting.benchmark_engine import BenchmarkEngine
from src.backtesting.scenario_engine import ScenarioEngine
from src.backtesting.market_simulator import ScenarioMarketSimulator
from src.backtesting.stress_testing import StressTestEngine
from src.backtesting.performance_calculator import PerformanceCalculator
from src.backtesting.risk_metrics import RiskMetricsCalculator
from src.backtesting.return_metrics import ReturnMetricsCalculator
from src.backtesting.tax_performance import TaxPerformanceEvaluator
from src.backtesting.agent_evaluator import AgentPerformanceEvaluator
from src.backtesting.optimization_evaluator import OptimizationQualityEvaluator

__all__ = [
    "HistoricalReplayEngine",
    "StrategyRunner",
    "BenchmarkEngine",
    "ScenarioEngine",
    "ScenarioMarketSimulator",
    "StressTestEngine",
    "PerformanceCalculator",
    "RiskMetricsCalculator",
    "ReturnMetricsCalculator",
    "TaxPerformanceEvaluator",
    "AgentPerformanceEvaluator",
    "OptimizationQualityEvaluator",
]
