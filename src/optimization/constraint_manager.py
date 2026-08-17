"""Constraint Manager evaluating and enforcing portfolio limits and generating violation reports."""

from typing import Dict, List, Optional
from src.core.constants import AssetCategory
from src.core.logger import get_logger
from src.models.client import ClientProfile
from src.models.optimization_result import ConstraintViolation
from src.models.portfolio import Portfolio
from src.models.security import Security

logger = get_logger(__name__)


class ConstraintManager:
    """Enterprise constraint manager evaluating portfolio limits and boundary violations."""

    def __init__(
        self,
        max_sector_weight: float = 0.35,
        max_position_weight: float = 0.15,
        min_cash_weight: float = 0.02,
        min_liquidity_score: float = 30.0,
    ) -> None:
        self.max_sector_weight = max_sector_weight
        self.max_position_weight = max_position_weight
        self.min_cash_weight = min_cash_weight
        self.min_liquidity_score = min_liquidity_score

    def validate_constraints(
        self,
        portfolio: Portfolio,
        proposed_weights: Dict[str, float],
        client: Optional[ClientProfile] = None,
        securities_map: Optional[Dict[str, Security]] = None,
    ) -> List[ConstraintViolation]:
        """Validate proposed security and asset weights against portfolio constraints.

        Args:
            portfolio: Portfolio domain model.
            proposed_weights: Map of ticker or category to proposed weight fraction.
            client: Optional ClientProfile instance.
            securities_map: Optional lookup dictionary of ticker to Security.

        Returns:
            List of ConstraintViolation objects.
        """
        violations: List[ConstraintViolation] = []

        # 1. Maximum Single Position Limit Check (max 15%)
        for ticker, w in proposed_weights.items():
            if ticker in (AssetCategory.EQUITY.value, AssetCategory.FIXED_INCOME.value, AssetCategory.ALTERNATIVES.value, AssetCategory.CASH.value):
                continue
            if w > self.max_position_weight:
                violations.append(
                    ConstraintViolation(
                        constraint_name="Maximum Position Limit",
                        description=f"Security {ticker} weight ({w:.2%}) exceeds maximum limit ({self.max_position_weight:.2%})",
                        severity="WARNING",
                        current_value=round(w, 4),
                        allowed_limit=self.max_position_weight,
                    )
                )

        # 2. Cash Reserve Minimum Check
        cash_w = proposed_weights.get(AssetCategory.CASH.value, portfolio.current_weights.get(AssetCategory.CASH.value, 0.0))
        if cash_w < self.min_cash_weight:
            violations.append(
                ConstraintViolation(
                    constraint_name="Minimum Cash Reserve",
                    description=f"Cash allocation ({cash_w:.2%}) is below required minimum ({self.min_cash_weight:.2%})",
                    severity="WARNING",
                    current_value=round(cash_w, 4),
                    allowed_limit=self.min_cash_weight,
                )
            )

        # 3. Client Restricted Securities Check
        if client and client.restricted_securities:
            restricted_set = set(client.restricted_securities)
            for h in portfolio.holdings:
                if h.ticker in restricted_set and proposed_weights.get(h.ticker, h.current_weight) > 0:
                    violations.append(
                        ConstraintViolation(
                            constraint_name="Client Restricted Security Violation",
                            description=f"Portfolio holds restricted ticker '{h.ticker}' for client {client.client_id}",
                            severity="ERROR",
                            current_value=round(proposed_weights.get(h.ticker, h.current_weight), 4),
                            allowed_limit=0.0,
                        )
                    )

        # 4. Liquidity Requirement Check
        if securities_map:
            for h in portfolio.holdings:
                sec = securities_map.get(h.ticker)
                if sec and sec.liquidity_score < self.min_liquidity_score:
                    violations.append(
                        ConstraintViolation(
                            constraint_name="Low Security Liquidity Violation",
                            description=f"Security {h.ticker} liquidity score ({sec.liquidity_score}) is below minimum ({self.min_liquidity_score})",
                            severity="WARNING",
                            current_value=sec.liquidity_score,
                            allowed_limit=self.min_liquidity_score,
                        )
                    )

        return violations
