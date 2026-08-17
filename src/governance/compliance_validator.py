"""Governance Compliance Validator evaluating restriction rules and policy permissions."""

from typing import Dict, List, Optional, Tuple
from src.core.logger import get_logger
from src.memory.decision_memory import FinalDecisionPackage
from src.models.client import ClientProfile
from src.models.portfolio import Portfolio

logger = get_logger(__name__)

Tuple_Validation = Tuple[bool, List[str]]


class GovernanceComplianceValidator:
    """Enterprise Governance Compliance Validator ensuring regulatory boundary adherence."""

    def validate_governance_compliance(
        self,
        portfolio: Portfolio,
        decision_package: FinalDecisionPackage,
        client: Optional[ClientProfile] = None,
    ) -> Tuple_Validation:
        """Validate comprehensive governance rules across compliance summaries and client mandates.

        Args:
            portfolio: Portfolio instance.
            decision_package: Phase 4 FinalDecisionPackage.
            client: Optional ClientProfile.

        Returns:
            Tuple of (is_valid_bool, list_of_violations).
        """
        violations: List[str] = []

        comp_sum = decision_package.compliance_summary
        status = comp_sum.get("compliance_status", "APPROVED")

        if status == "REJECTED":
            violations.append("Phase 4 Compliance Officer rejected the rebalancing proposal.")

        if client and client.restricted_securities:
            rest_viols = comp_sum.get("restricted_violations", [])
            if rest_viols:
                violations.append(f"Restricted securities breached: {rest_viols}")

        is_valid = len(violations) == 0
        return is_valid, violations
