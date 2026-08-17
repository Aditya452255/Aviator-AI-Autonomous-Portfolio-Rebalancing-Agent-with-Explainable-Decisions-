"""Enterprise Monitoring Service orchestrating portfolio drift detection, triggers, priority scoring, alerts, and analytics."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

from src.analytics.asset_exposure import AssetExposureAnalyzer
from src.analytics.drift_statistics import DriftStatistics
from src.analytics.sector_exposure import SectorExposureAnalyzer
from src.core.config import AppConfig, load_config, _load_yaml_file
from src.core.exceptions import ValidationError
from src.core.logger import get_logger
from src.core.utils import Timer
from src.models.client import ClientProfile
from src.models.drift import PortfolioDriftMetrics
from src.models.portfolio import Portfolio
from src.models.rebalancing_request import AlertObject, RebalancingRequest
from src.models.risk_category import RiskCategory
from src.models.security import Security
from src.monitoring.alerts import AlertEngine
from src.monitoring.drift_metrics import DriftMetricsAggregator
from src.monitoring.drift_monitor import DriftMonitor
from src.monitoring.priority_engine import PriorityEngine
from src.monitoring.rebalancing_queue import RebalancingQueueManager
from src.monitoring.trigger_engine import TriggerEngine
from src.services.simulation_service import SimulationService
from src.services.storage_service import StorageService

logger = get_logger(__name__)


class MonitoringService:
    """Enterprise orchestration service executing Phase 2 Portfolio Drift Monitoring & Trigger Intelligence."""

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

        # Load Phase 2 yaml configs
        config_path = Path("config")
        monitoring_cfg = _load_yaml_file(config_path / "monitoring.yaml") if (config_path / "monitoring.yaml").exists() else {}
        trigger_rules_cfg = _load_yaml_file(config_path / "trigger_rules.yaml") if (config_path / "trigger_rules.yaml").exists() else {}
        priority_cfg = _load_yaml_file(config_path / "priority_weights.yaml") if (config_path / "priority_weights.yaml").exists() else {}

        # Instantiate monitoring components
        batch_size = monitoring_cfg.get("monitoring", {}).get("batch_size", 5000)
        self.drift_monitor = DriftMonitor(risk_categories=self.risk_categories, batch_size=batch_size)
        self.trigger_engine = TriggerEngine(rules_config=trigger_rules_cfg)
        self.priority_engine = PriorityEngine(weights_config=priority_cfg)
        self.queue_manager = RebalancingQueueManager()
        self.alert_engine = AlertEngine(monitoring_config=monitoring_cfg)

        self.drift_stats_analyzer = DriftStatistics()
        self.sector_analyzer = SectorExposureAnalyzer()
        self.asset_analyzer = AssetExposureAnalyzer()

    def run_monitoring_cycle(
        self,
        portfolios: List[Portfolio],
        clients: Optional[List[ClientProfile]] = None,
        market_summary: Optional[Dict] = None,
        save_exports: bool = True,
    ) -> Tuple[List[PortfolioDriftMetrics], List[RebalancingRequest], List[AlertObject], Dict]:
        """Execute complete Phase 2 monitoring cycle across all portfolios.

        Args:
            portfolios: List of Portfolio objects.
            clients: Optional list of ClientProfile objects.
            market_summary: Optional market metrics dictionary.
            save_exports: True to export parquet, csv, and json summaries.

        Returns:
            Tuple of (drift_metrics_list, rebalancing_queue, alerts_list, analytics_summary_dict).
        """
        with Timer(f"Phase 2 Monitoring Cycle ({len(portfolios)} portfolios)") as timer_metrics:
            logger.info("Executing Phase 2 Portfolio Drift Monitoring & Trigger Intelligence Cycle...")

            client_map: Dict[str, ClientProfile] = {c.client_id: c for c in (clients or [])}

            # Step 1: Scan & Compute Portfolio Drift
            metrics_list = self.drift_monitor.monitor_batch(portfolios)

            # Step 2: Evaluate Triggers, Priority, Queue & Alerts per Portfolio
            all_alerts: List[AlertObject] = []
            for p, m in zip(portfolios, metrics_list):
                cli = client_map.get(p.client_id)
                triggers = self.trigger_engine.evaluate_triggers(
                    portfolio=p,
                    metrics=m,
                    client=cli,
                    market_summary=market_summary,
                )

                # Generate Alerts
                alerts = self.alert_engine.evaluate_alerts(
                    portfolio=p,
                    metrics=m,
                    triggers=triggers,
                )
                all_alerts.extend(alerts)

                # Evaluate Rebalancing Candidate
                if m.is_rebalance_candidate or triggers:
                    p_score, p_level = self.priority_engine.calculate_priority(
                        portfolio=p,
                        metrics=m,
                        client=cli,
                        triggers=triggers,
                    )
                    req = self.queue_manager.create_request(
                        portfolio=p,
                        metrics=m,
                        priority=p_level,
                        priority_score=p_score,
                        triggers=triggers,
                    )
                    self.queue_manager.enqueue_request(req)

            # Step 3: Sort Queue & Validate
            queue = self.queue_manager.sort_by_priority()
            self.validate_monitoring_outputs(portfolios, metrics_list, queue)

            # Step 4: Generate Analytics Summaries
            stats_summary = self.drift_stats_analyzer.compute_summary_statistics(metrics_list)
            df_sector = self.sector_analyzer.compute_sector_exposure(portfolios)
            df_asset = self.asset_analyzer.compute_asset_exposure(portfolios)
            df_top100 = self.drift_stats_analyzer.get_top_drifted_portfolios(metrics_list, top_n=100)

            critical_alerts_count = sum(1 for a in all_alerts if a.severity.value == "Critical")

            analytics_summary = {
                "cycle_metrics": {
                    "portfolios_processed": len(portfolios),
                    "portfolios_flagged": len(queue),
                    "flagged_percentage": round(len(queue) / len(portfolios) * 100.0, 2) if portfolios else 0.0,
                    "average_drift": stats_summary.get("average_portfolio_drift_score", 0.0),
                    "critical_alerts": critical_alerts_count,
                    "total_alerts": len(all_alerts),
                    "queue_size": len(queue),
                    "execution_time_seconds": timer_metrics.get("elapsed_seconds", 0.0),
                },
                "drift_statistics": stats_summary,
                "top_100_drifted_portfolios": df_top100.to_dict(orient="records"),
                "sector_exposure": df_sector.to_dict(orient="records"),
                "asset_exposure": df_asset.to_dict(orient="records"),
            }

            # Step 5: Save Exports if requested
            if save_exports:
                self.export_results(metrics_list, queue, all_alerts, analytics_summary)

            # Log cycle summary statistics
            logger.info("---------------------------------------------------------------")
            logger.info(f"Portfolios Processed : {len(portfolios)}")
            logger.info(f"Portfolios Flagged   : {len(queue)}")
            logger.info(f"Average Drift        : {stats_summary.get('average_portfolio_drift_score', 0.0):.4f}")
            logger.info(f"Critical Alerts      : {critical_alerts_count}")
            logger.info(f"Rebalancing Queue    : {len(queue)} items")
            logger.info("---------------------------------------------------------------")

            return metrics_list, queue, all_alerts, analytics_summary

    def validate_monitoring_outputs(
        self,
        portfolios: List[Portfolio],
        metrics_list: List[PortfolioDriftMetrics],
        queue: List[RebalancingRequest],
    ) -> bool:
        """Validate monitoring outputs integrity constraints.

        Raises:
            ValidationError: If any validation rule fails.
        """
        logger.debug("Validating Phase 2 monitoring dataset integrity...")

        # Rule 1: Every portfolio must have a drift metric
        if len(portfolios) != len(metrics_list):
            raise ValidationError(f"Mismatch: {len(portfolios)} portfolios but {len(metrics_list)} drift metrics.")

        # Rule 2: Allocation sums remain 100%
        for p in portfolios:
            w_sum = sum(p.current_weights.values())
            if not (0.99 <= w_sum <= 1.01):
                raise ValidationError(f"Portfolio {p.portfolio_id} current allocation weight sum is {w_sum:.4f}, expected ~1.0")

        # Rule 3: Queue validation (no duplicates, valid priorities)
        self.queue_manager.validate_queue()

        logger.debug("Phase 2 dataset validation check PASSED successfully.")
        return True

    def export_results(
        self,
        metrics_list: List[PortfolioDriftMetrics],
        queue: List[RebalancingRequest],
        alerts: List[AlertObject],
        analytics_summary: Dict,
    ) -> None:
        """Save Phase 2 outputs to Parquet, CSV, and JSON.

        Args:
            metrics_list: List of PortfolioDriftMetrics objects.
            queue: List of RebalancingRequest objects.
            alerts: List of AlertObject objects.
            analytics_summary: Analytics dict.
        """
        with Timer("Exporting Phase 2 Monitoring Datasets"):
            # 1. Export Drift Report
            df_drift = DriftMetricsAggregator.to_dataframe(metrics_list)
            df_drift.to_parquet(self.output_dir / "drift_report.parquet", index=False)
            if self.config.storage.save_csv:
                df_drift.to_csv(self.output_dir / "drift_report.csv", index=False)

            # 2. Export Rebalancing Queue
            df_queue = self.queue_manager.to_dataframe()
            df_queue.to_parquet(self.output_dir / "rebalancing_queue.parquet", index=False)
            if self.config.storage.save_csv:
                df_queue.to_csv(self.output_dir / "rebalancing_queue.csv", index=False)

            # 3. Export Alerts
            df_alerts = AlertEngine.to_dataframe(alerts)
            df_alerts.to_parquet(self.output_dir / "alerts.parquet", index=False)
            if self.config.storage.save_csv:
                df_alerts.to_csv(self.output_dir / "alerts.csv", index=False)

            # 4. Export Analytics Summary JSON
            with open(self.output_dir / "analytics_summary.json", "w", encoding="utf-8") as f:
                json.dump(analytics_summary, f, indent=2)

            logger.info(f"Successfully exported Phase 2 datasets to {self.output_dir}")
