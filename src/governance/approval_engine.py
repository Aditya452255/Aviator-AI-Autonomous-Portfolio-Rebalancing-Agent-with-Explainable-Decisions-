"""Approval Engine constructing approval requests and assessing decision review flows."""

from typing import Dict, List, Optional
from src.core.logger import get_logger
from src.governance.approval_rules import ApprovalRulesEvaluator
from src.memory.decision_memory import FinalDecisionPackage
from src.models.approval import ApprovalDecision, ApprovalLevel, ApprovalRequest
from src.models.portfolio import Portfolio

logger = get_logger(__name__)


class ApprovalEngine:
    """Enterprise Approval Engine managing human review workflows."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.evaluator = ApprovalRulesEvaluator(config=self.config)
        self.active_requests: Dict[str, ApprovalRequest] = {}

    def create_approval_request(
        self,
        portfolio: Portfolio,
        decision_package: FinalDecisionPackage,
    ) -> ApprovalRequest:
        """Construct an ApprovalRequest for a portfolio decision.

        Args:
            portfolio: Target portfolio instance.
            decision_package: Phase 4 FinalDecisionPackage.

        Returns:
            ApprovalRequest domain model.
        """
        level, reason = self.evaluator.determine_approval_level(portfolio, decision_package)
        req_id = f"REQ_APP_{portfolio.portfolio_id}"

        req = ApprovalRequest(
            request_id=req_id,
            portfolio_id=portfolio.portfolio_id,
            decision_id=decision_package.decision_id,
            approval_level=level,
            reason=reason,
            is_approved=(level == ApprovalLevel.INFORMATIONAL),
        )

        self.active_requests[req_id] = req
        logger.info(f"Created ApprovalRequest [{req_id}] | Level: {level.value} | Reason: {reason}")
        return req

    def record_decision(
        self,
        request_id: str,
        approver_id: str,
        status: str = "APPROVED",
        comments: str = "",
    ) -> ApprovalDecision:
        """Record an advisor or manager approval decision.

        Args:
            request_id: Request ID.
            approver_id: Approver ID string.
            status: APPROVED, REJECTED, or ESCALATED.
            comments: Approver notes.

        Returns:
            ApprovalDecision domain model.
        """
        req = self.active_requests.get(request_id)
        level = req.approval_level if req else ApprovalLevel.INFORMATIONAL
        port_id = req.portfolio_id if req else "UNKNOWN"

        if req and status == "APPROVED":
            req.is_approved = True
            req.approved_by = approver_id

        decision = ApprovalDecision(
            request_id=request_id,
            portfolio_id=port_id,
            level=level,
            status=status,
            approver_id=approver_id,
            comments=comments,
        )

        logger.info(f"Recorded ApprovalDecision [{request_id}] by {approver_id} -> {status}")
        return decision
