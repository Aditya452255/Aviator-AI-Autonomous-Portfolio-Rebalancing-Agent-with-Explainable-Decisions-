"""Enterprise Governance Service orchestrating Phase 6 HITL approvals, overrides, kill switch, and audit exports."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

from src.analytics.audit_statistics import AuditStatistics
from src.analytics.governance_metrics import GovernanceMetrics
from src.analytics.override_statistics import OverrideStatistics
from src.core.config import AppConfig, load_config, _load_yaml_file
from src.core.logger import get_logger
from src.core.utils import Timer
from src.explainability.surrogate_model import SurrogateModel
from src.governance.approval_engine import ApprovalEngine
from src.governance.audit_trail import AuditTrail
from src.governance.compliance_validator import GovernanceComplianceValidator
from src.governance.decision_lifecycle import DecisionLifecycleManager
from src.governance.escalation_manager import EscalationManager
from src.governance.governance_policy import GovernancePolicyEngine
from src.governance.kill_switch import KillSwitch
from src.governance.override_analytics import OverrideAnalyticsEngine
from src.governance.override_manager import OverrideManager
from src.memory.decision_memory import FinalDecisionPackage
from src.models.approval import ApprovalDecision, ApprovalRequest
from src.models.audit_record import AuditEventType, AuditRecord
from src.models.decision_state import DecisionLifecycleState
from src.models.explainability_result import ExplainabilityResult
from src.models.governance_event import GovernanceEvent
from src.models.override import OverrideAction, OverrideRecord
from src.models.portfolio import Portfolio

logger = get_logger(__name__)


class GovernanceService:
    """Enterprise service executing Phase 6 Human-in-the-Loop, Governance & Compliance Layer."""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or load_config()
        self.output_dir = Path(self.config.storage.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        config_path = Path("config")
        gov_cfg = _load_yaml_file(config_path / "governance.yaml") if (config_path / "governance.yaml").exists() else {}
        app_cfg = _load_yaml_file(config_path / "approval_rules.yaml") if (config_path / "approval_rules.yaml").exists() else {}
        ovr_cfg = _load_yaml_file(config_path / "override_rules.yaml") if (config_path / "override_rules.yaml").exists() else {}
        ks_cfg = _load_yaml_file(config_path / "kill_switch.yaml") if (config_path / "kill_switch.yaml").exists() else {}

        combined_cfg = {**gov_cfg, **app_cfg, **ovr_cfg, **ks_cfg}

        self.approval_engine = ApprovalEngine(config=combined_cfg)
        self.override_manager = OverrideManager(config=combined_cfg)
        self.escalation_manager = EscalationManager(config=combined_cfg)
        self.kill_switch = KillSwitch(config=combined_cfg)
        self.audit_trail = AuditTrail()
        self.policy_engine = GovernancePolicyEngine(config=combined_cfg)
        self.lifecycle_manager = DecisionLifecycleManager()
        self.compliance_validator = GovernanceComplianceValidator()
        self.override_analytics = OverrideAnalyticsEngine()

        self.audit_stats = AuditStatistics()
        self.override_stats = OverrideStatistics()
        self.gov_metrics = GovernanceMetrics()

    def run_governance_cycle(
        self,
        portfolios: List[Portfolio],
        decision_packages: List[FinalDecisionPackage],
        explainability_results: Optional[List[ExplainabilityResult]] = None,
        save_exports: bool = True,
    ) -> Tuple[List[ApprovalRequest], Dict]:
        """Execute Phase 6 Governance & Compliance cycle.

        Args:
            portfolios: List of Portfolio objects.
            decision_packages: List of Phase 4 FinalDecisionPackage objects.
            explainability_results: Optional list of Phase 5 ExplainabilityResult objects.
            save_exports: True to persist parquet, csv, and json outputs.

        Returns:
            Tuple of (approval_requests_list, summary_analytics_dict).
        """
        with Timer(f"Phase 6 Governance Cycle ({len(decision_packages)} portfolios)") as timer_metrics:
            logger.info("Executing Phase 6 Human-in-the-Loop, Governance & Compliance Layer Cycle...")

            port_map: Dict[str, Portfolio] = {p.portfolio_id: p for p in portfolios}
            approval_requests: List[ApprovalRequest] = []
            approval_decisions: List[ApprovalDecision] = []
            governance_events: List[GovernanceEvent] = []

            # 1. Evaluate Kill Switch Automatic Rules
            self.kill_switch.evaluate_auto_triggers(
                market_volatility=0.15,
                failure_rate_pct=0.0,
                compliance_breach_pct=0.0,
            )

            for dec_pkg in decision_packages:
                p = port_map.get(dec_pkg.portfolio_id)
                if not p:
                    logger.warning(f"Portfolio {dec_pkg.portfolio_id} not found for governance cycle. Skipping.")
                    continue

                # Lifecycle: CREATED -> UNDER_REVIEW
                self.lifecycle_manager.transition_state(p.portfolio_id, dec_pkg.decision_id, DecisionLifecycleState.CREATED, "Decision package created")
                self.audit_trail.record_event(p.portfolio_id, dec_pkg.decision_id, AuditEventType.CREATED, "Decision Package Ingested")

                self.lifecycle_manager.transition_state(p.portfolio_id, dec_pkg.decision_id, DecisionLifecycleState.UNDER_REVIEW, "Under governance review")
                self.audit_trail.record_event(p.portfolio_id, dec_pkg.decision_id, AuditEventType.AGENT_EXECUTION, f"Agent Consensus: {dec_pkg.consensus_score:.2f}")

                # 2. Check Governance Policy & Compliance
                is_comp, comp_viols = self.compliance_validator.validate_governance_compliance(p, dec_pkg)
                if not is_comp:
                    self.audit_trail.record_event(p.portfolio_id, dec_pkg.decision_id, AuditEventType.FINAL_OUTCOME, f"Compliance Violation: {comp_viols}")
                    logger.warning(f"Governance Compliance Violation for portfolio {p.portfolio_id}: {comp_viols}")

                # 3. Create Approval Request
                req = self.approval_engine.create_approval_request(p, dec_pkg)
                approval_requests.append(req)
                self.audit_trail.record_event(p.portfolio_id, dec_pkg.decision_id, AuditEventType.APPROVAL, f"Approval Request Created: {req.approval_level.value}")

                # 4. Check Escalation Engine
                esc_event = self.escalation_manager.evaluate_and_escalate(dec_pkg, kill_switch_active=self.kill_switch.is_active)
                if esc_event:
                    governance_events.append(esc_event)
                    self.lifecycle_manager.transition_state(p.portfolio_id, dec_pkg.decision_id, DecisionLifecycleState.ESCALATED, esc_event.description)
                    self.audit_trail.record_event(p.portfolio_id, dec_pkg.decision_id, AuditEventType.FINAL_OUTCOME, f"Escalated: {esc_event.description}")
                elif req.is_approved:
                    self.lifecycle_manager.transition_state(p.portfolio_id, dec_pkg.decision_id, DecisionLifecycleState.APPROVED, "Auto-approved per policy")
                    self.audit_trail.record_event(p.portfolio_id, dec_pkg.decision_id, AuditEventType.FINAL_OUTCOME, "Auto-Approved per policy")
                else:
                    self.lifecycle_manager.transition_state(p.portfolio_id, dec_pkg.decision_id, DecisionLifecycleState.AWAITING_APPROVAL, "Awaiting advisor signoff")

                # Mock recording clean approval decision for audit log completeness
                app_dec = self.approval_engine.record_decision(
                    request_id=req.request_id,
                    approver_id="SYS_AUTO" if req.is_approved else "ADV_PENDING",
                    status="APPROVED" if req.is_approved else "PENDING",
                    comments=req.reason,
                )
                approval_decisions.append(app_dec)

            # Record Kill Switch events in governance events
            governance_events.extend(self.kill_switch.events)

            # Compute Analytics
            override_records = list(self.override_manager.override_history.values())
            kpi_metrics = self.override_analytics.compute_override_kpis(
                approval_decisions=approval_decisions,
                override_records=override_records,
                total_decisions=len(decision_packages),
                kill_switch_events=len(self.kill_switch.events),
            )

            df_audit = self.audit_stats.compute_audit_summary_df(self.audit_trail.records)
            df_override = self.override_stats.compute_override_summary_df(override_records)

            summary_analytics = {
                "cycle_metrics": {
                    "total_portfolios_governed": len(decision_packages),
                    "approval_requests_created": len(approval_requests),
                    "escalations_count": len(governance_events),
                    "kill_switch_active": self.kill_switch.is_active,
                    "execution_time_seconds": timer_metrics.get("elapsed_seconds", 0.0),
                },
                "kpis": kpi_metrics,
            }

            if save_exports:
                self.export_results(approval_requests, override_records, governance_events, df_audit, df_override, summary_analytics)

            logger.info("Phase 6 Human-in-the-Loop, Governance & Compliance Layer successfully completed.")
            return approval_requests, summary_analytics

    def record_manual_override(
        self,
        decision_package: FinalDecisionPackage,
        advisor_id: str,
        action: OverrideAction,
        reason_category: str,
        comments: str,
        modifications: Optional[Dict] = None,
    ) -> OverrideRecord:
        """Process and record an advisor manual override action.

        Args:
            decision_package: Target Phase 4 FinalDecisionPackage.
            advisor_id: Advisor ID string.
            action: OverrideAction (APPROVE, REJECT, MODIFY, DEFER, CANCEL).
            reason_category: Category string.
            comments: Explanatory notes.
            modifications: Optional trade modifications.

        Returns:
            OverrideRecord object.
        """
        rec = self.override_manager.execute_override(
            decision_package=decision_package,
            advisor_id=advisor_id,
            action=action,
            reason_category=reason_category,
            comments=comments,
            modifications=modifications,
        )

        # Transition lifecycle state
        if action in (OverrideAction.APPROVE, OverrideAction.MODIFY):
            new_state = DecisionLifecycleState.APPROVED
        elif action in (OverrideAction.REJECT, OverrideAction.CANCEL):
            new_state = DecisionLifecycleState.REJECTED
        else:
            new_state = DecisionLifecycleState.UNDER_REVIEW

        self.lifecycle_manager.transition_state(decision_package.portfolio_id, decision_package.decision_id, new_state, f"Advisor Override by {advisor_id}: {action.value}")
        self.audit_trail.record_event(
            portfolio_id=decision_package.portfolio_id,
            decision_id=decision_package.decision_id,
            event_type=AuditEventType.OVERRIDE,
            event_summary=f"Advisor Override: {action.value} by {advisor_id}",
            details={"reason_category": reason_category, "comments": comments},
            actor=advisor_id,
        )

        return rec

    def export_results(
        self,
        requests: List[ApprovalRequest],
        overrides: List[OverrideRecord],
        events: List[GovernanceEvent],
        df_audit: pd.DataFrame,
        df_override: pd.DataFrame,
        summary_analytics: Dict,
    ) -> None:
        """Export Phase 6 governance datasets to Parquet, CSV, and JSON.

        Args:
            requests: List of ApprovalRequest objects.
            overrides: List of OverrideRecord objects.
            events: List of GovernanceEvent objects.
            df_audit: Audit trail DataFrame.
            df_override: Override history DataFrame.
            summary_analytics: Summary metrics dict.
        """
        with Timer("Exporting Phase 6 Governance Datasets"):
            req_rows = []
            for r in requests:
                req_rows.append({
                    "request_id": r.request_id,
                    "portfolio_id": r.portfolio_id,
                    "decision_id": r.decision_id,
                    "approval_level": r.approval_level.value if hasattr(r.approval_level, "value") else str(r.approval_level),
                    "reason": r.reason,
                    "is_approved": r.is_approved,
                    "approved_by": r.approved_by or "NONE",
                    "timestamp": r.timestamp,
                })

            evt_rows = []
            for e in events:
                evt_rows.append({
                    "event_id": e.event_id,
                    "event_type": e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type),
                    "severity": e.severity,
                    "description": e.description,
                    "timestamp": e.timestamp,
                })

            df_req = pd.DataFrame(req_rows)
            df_evt = pd.DataFrame(evt_rows)

            df_req.to_parquet(self.output_dir / "approval_history.parquet", index=False)
            df_override.to_parquet(self.output_dir / "override_history.parquet", index=False)
            df_audit.to_parquet(self.output_dir / "audit_trail.parquet", index=False)
            df_evt.to_parquet(self.output_dir / "governance_events.parquet", index=False)

            if self.config.storage.save_csv:
                df_req.to_csv(self.output_dir / "approval_history.csv", index=False)
                df_override.to_csv(self.output_dir / "override_history.csv", index=False)
                df_audit.to_csv(self.output_dir / "audit_trail.csv", index=False)
                df_evt.to_csv(self.output_dir / "governance_events.csv", index=False)

            df_kpis = pd.DataFrame([summary_analytics.get("kpis", {})])
            df_kpis.to_csv(self.output_dir / "override_metrics.csv", index=False)

            with open(self.output_dir / "governance_summary.json", "w", encoding="utf-8") as f:
                json.dump(summary_analytics, f, indent=2)

            logger.info(f"Saved Phase 6 governance outputs to {self.output_dir}")
