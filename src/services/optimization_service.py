"""Enterprise Optimization Service orchestrating Phase 3 portfolio rebalancing, trade generation, and exports."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

from src.analytics.cost_analysis import CostAnalysis
from src.analytics.optimization_statistics import OptimizationStatistics
from src.analytics.tax_analysis import TaxAnalysis
from src.core.config import AppConfig, load_config, _load_yaml_file
from src.core.exceptions import ValidationError
from src.core.logger import get_logger
from src.core.utils import Timer
from src.models.client import ClientProfile
from src.models.execution_plan import ExecutionPlan
from src.models.optimization_result import OptimizationResult, OptimizationStrategy
from src.models.portfolio import Portfolio
from src.models.rebalancing_request import RebalancingRequest
from src.models.risk_category import RiskCategory
from src.models.security import Security
from src.models.trade import Trade
from src.optimization.portfolio_rebalancer import PortfolioRebalancer

logger = get_logger(__name__)


class OptimizationService:
    """Enterprise orchestration service executing Phase 3 Portfolio Optimization & Trade Generation Engine."""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or load_config()
        self.output_dir = Path(self.config.storage.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Build risk category lookup
        self.risk_categories: Dict[str, RiskCategory] = {}
        for key, item in self.config.risk_categories.items():
            self.risk_categories[key] = RiskCategory(
                id=item.id,
                name=item.name,
                target_equity=item.target_equity,
                target_fixed_income=item.target_fixed_income,
                target_alternatives=item.target_alternatives,
                target_cash=item.target_cash,
                drift_threshold=item.drift_threshold,
            )

        # Load Phase 3 YAML configurations
        config_path = Path("config")
        opt_cfg = _load_yaml_file(config_path / "optimization.yaml") if (config_path / "optimization.yaml").exists() else {}
        tax_cfg = _load_yaml_file(config_path / "tax_rules.yaml") if (config_path / "tax_rules.yaml").exists() else {}
        exec_cfg = _load_yaml_file(config_path / "execution_rules.yaml") if (config_path / "execution_rules.yaml").exists() else {}

        combined_cfg = {**opt_cfg, **tax_cfg, **exec_cfg}
        self.rebalancer = PortfolioRebalancer(config=combined_cfg)
        self.opt_stats = OptimizationStatistics()
        self.cost_analyzer = CostAnalysis()
        self.tax_analyzer = TaxAnalysis()

    def run_optimization_cycle(
        self,
        portfolios: List[Portfolio],
        rebalancing_queue: List[RebalancingRequest],
        clients: Optional[List[ClientProfile]] = None,
        securities: Optional[List[Security]] = None,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        save_exports: bool = True,
    ) -> Tuple[List[OptimizationResult], Dict]:
        """Execute Phase 3 optimization cycle across queue items.

        Args:
            portfolios: Complete list of Portfolio instances.
            rebalancing_queue: Validated RebalancingRequest list from Phase 2.
            clients: List of ClientProfile instances.
            securities: List of Security master instances.
            strategy: OptimizationStrategy choice.
            save_exports: True to persist parquet, csv, and json summaries.

        Returns:
            Tuple of (optimization_results_list, analytics_summary_dict).
        """
        with Timer(f"Phase 3 Optimization Cycle ({len(rebalancing_queue)} queue items)") as timer_metrics:
            logger.info("Executing Phase 3 Portfolio Optimization & Trade Generation Engine Cycle...")

            port_map: Dict[str, Portfolio] = {p.portfolio_id: p for p in portfolios}
            client_map: Dict[str, ClientProfile] = {c.client_id: c for c in (clients or [])}
            sec_map: Dict[str, Security] = {s.ticker: s for s in (securities or [])}

            results: List[OptimizationResult] = []

            for req in rebalancing_queue:
                p = port_map.get(req.portfolio_id)
                if not p:
                    logger.warning(f"Portfolio {req.portfolio_id} from queue not found in active portfolios. Skipping.")
                    continue

                cli = client_map.get(p.client_id)
                rc_key = p.risk_category.value if hasattr(p.risk_category, "value") else str(p.risk_category)
                rc = self.risk_categories.get(rc_key)

                # Run optimization for portfolio
                res = self.rebalancer.rebalance_portfolio(
                    portfolio=p,
                    risk_category=rc,
                    client=cli,
                    securities_map=sec_map,
                    strategy=strategy,
                    priority=req.priority.value if hasattr(req.priority, "value") else str(req.priority),
                )

                # Structured Logging per portfolio
                logger.info(
                    f"Optimized [{p.portfolio_id}] | Strategy: {strategy.value} | Status: {res.solver_status} | "
                    f"Drift: {res.drift_score_before:.4f}->{res.drift_score_after:.4f} | "
                    f"TE: {res.tracking_error_before:.4f}->{res.tracking_error_after:.4f} | "
                    f"Cost: {res.total_estimated_cost:,.2f} | Tax: {res.total_tax_impact:,.2f}"
                )

                results.append(res)

            # Compute Analytics
            stats_summary = self.opt_stats.compute_summary_statistics(results)
            df_cost = self.cost_analyzer.compute_cost_summary(results)
            df_tax = self.tax_analyzer.compute_tax_summary(results)

            analytics_summary = {
                "cycle_metrics": {
                    "portfolios_optimized": len(results),
                    "execution_time_seconds": timer_metrics.get("elapsed_seconds", 0.0),
                },
                "optimization_statistics": stats_summary,
                "cost_summary": df_cost.to_dict(orient="records") if not df_cost.empty else [],
                "tax_summary": df_tax.to_dict(orient="records") if not df_tax.empty else [],
            }

            if save_exports:
                self.export_results(results, analytics_summary, df_cost, df_tax)

            logger.info("Phase 3 Portfolio Optimization & Trade Generation Engine successfully finished.")
            return results, analytics_summary

    def export_results(
        self,
        results: List[OptimizationResult],
        analytics_summary: Dict,
        df_cost: pd.DataFrame,
        df_tax: pd.DataFrame,
    ) -> None:
        """Export Phase 3 results to Parquet, CSV, and JSON formats.

        Args:
            results: List of OptimizationResult objects.
            analytics_summary: Summary metrics dictionary.
            df_cost: Cost analysis DataFrame.
            df_tax: Tax analysis DataFrame.
        """
        with Timer("Exporting Phase 3 Optimization Datasets"):
            # 1. Export Optimized Portfolios Summary
            opt_rows = []
            trade_rows = []
            plan_rows = []

            for r in results:
                opt_rows.append({
                    "optimization_id": r.optimization_id,
                    "portfolio_id": r.portfolio_id,
                    "strategy": r.strategy.value if hasattr(r.strategy, "value") else str(r.strategy),
                    "solver_status": r.solver_status,
                    "optimization_time_seconds": r.optimization_time_seconds,
                    "tracking_error_before": r.tracking_error_before,
                    "tracking_error_after": r.tracking_error_after,
                    "drift_score_before": r.drift_score_before,
                    "drift_score_after": r.drift_score_after,
                    "turnover": r.turnover,
                    "total_estimated_cost": r.total_estimated_cost,
                    "total_tax_impact": r.total_tax_impact,
                    "trades_count": len(r.trades),
                    "violations_count": len(r.constraint_violations),
                    "optimized_cat_weights_json": json.dumps(r.optimized_weights),
                })

                for t in r.trades:
                    trade_rows.append({
                        "trade_id": t.trade_id,
                        "portfolio_id": t.portfolio_id,
                        "ticker": t.ticker,
                        "action": t.action.value if hasattr(t.action, "value") else str(t.action),
                        "shares": t.shares,
                        "current_weight": t.current_weight,
                        "target_weight": t.target_weight,
                        "weight_change": t.weight_change,
                        "price": t.price,
                        "market_value": t.market_value,
                        "estimated_cost": t.estimated_cost,
                        "tax_impact": t.tax_impact,
                        "reason": t.reason,
                    })

                if r.execution_plan:
                    ep = r.execution_plan
                    plan_rows.append({
                        "plan_id": ep.plan_id,
                        "portfolio_id": ep.portfolio_id,
                        "strategy": ep.strategy.value if hasattr(ep.strategy, "value") else str(ep.strategy),
                        "execution_window": ep.execution_window,
                        "trade_priority": ep.trade_priority,
                        "estimated_completion_minutes": ep.estimated_completion_minutes,
                        "execution_risk_rating": ep.execution_risk_rating,
                        "total_estimated_cost": ep.total_estimated_cost,
                        "slices_count": len(ep.slices),
                    })

            df_opt = pd.DataFrame(opt_rows)
            df_trade = pd.DataFrame(trade_rows)
            df_plan = pd.DataFrame(plan_rows)

            df_opt.to_parquet(self.output_dir / "optimized_portfolios.parquet", index=False)
            df_trade.to_parquet(self.output_dir / "trade_list.parquet", index=False)
            df_plan.to_parquet(self.output_dir / "execution_plan.parquet", index=False)

            if self.config.storage.save_csv:
                df_opt.to_csv(self.output_dir / "optimized_portfolios.csv", index=False)
                df_trade.to_csv(self.output_dir / "trade_list.csv", index=False)
                df_plan.to_csv(self.output_dir / "execution_plan.csv", index=False)

            df_cost.to_csv(self.output_dir / "cost_analysis.csv", index=False)
            df_tax.to_csv(self.output_dir / "tax_analysis.csv", index=False)

            with open(self.output_dir / "optimization_summary.json", "w", encoding="utf-8") as f:
                json.dump(analytics_summary, f, indent=2)

            logger.info(f"Saved Phase 3 optimization datasets to {self.output_dir}")
