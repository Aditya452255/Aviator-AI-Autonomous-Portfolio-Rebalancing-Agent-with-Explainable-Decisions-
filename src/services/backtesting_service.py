"""Enterprise Backtesting Service orchestrating Phase 7 simulation, strategy comparisons, stress tests, and performance exports."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

from src.analytics.benchmark_statistics import BenchmarkStatistics
from src.analytics.performance_statistics import PerformanceStatistics
from src.analytics.scenario_statistics import ScenarioStatistics
from src.backtesting.agent_evaluator import AgentPerformanceEvaluator
from src.backtesting.benchmark_engine import BenchmarkEngine
from src.backtesting.historical_replay import HistoricalReplayEngine
from src.backtesting.optimization_evaluator import OptimizationQualityEvaluator
from src.backtesting.performance_calculator import PerformanceCalculator
from src.backtesting.return_metrics import ReturnMetricsCalculator
from src.backtesting.risk_metrics import RiskMetricsCalculator
from src.backtesting.scenario_engine import ScenarioEngine
from src.backtesting.strategy_runner import StrategyRunner
from src.backtesting.stress_testing import StressTestEngine
from src.core.config import AppConfig, load_config, _load_yaml_file
from src.core.logger import get_logger
from src.core.utils import Timer
from src.memory.decision_memory import FinalDecisionPackage
from src.models.backtest_result import BacktestResult, StrategyPerformance
from src.models.benchmark_result import BenchmarkResult
from src.models.optimization_result import OptimizationResult
from src.models.portfolio import Portfolio
from src.models.scenario_result import ScenarioResult, ScenarioType

logger = get_logger(__name__)


class BacktestingService:
    """Enterprise service executing Phase 7 Backtesting, Simulation & Performance Evaluation Engine."""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or load_config()
        self.output_dir = Path(self.config.storage.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        config_path = Path("config")
        bt_cfg = _load_yaml_file(config_path / "backtesting.yaml") if (config_path / "backtesting.yaml").exists() else {}
        sc_cfg = _load_yaml_file(config_path / "scenarios.yaml") if (config_path / "scenarios.yaml").exists() else {}
        bm_cfg = _load_yaml_file(config_path / "benchmarks.yaml") if (config_path / "benchmarks.yaml").exists() else {}

        combined_cfg = {**bt_cfg, **sc_cfg, **bm_cfg}

        self.replay_engine = HistoricalReplayEngine()
        self.perf_calc = PerformanceCalculator(risk_free_rate=0.065)
        self.risk_calc = RiskMetricsCalculator()
        self.return_calc = ReturnMetricsCalculator()
        self.strategy_runner = StrategyRunner(performance_calculator=self.perf_calc)
        self.benchmark_engine = BenchmarkEngine(risk_calculator=self.risk_calc)
        self.scenario_engine = ScenarioEngine(perf_calc=self.perf_calc, risk_calc=self.risk_calc)
        self.stress_test_engine = StressTestEngine(scenario_engine=self.scenario_engine)
        self.agent_evaluator = AgentPerformanceEvaluator()
        self.opt_evaluator = OptimizationQualityEvaluator()

        self.perf_stats = PerformanceStatistics()
        self.bench_stats = BenchmarkStatistics()
        self.sc_stats = ScenarioStatistics()

    def run_backtesting_cycle(
        self,
        portfolios: List[Portfolio],
        optimization_results: Optional[List[OptimizationResult]] = None,
        decision_packages: Optional[List[FinalDecisionPackage]] = None,
        trading_days: int = 252,
        save_exports: bool = True,
    ) -> Tuple[List[BacktestResult], Dict]:
        """Execute Phase 7 backtesting cycle across portfolios.

        Args:
            portfolios: List of Portfolio objects.
            optimization_results: List of Phase 3 OptimizationResult objects.
            decision_packages: List of Phase 4 FinalDecisionPackage objects.
            trading_days: Number of trading days.
            save_exports: True to export results to parquet, csv, and json.

        Returns:
            Tuple of (backtest_results_list, summary_analytics_dict).
        """
        with Timer(f"Phase 7 Backtesting Cycle ({len(portfolios)} portfolios)") as timer_metrics:
            logger.info("Executing Phase 7 Backtesting, Simulation & Performance Evaluation Engine Cycle...")

            backtest_results: List[BacktestResult] = []
            all_strategy_perfs: List[StrategyPerformance] = []
            all_benchmark_results: List[BenchmarkResult] = []
            all_scenario_results: List[ScenarioResult] = []

            strategies = [
                "BUY_AND_HOLD",
                "THRESHOLD_REBALANCING",
                "CALENDAR_REBALANCING",
                "AI_OPTIMIZED",
                "TAX_OPTIMIZED",
            ]
            benchmarks = ["NIFTY_50", "NIFTY_500", "60_40_PORTFOLIO", "EQUAL_WEIGHT", "STATIC_ALLOCATION"]

            for p in portfolios:
                bt_id = f"BT_{p.portfolio_id}"
                strat_perfs: Dict[str, StrategyPerformance] = {}

                # 1. Run Strategy Comparison
                for s_name in strategies:
                    perf = self.strategy_runner.run_strategy(
                        portfolio=p,
                        strategy_name=s_name,
                        trading_days=trading_days,
                    )
                    strat_perfs[s_name] = perf
                    all_strategy_perfs.append(perf)

                # 2. Find best strategy by Sharpe Ratio
                best_strat = max(strat_perfs.values(), key=lambda x: x.sharpe_ratio).strategy_name
                ai_perf = strat_perfs.get("AI_OPTIMIZED", list(strat_perfs.values())[0])

                # 3. Benchmark Comparisons
                for bm_name in benchmarks:
                    bm_res = self.benchmark_engine.compare_benchmark(
                        portfolio_id=p.portfolio_id,
                        portfolio_cagr=ai_perf.cagr,
                        portfolio_volatility=ai_perf.volatility,
                        benchmark_name=bm_name,
                    )
                    all_benchmark_results.append(bm_res)

                # 4. Stress Tests & Scenarios
                st_results = self.stress_test_engine.run_stress_tests(p.portfolio_id, p.total_market_value)
                all_scenario_results.extend(st_results)

                bt_result = BacktestResult(
                    backtest_id=bt_id,
                    portfolio_id=p.portfolio_id,
                    replay_frequency="DAILY",
                    trading_days=trading_days,
                    strategy_performances=strat_perfs,
                    best_strategy=best_strat,
                )
                backtest_results.append(bt_result)

            # 5. Agent & Optimization Evaluations
            agent_metrics = self.agent_evaluator.evaluate_agent_system(decision_packages or [])
            opt_metrics = self.opt_evaluator.evaluate_optimization_engine(optimization_results or [])

            # Compute DataFrames
            df_strat = self.perf_stats.compute_strategy_comparison_df(all_strategy_perfs)
            df_bench = self.bench_stats.compute_benchmark_comparison_df(all_benchmark_results)
            df_scen = self.sc_stats.compute_scenario_summary_df(all_scenario_results)

            summary_analytics = {
                "cycle_metrics": {
                    "total_portfolios_backtested": len(portfolios),
                    "trading_days_simulated": trading_days,
                    "strategies_evaluated_count": len(strategies),
                    "scenarios_evaluated_count": len(all_scenario_results),
                    "execution_time_seconds": timer_metrics.get("elapsed_seconds", 0.0),
                },
                "agent_evaluation": agent_metrics,
                "optimization_evaluation": opt_metrics,
            }

            if save_exports:
                self.export_results(backtest_results, df_strat, df_bench, df_scen, agent_metrics, summary_analytics)

            logger.info("Phase 7 Backtesting & Performance Evaluation Engine successfully completed.")
            return backtest_results, summary_analytics

    def export_results(
        self,
        results: List[BacktestResult],
        df_strat: pd.DataFrame,
        df_bench: pd.DataFrame,
        df_scen: pd.DataFrame,
        agent_metrics: Dict,
        summary_analytics: Dict,
    ) -> None:
        """Export Phase 7 backtesting datasets to Parquet, CSV, and JSON.

        Args:
            results: List of BacktestResult domain models.
            df_strat: Strategy comparison DataFrame.
            df_bench: Benchmark comparison DataFrame.
            df_scen: Scenario results DataFrame.
            agent_metrics: Agent evaluation metrics dict.
            summary_analytics: Summary metrics dict.
        """
        with Timer("Exporting Phase 7 Backtesting Datasets"):
            bt_rows = []
            for r in results:
                bt_rows.append({
                    "backtest_id": r.backtest_id,
                    "portfolio_id": r.portfolio_id,
                    "replay_frequency": r.replay_frequency,
                    "trading_days": r.trading_days,
                    "best_strategy": r.best_strategy,
                })

            df_bt = pd.DataFrame(bt_rows)

            df_bt.to_parquet(self.output_dir / "backtest_results.parquet", index=False)
            df_scen.to_parquet(self.output_dir / "scenario_results.parquet", index=False)

            if self.config.storage.save_csv:
                df_bt.to_csv(self.output_dir / "backtest_results.csv", index=False)
                df_scen.to_csv(self.output_dir / "scenario_results.csv", index=False)

            df_strat.to_csv(self.output_dir / "strategy_comparison.csv", index=False)
            df_bench.to_csv(self.output_dir / "benchmark_comparison.csv", index=False)

            df_agent = pd.DataFrame([agent_metrics])
            df_agent.to_csv(self.output_dir / "agent_evaluation.csv", index=False)

            with open(self.output_dir / "performance_metrics.json", "w", encoding="utf-8") as f:
                json.dump(summary_analytics, f, indent=2)

            logger.info(f"Saved Phase 7 backtesting outputs to {self.output_dir}")
