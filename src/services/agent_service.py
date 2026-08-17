"""Enterprise Agent Service orchestrating Phase 4 Multi-Agent Decision Intelligence Layer."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

from src.core.config import AppConfig, load_config, _load_yaml_file
from src.core.logger import get_logger
from src.core.utils import Timer
from src.memory.decision_memory import FinalDecisionPackage
from src.models.client import ClientProfile
from src.models.optimization_result import OptimizationResult
from src.models.portfolio import Portfolio
from src.workflows.workflow_engine import MultiAgentWorkflowEngine

logger = get_logger(__name__)


class AgentService:
    """Enterprise service executing Phase 4 Multi-Agent Decision Intelligence workflows and exports."""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or load_config()
        self.output_dir = Path(self.config.storage.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        config_path = Path("config")
        agents_cfg = _load_yaml_file(config_path / "agents.yaml") if (config_path / "agents.yaml").exists() else {}

        self.workflow_engine = MultiAgentWorkflowEngine(config=agents_cfg)

    def run_decision_intelligence_cycle(
        self,
        portfolios: List[Portfolio],
        optimization_results: List[OptimizationResult],
        clients: Optional[List[ClientProfile]] = None,
        save_exports: bool = True,
    ) -> Tuple[List[FinalDecisionPackage], Dict]:
        """Execute Phase 4 multi-agent decision intelligence cycle.

        Args:
            portfolios: List of Portfolio objects.
            optimization_results: List of Phase 3 OptimizationResult objects.
            clients: List of ClientProfile objects.
            save_exports: True to export decision packages and task history.

        Returns:
            Tuple of (decision_packages_list, summary_analytics_dict).
        """
        with Timer(f"Phase 4 Decision Intelligence Cycle ({len(optimization_results)} portfolios)") as timer_metrics:
            logger.info("Executing Phase 4 Multi-Agent Decision Intelligence Layer Cycle...")

            port_map: Dict[str, Portfolio] = {p.portfolio_id: p for p in portfolios}
            client_map: Dict[str, ClientProfile] = {c.client_id: c for c in (clients or [])}

            packages: List[FinalDecisionPackage] = []
            task_history_rows = []

            for opt_res in optimization_results:
                p = port_map.get(opt_res.portfolio_id)
                if not p:
                    logger.warning(f"Portfolio {opt_res.portfolio_id} not found in active portfolio map. Skipping.")
                    continue

                cli = client_map.get(p.client_id)

                # Execute 6-agent Crew workflow
                pkg = self.workflow_engine.run_workflow(
                    portfolio=p,
                    opt_result=opt_res,
                    client=cli,
                )
                packages.append(pkg)

                # Record task history rows for export
                for agent_name, task_res in pkg.agent_outputs.items():
                    task_history_rows.append({
                        "decision_id": pkg.decision_id,
                        "portfolio_id": pkg.portfolio_id,
                        "agent_name": agent_name,
                        "task_id": task_res.task_id,
                        "confidence_score": task_res.confidence_score,
                        "recommendation": task_res.recommendation,
                        "status": task_res.status.value if hasattr(task_res.status, "value") else str(task_res.status),
                        "timestamp": task_res.timestamp,
                        "comments": task_res.comments,
                    })

            # Calculate Decision Analytics
            execute_count = sum(1 for p in packages if p.recommendation == "EXECUTE")
            modified_count = sum(1 for p in packages if p.recommendation == "MODIFIED_EXECUTE")
            reject_count = sum(1 for p in packages if p.recommendation == "REJECT")
            avg_consensus = float(pd.Series([p.consensus_score for p in packages]).mean()) if packages else 1.0
            avg_confidence = float(pd.Series([p.confidence_score for p in packages]).mean()) if packages else 1.0

            df_task_history = pd.DataFrame(task_history_rows)

            summary_analytics = {
                "cycle_metrics": {
                    "total_decision_packages": len(packages),
                    "execute_recommendations": execute_count,
                    "modified_recommendations": modified_count,
                    "rejected_recommendations": reject_count,
                    "average_consensus_score": round(avg_consensus, 4),
                    "average_confidence_score": round(avg_confidence, 4),
                    "execution_time_seconds": timer_metrics.get("elapsed_seconds", 0.0),
                },
                "decision_packages": [
                    {
                        "decision_id": p.decision_id,
                        "portfolio_id": p.portfolio_id,
                        "recommendation": p.recommendation,
                        "consensus_score": p.consensus_score,
                        "confidence_score": p.confidence_score,
                        "execution_readiness": p.execution_readiness.value if hasattr(p.execution_readiness, "value") else str(p.execution_readiness),
                    }
                    for p in packages
                ],
            }

            if save_exports:
                self.export_results(packages, df_task_history, summary_analytics)

            logger.info(
                f"Phase 4 Decision Intelligence Cycle finished. Packages: {len(packages)} | "
                f"Execute: {execute_count} | Modified: {modified_count} | Reject: {reject_count} | "
                f"Avg Consensus: {avg_consensus:.4f}"
            )
            return packages, summary_analytics

    def export_results(
        self,
        packages: List[FinalDecisionPackage],
        df_task_history: pd.DataFrame,
        summary_analytics: Dict,
    ) -> None:
        """Export Phase 4 decision packages and task history to Parquet, CSV, and JSON.

        Args:
            packages: List of FinalDecisionPackage objects.
            df_task_history: Task history DataFrame.
            summary_analytics: Summary metrics dict.
        """
        with Timer("Exporting Phase 4 Decision Intelligence Datasets"):
            pkg_rows = []
            for p in packages:
                pkg_rows.append({
                    "decision_id": p.decision_id,
                    "portfolio_id": p.portfolio_id,
                    "client_id": p.client_id,
                    "timestamp": p.timestamp,
                    "recommendation": p.recommendation,
                    "consensus_score": p.consensus_score,
                    "confidence_score": p.confidence_score,
                    "execution_readiness": p.execution_readiness.value if hasattr(p.execution_readiness, "value") else str(p.execution_readiness),
                    "client_explanation": p.explanations.get("client_explanation", ""),
                    "advisor_explanation": p.explanations.get("advisor_explanation", ""),
                    "compliance_explanation": p.explanations.get("compliance_explanation", ""),
                })

            df_pkg = pd.DataFrame(pkg_rows)

            df_pkg.to_parquet(self.output_dir / "decision_packages.parquet", index=False)
            df_task_history.to_parquet(self.output_dir / "agent_task_history.parquet", index=False)

            if self.config.storage.save_csv:
                df_pkg.to_csv(self.output_dir / "decision_packages.csv", index=False)
                df_task_history.to_csv(self.output_dir / "agent_task_history.csv", index=False)

            with open(self.output_dir / "decision_summary.json", "w", encoding="utf-8") as f:
                json.dump(summary_analytics, f, indent=2)

            logger.info(f"Saved Phase 4 decision intelligence outputs to {self.output_dir}")
