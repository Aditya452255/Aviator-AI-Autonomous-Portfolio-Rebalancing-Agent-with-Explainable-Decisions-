"""Trigger Engine evaluating threshold, calendar, market event, and client event rules."""

from typing import Dict, List, Optional
import pandas as pd

from src.core.logger import get_logger
from src.models.client import ClientProfile
from src.models.drift import PortfolioDriftMetrics
from src.models.portfolio import Portfolio
from src.models.trigger import TriggerEvaluation, TriggerReason, TriggerType

logger = get_logger(__name__)


class TriggerEngine:
    """Enterprise trigger engine evaluating rules across 4 trigger categories."""

    def __init__(self, rules_config: Optional[Dict] = None) -> None:
        self.config = rules_config or {}

        # Default rule thresholds
        t_cfg = self.config.get("threshold_triggers", {})
        self.eq_limit = t_cfg.get("equity_drift_limit", 0.05)
        self.fi_limit = t_cfg.get("fixed_income_drift_limit", 0.03)
        self.alt_limit = t_cfg.get("alternatives_drift_limit", 0.04)
        self.cash_limit = t_cfg.get("cash_drift_limit", 0.02)
        self.sec_max_limit = t_cfg.get("single_security_max_weight", 0.15)

        m_cfg = self.config.get("market_event_triggers", {})
        self.market_gap_limit = m_cfg.get("market_gap_threshold", 0.035)
        self.vol_spike_limit = m_cfg.get("volatility_spike_threshold", 0.25)
        self.sector_crash_limit = m_cfg.get("sector_crash_threshold", 0.05)

        c_cfg = self.config.get("client_event_triggers", {})
        self.large_cf_pct = c_cfg.get("large_cash_flow_pct", 0.05)
        self.retire_horizon = c_cfg.get("retirement_horizon_years", 3)

    def evaluate_triggers(
        self,
        portfolio: Portfolio,
        metrics: PortfolioDriftMetrics,
        client: Optional[ClientProfile] = None,
        market_summary: Optional[Dict] = None,
        days_since_rebalance: int = 45,
    ) -> List[TriggerEvaluation]:
        """Evaluate all trigger categories for a portfolio.

        Args:
            portfolio: Portfolio instance.
            metrics: Calculated PortfolioDriftMetrics.
            client: Optional ClientProfile instance.
            market_summary: Optional dictionary with current market metrics.
            days_since_rebalance: Integer count of days since last rebalance.

        Returns:
            List of TriggerEvaluation instances that fired (is_triggered=True).
        """
        triggers: List[TriggerEvaluation] = []

        # -------------------------------------------------------------
        # 1. THRESHOLD TRIGGERS
        # -------------------------------------------------------------
        eq_drift = metrics.asset_drifts.get("Equity")
        if eq_drift and eq_drift.absolute_drift > self.eq_limit:
            triggers.append(
                TriggerEvaluation(
                    trigger_type=TriggerType.THRESHOLD,
                    trigger_reason=TriggerReason.EQUITY_DRIFT_BREACH,
                    is_triggered=True,
                    severity_score=min(1.0, eq_drift.absolute_drift / 0.15),
                    message=f"Equity allocation drift ({eq_drift.absolute_drift:.2%}) breached limit ({self.eq_limit:.2%})",
                    metadata={"drift": eq_drift.absolute_drift, "threshold": self.eq_limit},
                )
            )

        fi_drift = metrics.asset_drifts.get("Fixed Income")
        if fi_drift and fi_drift.absolute_drift > self.fi_limit:
            triggers.append(
                TriggerEvaluation(
                    trigger_type=TriggerType.THRESHOLD,
                    trigger_reason=TriggerReason.FIXED_INCOME_DRIFT_BREACH,
                    is_triggered=True,
                    severity_score=min(1.0, fi_drift.absolute_drift / 0.10),
                    message=f"Fixed Income drift ({fi_drift.absolute_drift:.2%}) breached limit ({self.fi_limit:.2%})",
                    metadata={"drift": fi_drift.absolute_drift, "threshold": self.fi_limit},
                )
            )

        if abs(metrics.cash_drift) > self.cash_limit:
            triggers.append(
                TriggerEvaluation(
                    trigger_type=TriggerType.THRESHOLD,
                    trigger_reason=TriggerReason.CASH_DRIFT_BREACH,
                    is_triggered=True,
                    severity_score=min(1.0, abs(metrics.cash_drift) / 0.08),
                    message=f"Cash allocation drift ({metrics.cash_drift:+.2%}) breached limit ({self.cash_limit:.2%})",
                    metadata={"cash_drift": metrics.cash_drift, "threshold": self.cash_limit},
                )
            )

        # -------------------------------------------------------------
        # 2. CALENDAR TRIGGERS
        # -------------------------------------------------------------
        if days_since_rebalance >= 90:
            triggers.append(
                TriggerEvaluation(
                    trigger_type=TriggerType.CALENDAR,
                    trigger_reason=TriggerReason.SCHEDULED_REBALANCE,
                    is_triggered=True,
                    severity_score=min(1.0, days_since_rebalance / 180.0),
                    message=f"Scheduled quarterly rebalance due ({days_since_rebalance} days since last rebalance)",
                    metadata={"days_since_rebalance": days_since_rebalance},
                )
            )

        # -------------------------------------------------------------
        # 3. MARKET EVENT TRIGGERS
        # -------------------------------------------------------------
        if market_summary:
            max_gap = market_summary.get("max_price_gap", 0.0)
            if max_gap >= self.market_gap_limit:
                triggers.append(
                    TriggerEvaluation(
                        trigger_type=TriggerType.MARKET_EVENT,
                        trigger_reason=TriggerReason.MARKET_GAP,
                        is_triggered=True,
                        severity_score=min(1.0, max_gap / 0.10),
                        message=f"Market price gap event detected ({max_gap:.2%} return movement)",
                        metadata={"market_gap": max_gap},
                    )
                )

            vol_level = market_summary.get("market_volatility", 0.0)
            if vol_level >= self.vol_spike_limit:
                triggers.append(
                    TriggerEvaluation(
                        trigger_type=TriggerType.MARKET_EVENT,
                        trigger_reason=TriggerReason.MARKET_VOLATILITY_SPIKE,
                        is_triggered=True,
                        severity_score=min(1.0, vol_level / 0.40),
                        message=f"Market volatility spike detected ({vol_level:.1%} annualized vol)",
                        metadata={"market_volatility": vol_level},
                    )
                )

            sector_drop = market_summary.get("sector_crash_drop", 0.0)
            if sector_drop >= self.sector_crash_limit:
                triggers.append(
                    TriggerEvaluation(
                        trigger_type=TriggerType.MARKET_EVENT,
                        trigger_reason=TriggerReason.SECTOR_CRASH,
                        is_triggered=True,
                        severity_score=min(1.0, sector_drop / 0.15),
                        message=f"Sector crash event detected ({sector_drop:.2%} drop)",
                        metadata={"sector_drop": sector_drop},
                    )
                )

        # -------------------------------------------------------------
        # 4. CLIENT EVENT TRIGGERS
        # -------------------------------------------------------------
        if client:
            if abs(client.upcoming_cash_flow) >= (client.portfolio_size * self.large_cf_pct):
                reason = TriggerReason.LARGE_CASH_DEPOSIT if client.upcoming_cash_flow > 0 else TriggerReason.LARGE_CASH_WITHDRAWAL
                triggers.append(
                    TriggerEvaluation(
                        trigger_type=TriggerType.CLIENT_EVENT,
                        trigger_reason=reason,
                        is_triggered=True,
                        severity_score=min(1.0, abs(client.upcoming_cash_flow) / client.portfolio_size),
                        message=f"Large cash flow event ({client.upcoming_cash_flow:+.2f} base currency)",
                        metadata={"cash_flow": client.upcoming_cash_flow},
                    )
                )

            if client.investment_horizon <= self.retire_horizon:
                triggers.append(
                    TriggerEvaluation(
                        trigger_type=TriggerType.CLIENT_EVENT,
                        trigger_reason=TriggerReason.RETIRING_SOON,
                        is_triggered=True,
                        severity_score=0.75,
                        message=f"Client approaching retirement horizon ({client.investment_horizon} years remaining)",
                        metadata={"horizon_years": client.investment_horizon},
                    )
                )

        return triggers
