"""Drift Monitor scanner supporting batch, incremental, scheduled, and on-demand execution modes."""

from typing import Dict, List, Optional
from src.core.logger import get_logger
from src.core.utils import Timer
from src.models.drift import PortfolioDriftMetrics
from src.models.portfolio import Portfolio
from src.models.risk_category import RiskCategory
from src.monitoring.drift_calculator import DriftCalculator

logger = get_logger(__name__)


class DriftMonitor:
    """Enterprise scanning engine evaluating portfolio drift across multiple execution modes."""

    def __init__(self, risk_categories: Dict[str, RiskCategory], batch_size: int = 5000) -> None:
        self.risk_categories = risk_categories
        self.batch_size = batch_size
        self.calculator = DriftCalculator(risk_categories=risk_categories)

    def monitor_batch(self, portfolios: List[Portfolio]) -> List[PortfolioDriftMetrics]:
        """Process all portfolios in batch chunks and return calculated metrics for all portfolios.

        Args:
            portfolios: Complete list of portfolios to scan.

        Returns:
            List of PortfolioDriftMetrics for all scanned portfolios.
        """
        with Timer(f"Batch Monitoring ({len(portfolios)} portfolios)"):
            all_metrics: List[PortfolioDriftMetrics] = []
            num_portfolios = len(portfolios)

            for i in range(0, num_portfolios, self.batch_size):
                batch = portfolios[i : i + self.batch_size]
                for p in batch:
                    metrics = self.calculator.calculate_portfolio_drift(p)
                    all_metrics.append(metrics)

            flagged_count = sum(1 for m in all_metrics if m.is_rebalance_candidate)
            logger.info(f"Batch monitoring completed. Scanned {len(all_metrics)} portfolios, flagged {flagged_count} candidates.")
            return all_metrics

    def monitor_incremental(self, updated_portfolios: List[Portfolio]) -> List[PortfolioDriftMetrics]:
        """Perform incremental drift calculation on a delta subset of updated portfolios.

        Args:
            updated_portfolios: Portfolios modified or marked for delta scan.

        Returns:
            List of PortfolioDriftMetrics.
        """
        with Timer(f"Incremental Monitoring ({len(updated_portfolios)} portfolios)"):
            metrics_list = [self.calculator.calculate_portfolio_drift(p) for p in updated_portfolios]
            logger.info(f"Incremental monitoring processed {len(metrics_list)} portfolios.")
            return metrics_list

    def monitor_on_demand(self, portfolio: Portfolio) -> PortfolioDriftMetrics:
        """Scan a single targeted portfolio on demand.

        Args:
            portfolio: Single Portfolio instance.

        Returns:
            PortfolioDriftMetrics instance.
        """
        logger.debug(f"On-demand monitoring scan triggered for portfolio: {portfolio.portfolio_id}")
        return self.calculator.calculate_portfolio_drift(portfolio)

    def filter_flagged_portfolios(self, metrics_list: List[PortfolioDriftMetrics]) -> List[PortfolioDriftMetrics]:
        """Filter metrics list returning only portfolios requiring rebalancing review.

        Args:
            metrics_list: List of calculated drift metrics.

        Returns:
            Filtered list of metrics where is_rebalance_candidate is True.
        """
        return [m for m in metrics_list if m.is_rebalance_candidate]
