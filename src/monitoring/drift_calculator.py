"""Drift Calculator engine computing multi-level portfolio drift metrics."""

from typing import Dict, List
import numpy as np

from src.core.constants import AssetCategory, RiskCategoryKey
from src.core.logger import get_logger
from src.models.drift import AssetClassDrift, PortfolioDriftMetrics, SectorDrift, SecurityDrift
from src.models.portfolio import Portfolio
from src.models.risk_category import RiskCategory

logger = get_logger(__name__)


class DriftCalculator:
    """Enterprise calculator computing absolute, relative, category, sector, security, and cash drifts."""

    def __init__(self, risk_categories: Dict[str, RiskCategory]) -> None:
        self.risk_categories = risk_categories

    def calculate_portfolio_drift(self, portfolio: Portfolio) -> PortfolioDriftMetrics:
        """Calculate complete multi-dimensional drift metrics for a single portfolio.

        Args:
            portfolio: Portfolio domain model instance.

        Returns:
            Validated PortfolioDriftMetrics object.
        """
        risk_key = portfolio.risk_category.value if isinstance(portfolio.risk_category, RiskCategoryKey) else str(portfolio.risk_category)
        risk_prof = self.risk_categories.get(risk_key)
        drift_limit = risk_prof.drift_threshold if risk_prof else 0.05

        # 1. Asset Category Drift Calculations
        target_cats = {
            AssetCategory.EQUITY.value: risk_prof.target_equity if risk_prof else portfolio.target_weights.get(AssetCategory.EQUITY.value, 0.5),
            AssetCategory.FIXED_INCOME.value: risk_prof.target_fixed_income if risk_prof else portfolio.target_weights.get(AssetCategory.FIXED_INCOME.value, 0.3),
            AssetCategory.ALTERNATIVES.value: risk_prof.target_alternatives if risk_prof else portfolio.target_weights.get(AssetCategory.ALTERNATIVES.value, 0.1),
            AssetCategory.CASH.value: risk_prof.target_cash if risk_prof else portfolio.target_weights.get(AssetCategory.CASH.value, 0.1),
        }

        asset_drifts: Dict[str, AssetClassDrift] = {}
        abs_drifts_list: List[float] = []
        max_drift_cat = AssetCategory.EQUITY.value
        max_drift_val = -1.0
        breached_any = False

        for cat_name, tgt_w in target_cats.items():
            curr_w = portfolio.current_weights.get(cat_name, 0.0)
            abs_d = abs(curr_w - tgt_w)
            rel_d = (abs_d / tgt_w) if tgt_w > 0 else 0.0
            is_br = abs_d > drift_limit
            if is_br:
                breached_any = True

            if abs_d > max_drift_val:
                max_drift_val = abs_d
                max_drift_cat = cat_name

            abs_drifts_list.append(abs_d)

            asset_drifts[cat_name] = AssetClassDrift(
                asset_category=cat_name,
                target_weight=round(tgt_w, 4),
                current_weight=round(curr_w, 4),
                absolute_drift=round(abs_d, 4),
                relative_drift=round(rel_d, 4),
                is_breached=is_br,
            )

        # Total absolute drift sum & Portfolio Drift Score (RMS drift)
        total_abs_drift = sum(abs_drifts_list)
        portfolio_drift_score = float(np.sqrt(np.mean(np.square(abs_drifts_list))))

        # Cash Drift: current cash weight minus target cash weight
        curr_cash_w = portfolio.current_weights.get(AssetCategory.CASH.value, 0.0)
        tgt_cash_w = target_cats[AssetCategory.CASH.value]
        cash_drift = curr_cash_w - tgt_cash_w

        # 2. Sector-Level Drift Calculation
        sector_weights: Dict[str, float] = {}
        for h in portfolio.holdings:
            # Aggregate by sector (or asset_class if sector not specified in holding)
            sec_name = getattr(h, "sector", h.asset_category)
            sector_weights[sec_name] = sector_weights.get(sec_name, 0.0) + h.current_weight

        sector_drifts: Dict[str, SectorDrift] = {}
        for s_name, curr_w in sector_weights.items():
            sector_drifts[s_name] = SectorDrift(
                sector=s_name,
                current_weight=round(curr_w, 4),
                target_weight=0.0,
                absolute_drift=round(curr_w, 4),
            )

        # 3. Security-Level Drift Calculation
        security_drifts: List[SecurityDrift] = []
        for h in portfolio.holdings:
            abs_d = abs(h.current_weight - h.target_weight)
            rel_d = (abs_d / h.target_weight) if h.target_weight > 0 else 0.0
            security_drifts.append(
                SecurityDrift(
                    ticker=h.ticker,
                    asset_category=h.asset_category,
                    target_weight=round(h.target_weight, 4),
                    current_weight=round(h.current_weight, 4),
                    absolute_drift=round(abs_d, 4),
                    relative_drift=round(rel_d, 4),
                )
            )

        return PortfolioDriftMetrics(
            portfolio_id=portfolio.portfolio_id,
            client_id=portfolio.client_id,
            risk_category=risk_key,
            total_absolute_drift=round(total_abs_drift, 4),
            portfolio_drift_score=round(portfolio_drift_score, 4),
            cash_drift=round(cash_drift, 4),
            max_drift_asset_class=max_drift_cat,
            max_drift_value=round(max_drift_val, 4),
            asset_drifts=asset_drifts,
            sector_drifts=sector_drifts,
            security_drifts=security_drifts,
            is_rebalance_candidate=breached_any or (portfolio_drift_score >= 0.02),
        )
