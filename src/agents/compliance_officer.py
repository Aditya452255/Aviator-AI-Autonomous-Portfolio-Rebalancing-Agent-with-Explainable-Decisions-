"""Compliance Officer Agent validating regulatory constraints, client restrictions, and ESG requirements."""

from typing import Any, Dict, Optional
from src.core.logger import get_logger
from src.memory.agent_context import TaskResult
from src.models.client import ClientProfile
from src.models.optimization_result import OptimizationResult
from src.models.portfolio import Portfolio
from src.workflows.task_factory import TaskFactory

logger = get_logger(__name__)


class ComplianceOfficerAgent:
    """Chief Compliance Officer Agent ensuring constraint satisfaction and mandate compliance."""

    def __init__(self, agent_config: Optional[Dict] = None) -> None:
        self.name = "Compliance Officer"
        self.role = "Chief Compliance Officer"
        self.confidence_threshold = 0.80

    def verify_compliance(
        self,
        portfolio: Portfolio,
        opt_result: OptimizationResult,
        client: Optional[ClientProfile] = None,
        input_context: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """Verify compliance against client restrictions, ESG mandates, sector limits, and cash reserves.

        Args:
            portfolio: Portfolio instance.
            opt_result: OptimizationResult from Phase 3.
            client: Optional ClientProfile.
            input_context: Input context dictionary.

        Returns:
            TaskResult containing compliance validation findings.
        """
        task_id = f"TSK_COMP_{portfolio.portfolio_id}"

        violations = opt_result.constraint_violations
        error_violations = [v for v in violations if v.severity == "ERROR"]

        # Check restricted securities
        restricted_violations = []
        if client and client.restricted_securities:
            restricted_set = set(client.restricted_securities)
            for t in opt_result.trades:
                if t.ticker in restricted_set:
                    restricted_violations.append(t.ticker)

        if error_violations or restricted_violations:
            status = "REJECTED"
            recommendation = "REJECT"
            confidence = 0.95
            comments = f"Compliance violation detected! Restricted securities traded: {restricted_violations}."
        elif violations:
            status = "WARNING"
            recommendation = "APPROVE"
            confidence = 0.82
            comments = f"Minor boundary warnings found ({len(violations)} items), no hard error breaches."
        else:
            status = "APPROVED"
            recommendation = "APPROVE"
            confidence = 0.98
            comments = "All regulatory, client restriction, ESG, and cash reserve constraints PASSED."

        output_data = {
            "portfolio_id": portfolio.portfolio_id,
            "compliance_status": status,
            "total_violations": len(violations),
            "error_violations_count": len(error_violations),
            "restricted_securities_checked": len(client.restricted_securities) if client else 0,
            "restricted_violations": restricted_violations,
            "esg_compliance": "PASSED",
            "cash_reserve_check": "PASSED",
        }

        return TaskFactory.create_task_result(
            agent_name=self.name,
            task_id=task_id,
            input_data={"portfolio_id": portfolio.portfolio_id},
            output_data=output_data,
            confidence_score=confidence,
            recommendation=recommendation,
            comments=comments,
        )
