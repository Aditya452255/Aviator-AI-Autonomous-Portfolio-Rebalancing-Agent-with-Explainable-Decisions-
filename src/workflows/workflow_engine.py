"""Multi-Agent Workflow Engine orchestrating sequential agent tasks and building final decision packages."""

import time
from typing import Dict, List, Optional
from src.core.logger import get_logger
from src.memory.agent_context import AgentContext, TaskResult
from src.memory.decision_memory import DecisionMemory, FinalDecisionPackage
from src.memory.shared_state import SharedWorkflowState, WorkflowStatus
from src.models.client import ClientProfile
from src.models.optimization_result import OptimizationResult
from src.models.portfolio import Portfolio
from src.validators.consensus_validator import ConsensusValidator
from src.validators.conflict_resolver import ConflictResolver
from src.validators.decision_validator import DecisionValidator
from src.workflows.crew_builder import CrewBuilder
from src.workflows.handoff_manager import HandoffManager

logger = get_logger(__name__)


class MultiAgentWorkflowEngine:
    """Enterprise multi-agent workflow engine orchestrating 6 specialized agents."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.crew_builder = CrewBuilder(config=self.config)
        self.handoff_manager = HandoffManager()
        self.consensus_validator = ConsensusValidator()
        self.conflict_resolver = ConflictResolver()
        self.decision_validator = DecisionValidator()
        self.decision_memory = DecisionMemory()

    def run_workflow(
        self,
        portfolio: Portfolio,
        opt_result: OptimizationResult,
        client: Optional[ClientProfile] = None,
    ) -> FinalDecisionPackage:
        """Run complete 6-agent decision intelligence workflow for a portfolio.

        Workflow sequence:
        Portfolio Arrives -> Analyst -> Risk -> Tax -> Compliance -> Explanation -> Orchestrator -> Package

        Args:
            portfolio: Portfolio domain model.
            opt_result: OptimizationResult from Phase 3.
            client: Optional ClientProfile instance.

        Returns:
            Validated FinalDecisionPackage object.
        """
        start_time = time.perf_counter()
        logger.info(f"Executing Multi-Agent Decision Workflow for portfolio {portfolio.portfolio_id}...")

        # Initialize shared workflow state
        state = SharedWorkflowState(
            portfolio_id=portfolio.portfolio_id,
            client_id=portfolio.client_id,
            workflow_status=WorkflowStatus.RUNNING,
        )

        # -------------------------------------------------------------
        # STEP 1: Portfolio Analyst Agent Execution
        # -------------------------------------------------------------
        analyst_res = self.crew_builder.analyst.analyze_portfolio(
            portfolio=portfolio,
            opt_result=opt_result,
        )
        state.record_task_result(analyst_res)

        # Handoff: Analyst -> Risk Manager
        handoff_1 = self.handoff_manager.create_handoff(
            sender="Portfolio Analyst",
            receiver="Risk Manager",
            portfolio_id=portfolio.portfolio_id,
            payload=analyst_res.output_data,
            previous_result=analyst_res,
        )

        # -------------------------------------------------------------
        # STEP 2: Risk Manager Agent Execution
        # -------------------------------------------------------------
        risk_res = self.crew_builder.risk_manager.assess_risk(
            portfolio=portfolio,
            opt_result=opt_result,
            input_context=handoff_1.payload,
        )
        state.record_task_result(risk_res)

        # Handoff: Risk Manager -> Tax Specialist
        handoff_2 = self.handoff_manager.create_handoff(
            sender="Risk Manager",
            receiver="Tax Specialist",
            portfolio_id=portfolio.portfolio_id,
            payload=risk_res.output_data,
            previous_result=risk_res,
        )

        # -------------------------------------------------------------
        # STEP 3: Tax Specialist Agent Execution
        # -------------------------------------------------------------
        tax_res = self.crew_builder.tax_specialist.evaluate_tax(
            portfolio=portfolio,
            opt_result=opt_result,
            input_context=handoff_2.payload,
        )
        state.record_task_result(tax_res)

        # Handoff: Tax Specialist -> Compliance Officer
        handoff_3 = self.handoff_manager.create_handoff(
            sender="Tax Specialist",
            receiver="Compliance Officer",
            portfolio_id=portfolio.portfolio_id,
            payload=tax_res.output_data,
            previous_result=tax_res,
        )

        # -------------------------------------------------------------
        # STEP 4: Compliance Officer Agent Execution
        # -------------------------------------------------------------
        comp_res = self.crew_builder.compliance_officer.verify_compliance(
            portfolio=portfolio,
            opt_result=opt_result,
            client=client,
            input_context=handoff_3.payload,
        )
        state.record_task_result(comp_res)

        # Handoff: Compliance Officer -> Explanation Writer
        handoff_4 = self.handoff_manager.create_handoff(
            sender="Compliance Officer",
            receiver="Explanation Writer",
            portfolio_id=portfolio.portfolio_id,
            payload=comp_res.output_data,
            previous_result=comp_res,
        )

        # -------------------------------------------------------------
        # STEP 5: Explanation Writer Agent Execution
        # -------------------------------------------------------------
        expl_res = self.crew_builder.explanation_writer.generate_explanations(
            portfolio=portfolio,
            opt_result=opt_result,
            client=client,
            agent_results=state.task_results,
        )
        state.record_task_result(expl_res)

        # -------------------------------------------------------------
        # STEP 6: Consensus & Conflict Resolution
        # -------------------------------------------------------------
        state.consensus_score = self.consensus_validator.compute_consensus_score(state.task_results)
        state, conflict_notes = self.conflict_resolver.resolve_conflicts(state)

        # -------------------------------------------------------------
        # STEP 7: Orchestrator Agent Output Aggregation
        # -------------------------------------------------------------
        self.decision_validator.validate_workflow_state(state)

        final_package = self.crew_builder.orchestrator.aggregate_decision_package(
            portfolio=portfolio,
            opt_result=opt_result,
            state=state,
            client=client,
        )

        self.decision_validator.validate_decision_package(final_package)
        self.decision_memory.store_decision(final_package)

        elapsed = time.perf_counter() - start_time
        logger.info(
            f"Multi-Agent Workflow COMPLETED for portfolio [{portfolio.portfolio_id}] in {elapsed:.3f}s | "
            f"Rec: {final_package.recommendation} | Consensus: {final_package.consensus_score:.2f} | Confidence: {final_package.confidence_score:.2f}"
        )

        return final_package
