"""Governance Policy engine enforcing YAML governance boundary conditions."""

from typing import Dict, List, Optional, Tuple
from src.core.logger import get_logger
from src.models.portfolio import Portfolio

logger = get_logger(__name__)

Tuple_Policy = Tuple[bool, List[str]]


class GovernancePolicyEngine:
    """Enterprise Governance Policy Engine enforcing regulatory boundaries."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        cfg = config or {}
        gov = cfg.get("governance", {})
        self.require_signoff = gov.get("require_advisor_signoff", True)
        self.max_drift = gov.get("max_allowed_drift_without_approval", 0.08)

    def check_policy_compliance(self, portfolio: Portfolio, drift_score: float) -> Tuple_Policy:
        """Check portfolio decision against governance policy parameters.

        Args:
            portfolio: Portfolio instance.
            drift_score: Drift score.

        Returns:
            Tuple of (is_compliant_bool, list_of_policy_violations).
        """
        violations: List[str] = []

        if drift_score > self.max_drift:
            violations.append(f"Portfolio drift ({drift_score:.2%}) exceeds maximum unapproved limit ({self.max_drift:.2%}).")

        is_compliant = len(violations) == 0
        return is_compliant, violations
