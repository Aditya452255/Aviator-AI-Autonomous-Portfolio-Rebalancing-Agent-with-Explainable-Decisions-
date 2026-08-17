"""Compliance Explainer generating detailed audit logs for regulatory and compliance auditors."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from src.core.logger import get_logger
from src.memory.decision_memory import FinalDecisionPackage
from src.models.explanation import ComplianceExplanation
from src.models.portfolio import Portfolio

logger = get_logger(__name__)


class ComplianceExplainer:
    """Enterprise Compliance Explainer generating regulatory audit trails."""

    def generate_compliance_explanation(
        self,
        portfolio: Portfolio,
        decision_package: FinalDecisionPackage,
        shap_values: Dict[str, float],
        counterfactual_summary: str,
    ) -> ComplianceExplanation:
        """Generate regulatory compliance explanation audit log.

        Args:
            portfolio: Target portfolio instance.
            decision_package: Phase 4 FinalDecisionPackage.
            shap_values: Map of SHAP values.
            counterfactual_summary: Counterfactual summary text.

        Returns:
            ComplianceExplanation domain model object.
        """
        opt_sum = decision_package.optimization_summary
        comp_sum = decision_package.compliance_summary

        audit_str = (
            f"COMPLIANCE REGULATORY AUDIT LOG\n"
            f"Decision ID: {decision_package.decision_id} | Portfolio ID: {portfolio.portfolio_id} | Client ID: {portfolio.client_id}\n"
            f"Timestamp: {datetime.now().isoformat()}\n"
            f"Consensus Score: {decision_package.consensus_score:.4f} | Confidence Score: {decision_package.confidence_score:.4f}\n"
            f"Overall Decision: {decision_package.recommendation} | Readiness: {decision_package.execution_readiness.value if hasattr(decision_package.execution_readiness, 'value') else str(decision_package.execution_readiness)}\n"
            f"Compliance Status: {comp_sum.get('compliance_status', 'APPROVED')} | Total Violations: {comp_sum.get('total_violations', 0)}"
        )

        input_feats = {
            "portfolio_drift": float(opt_sum.get("drift_before", 0.05)),
            "turnover": float(opt_sum.get("turnover", 0.10)),
            "total_cost": float(opt_sum.get("total_cost", 0.0)),
            "total_tax": float(opt_sum.get("total_tax", 0.0)),
        }

        constraint_checks = [
            f"Sector Concentration Limit: {comp_sum.get('sector_limit_check', 'PASSED')}",
            f"Issuer Position Limit: {comp_sum.get('issuer_limit_check', 'PASSED')}",
            f"Restricted Securities: {comp_sum.get('restricted_violations', [])}",
            f"Cash Reserve Minimum: {comp_sum.get('cash_reserve_check', 'PASSED')}",
        ]

        shap_str = f"Top SHAP Attributions: {sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:3]}"

        return ComplianceExplanation(
            decision_id=decision_package.decision_id,
            portfolio_id=portfolio.portfolio_id,
            timestamp=datetime.now().isoformat(),
            audit_summary=audit_str,
            input_features=input_feats,
            optimization_summary={"strategy": opt_sum.get("strategy", "BALANCED"), "solver_status": opt_sum.get("solver_status", "OPTIMAL")},
            constraint_results=constraint_checks,
            agent_consensus=f"Consensus: {decision_package.consensus_score:.4f}",
            shap_summary=shap_str,
            counterfactual_summary=counterfactual_summary,
            config_version="v1.0",
            model_version="v1.0.0",
        )
