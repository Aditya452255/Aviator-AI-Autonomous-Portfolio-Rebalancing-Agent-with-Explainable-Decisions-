"""Alert Engine generating structured alerts for critical monitoring conditions."""

from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from src.core.logger import get_logger
from src.models.drift import PortfolioDriftMetrics
from src.models.portfolio import Portfolio
from src.models.rebalancing_request import AlertCategory, AlertObject, AlertSeverity
from src.models.trigger import TriggerEvaluation, TriggerType

logger = get_logger(__name__)


class AlertEngine:
    """Enterprise alert engine generating structured system alerts."""

    def __init__(self, monitoring_config: Optional[Dict] = None) -> None:
        cfg = monitoring_config or {}
        m_cfg = cfg.get("monitoring", {})
        self.cash_alert_thresh = m_cfg.get("cash_drift_threshold", 0.02)
        self.sector_alert_thresh = m_cfg.get("sector_concentration_threshold", 0.35)

    def evaluate_alerts(
        self,
        portfolio: Portfolio,
        metrics: PortfolioDriftMetrics,
        triggers: List[TriggerEvaluation],
        days_since_rebalance: int = 45,
    ) -> List[AlertObject]:
        """Evaluate alert conditions for a portfolio and generate AlertObject list.

        Args:
            portfolio: Portfolio instance.
            metrics: Calculated PortfolioDriftMetrics.
            triggers: List of fired TriggerEvaluation objects.
            days_since_rebalance: Days elapsed since last rebalance.

        Returns:
            List of generated AlertObject instances.
        """
        alerts: List[AlertObject] = []
        now_str = datetime.now().isoformat()

        # 1. Critical Drift Alert
        if metrics.portfolio_drift_score >= 0.08:
            alert_id = f"ALT_DRIFT_{portfolio.portfolio_id}"
            alerts.append(
                AlertObject(
                    alert_id=alert_id,
                    portfolio_id=portfolio.portfolio_id,
                    client_id=portfolio.client_id,
                    category=AlertCategory.CRITICAL_DRIFT,
                    severity=AlertSeverity.CRITICAL,
                    title="Critical Portfolio Drift Violation",
                    description=f"Portfolio drift score ({metrics.portfolio_drift_score:.2%}) severely exceeds acceptable boundaries.",
                    timestamp=now_str,
                    metadata={"drift_score": metrics.portfolio_drift_score, "max_drift_asset": metrics.max_drift_asset_class},
                )
            )

        # 2. Large Cash Allocation Alert
        curr_cash_w = portfolio.current_weights.get("Cash", 0.0)
        if curr_cash_w >= 0.15 or metrics.cash_drift >= 0.05:
            alert_id = f"ALT_CASH_{portfolio.portfolio_id}"
            alerts.append(
                AlertObject(
                    alert_id=alert_id,
                    portfolio_id=portfolio.portfolio_id,
                    client_id=portfolio.client_id,
                    category=AlertCategory.LARGE_CASH_ALLOCATION,
                    severity=AlertSeverity.WARNING,
                    title="High Cash Reserve Alert",
                    description=f"Uninvested cash allocation ({curr_cash_w:.2%}) causes cash drag.",
                    timestamp=now_str,
                    metadata={"cash_weight": curr_cash_w, "cash_balance": portfolio.cash_balance},
                )
            )

        # 3. Sector Concentration Alert
        for sec_name, sec_drift in metrics.sector_drifts.items():
            if sec_drift.current_weight >= self.sector_alert_thresh:
                alert_id = f"ALT_SEC_{portfolio.portfolio_id}_{sec_name.replace(' ', '_')}"
                alerts.append(
                    AlertObject(
                        alert_id=alert_id,
                        portfolio_id=portfolio.portfolio_id,
                        client_id=portfolio.client_id,
                        category=AlertCategory.SECTOR_CONCENTRATION,
                        severity=AlertSeverity.WARNING,
                        title=f"High Sector Concentration: {sec_name}",
                        description=f"Sector '{sec_name}' accounts for {sec_drift.current_weight:.2%} of total portfolio value.",
                        timestamp=now_str,
                        metadata={"sector": sec_name, "sector_weight": sec_drift.current_weight},
                    )
                )

        # 4. Market Event Alert
        mkt_triggers = [t for t in triggers if t.trigger_type == TriggerType.MARKET_EVENT]
        for mt in mkt_triggers:
            alert_id = f"ALT_MKT_{portfolio.portfolio_id}_{mt.trigger_reason.value.replace(' ', '_')}"
            alerts.append(
                AlertObject(
                    alert_id=alert_id,
                    portfolio_id=portfolio.portfolio_id,
                    client_id=portfolio.client_id,
                    category=AlertCategory.MARKET_EVENT,
                    severity=AlertSeverity.WARNING,
                    title=f"Market Event: {mt.trigger_reason.value}",
                    description=mt.message,
                    timestamp=now_str,
                    metadata=mt.metadata,
                )
            )

        # 5. Missed Rebalance Alert
        if days_since_rebalance >= 90:
            alert_id = f"ALT_SCHED_{portfolio.portfolio_id}"
            alerts.append(
                AlertObject(
                    alert_id=alert_id,
                    portfolio_id=portfolio.portfolio_id,
                    client_id=portfolio.client_id,
                    category=AlertCategory.MISSED_REBALANCE,
                    severity=AlertSeverity.INFO,
                    title="Scheduled Calendar Rebalance Overdue",
                    description=f"Portfolio has not been rebalanced in {days_since_rebalance} days.",
                    timestamp=now_str,
                    metadata={"days_since_rebalance": days_since_rebalance},
                )
            )

        return alerts

    @staticmethod
    def to_dataframe(alerts: List[AlertObject]) -> pd.DataFrame:
        """Convert list of AlertObject instances to pandas DataFrame.

        Args:
            alerts: List of AlertObject instances.

        Returns:
            DataFrame containing alerts table.
        """
        rows = [a.model_dump() for a in alerts]
        df = pd.DataFrame(rows)
        if not df.empty and "metadata" in df.columns:
            df["metadata_json"] = df["metadata"].apply(lambda x: str(x))
        return df
