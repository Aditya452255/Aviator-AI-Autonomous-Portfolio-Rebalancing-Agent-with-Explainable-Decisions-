"""Enterprise Explainability Service orchestrating Phase 5 XAI engine and multi-audience exports."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

from src.analytics.explainability_metrics import ExplainabilityMetrics
from src.analytics.explanation_statistics import ExplanationStatistics
from src.core.config import AppConfig, load_config, _load_yaml_file
from src.core.logger import get_logger
from src.core.utils import Timer
from src.explainability.counterfactual_engine import CounterfactualEngine
from src.explainability.decision_explainer import DecisionExplainer
from src.explainability.explanation_quality import ExplanationQualityEngine
from src.explainability.explanation_validator import ExplanationValidator
from src.explainability.feature_attribution import FeatureAttributionEngine
from src.explainability.lime_engine import LIMEEngine
from src.explainability.shap_engine import SHAPEngine
from src.explainability.surrogate_model import SurrogateModel
from src.explainability.visualization_generator import VisualizationGenerator
from src.memory.decision_memory import FinalDecisionPackage
from src.models.explainability_result import ExplainabilityResult
from src.models.portfolio import Portfolio

logger = get_logger(__name__)


class ExplainabilityService:
    """Enterprise orchestration service executing Phase 5 Explainable AI Engine."""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or load_config()
        self.output_dir = Path(self.config.storage.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        config_path = Path("config")
        xai_cfg = _load_yaml_file(config_path / "explainability.yaml") if (config_path / "explainability.yaml").exists() else {}
        model_cfg = _load_yaml_file(config_path / "model.yaml") if (config_path / "model.yaml").exists() else {}

        self.surrogate_model = SurrogateModel(config=model_cfg)
        self.surrogate_model.fit_synthetic_baseline()

        self.shap_engine = SHAPEngine(surrogate_model=self.surrogate_model)
        self.lime_engine = LIMEEngine(surrogate_model=self.surrogate_model)
        self.counterfactual_engine = CounterfactualEngine()
        self.attribution_engine = FeatureAttributionEngine()
        self.decision_explainer = DecisionExplainer()
        self.validator = ExplanationValidator()
        self.quality_engine = ExplanationQualityEngine()
        self.viz_generator = VisualizationGenerator(output_dir=self.output_dir / "visualizations")
        self.metrics_analyzer = ExplainabilityMetrics()
        self.stats_analyzer = ExplanationStatistics()

    def run_explainability_cycle(
        self,
        portfolios: List[Portfolio],
        decision_packages: List[FinalDecisionPackage],
        save_exports: bool = True,
        generate_plots: bool = True,
    ) -> Tuple[List[ExplainabilityResult], Dict]:
        """Execute Phase 5 XAI engine across decision packages.

        Args:
            portfolios: Complete list of Portfolio objects.
            decision_packages: List of Phase 4 FinalDecisionPackage objects.
            save_exports: True to persist parquet, csv, and json outputs.
            generate_plots: True to generate PNG plot images.

        Returns:
            Tuple of (explainability_results_list, summary_metrics_dict).
        """
        with Timer(f"Phase 5 Explainability Cycle ({len(decision_packages)} decision packages)") as timer_metrics:
            logger.info("Executing Phase 5 Explainable AI (XAI) Engine Cycle...")

            port_map: Dict[str, Portfolio] = {p.portfolio_id: p for p in portfolios}
            results: List[ExplainabilityResult] = []

            for dec_pkg in decision_packages:
                p = port_map.get(dec_pkg.portfolio_id)
                if not p:
                    logger.warning(f"Portfolio {dec_pkg.portfolio_id} not found for explainability. Skipping.")
                    continue

                exp_id = f"XAI_{p.portfolio_id}"
                opt_sum = dec_pkg.optimization_summary

                # 1. Feature Extraction
                X_sample = self.surrogate_model.extract_features(
                    portfolio_id=p.portfolio_id,
                    drift_score=opt_sum.get("drift_before", 0.05),
                    risk_category_str=p.risk_category.value if hasattr(p.risk_category, "value") else str(p.risk_category),
                    tax_impact=opt_sum.get("total_tax", 0.0),
                    portfolio_size=p.total_market_value,
                    cash_allocation=p.cash_balance / max(1.0, p.total_market_value),
                )

                # 2. Compute SHAP Values
                with Timer(f"SHAP Execution [{p.portfolio_id}]") as shap_timer:
                    shap_vals = self.shap_engine.compute_shap_values(X_sample)
                global_imps = self.shap_engine.get_global_feature_importance()

                # 3. Compute LIME Explanations
                with Timer(f"LIME Execution [{p.portfolio_id}]") as lime_timer:
                    lime_contribs = self.lime_engine.compute_lime_explanation(X_sample)

                # 4. Feature Attribution Ranking
                attr_summary = self.attribution_engine.rank_attributions(
                    portfolio_id=p.portfolio_id,
                    shap_values=shap_vals,
                    global_importances=global_imps,
                )

                # 5. Counterfactual Engine
                cf_summary = self.counterfactual_engine.generate_counterfactuals(
                    portfolio_id=p.portfolio_id,
                    features=X_sample.iloc[0].to_dict(),
                    current_decision=dec_pkg.recommendation,
                )
                cf_text = cf_summary.counterfactuals[0].impact_description if cf_summary.counterfactuals else "N/A"

                # 6. Multi-Audience Explanation Generation
                explanations = self.decision_explainer.generate_all_explanations(
                    portfolio=p,
                    decision_package=dec_pkg,
                    shap_values=shap_vals,
                    counterfactual_str=cf_text,
                    top_driver=attr_summary.top_driver,
                )

                cli_exp = explanations["client"]
                adv_exp = explanations["advisor"]
                comp_exp = explanations["compliance"]

                # 7. Validate & Quality Scoring
                self.validator.validate_client_explanation(cli_exp)
                self.validator.validate_advisor_explanation(adv_exp)
                q_scores = self.quality_engine.evaluate_quality(cli_exp, adv_exp, comp_exp)

                # 8. Visualizations
                viz_paths = []
                if generate_plots:
                    p_bar = self.viz_generator.generate_feature_importance_bar_chart(p.portfolio_id, shap_vals)
                    p_cf = self.viz_generator.generate_counterfactual_comparison_chart(
                        portfolio_id=p.portfolio_id,
                        current_drift=opt_sum.get("drift_before", 0.05),
                        threshold_drift=0.042,
                    )
                    viz_paths.extend([p_bar, p_cf])

                exp_result = ExplainabilityResult(
                    explanation_id=exp_id,
                    portfolio_id=p.portfolio_id,
                    decision_id=dec_pkg.decision_id,
                    feature_attributions=attr_summary.attributions,
                    shap_values=shap_vals,
                    lime_contributions=lime_contribs,
                    counterfactuals=cf_summary.counterfactuals,
                    client_explanation=cli_exp,
                    advisor_explanation=adv_exp,
                    compliance_explanation=comp_exp,
                    quality_scores=q_scores,
                    visualization_paths=viz_paths,
                )

                logger.info(
                    f"Generated XAI Package [{p.portfolio_id}] | Top Driver: {attr_summary.top_driver} | "
                    f"SHAP Time: {shap_timer.get('elapsed_seconds', 0.0):.3f}s | "
                    f"LIME Time: {lime_timer.get('elapsed_seconds', 0.0):.3f}s | "
                    f"Overall Quality Score: {q_scores.overall_score:.4f}"
                )
                results.append(exp_result)

            # Compute Analytics
            summary_metrics = self.metrics_analyzer.compute_metrics_summary(results)
            df_feature_imp = self.stats_analyzer.compute_feature_importance_df(results)

            if save_exports:
                self.export_results(results, df_feature_imp, summary_metrics)

            logger.info("Phase 5 Explainable AI (XAI) Engine successfully completed.")
            return results, summary_metrics

    def export_results(
        self,
        results: List[ExplainabilityResult],
        df_feature_imp: pd.DataFrame,
        summary_metrics: Dict,
    ) -> None:
        """Export Phase 5 explainability datasets to Parquet, CSV, and JSON.

        Args:
            results: List of ExplainabilityResult domain models.
            df_feature_imp: Feature importance DataFrame.
            summary_metrics: Summary metrics dict.
        """
        with Timer("Exporting Phase 5 Explainability Datasets"):
            cli_rows = []
            adv_rows = []
            comp_rows = []
            cf_rows = []

            for r in results:
                c = r.client_explanation
                cli_rows.append({
                    "portfolio_id": c.portfolio_id,
                    "summary": c.summary,
                    "word_count": c.word_count,
                    "benefits": c.benefits,
                    "costs_and_taxes": c.costs_and_taxes,
                    "risks": c.risks,
                    "overall_quality_score": r.quality_scores.overall_score,
                })

                a = r.advisor_explanation
                adv_rows.append({
                    "portfolio_id": a.portfolio_id,
                    "summary": a.summary,
                    "word_count": a.word_count,
                    "drift_analysis": a.drift_analysis,
                    "tracking_error_analysis": a.tracking_error_analysis,
                    "tax_and_cost_analysis": a.tax_and_cost_analysis,
                    "liquidity_and_execution": a.liquidity_and_execution,
                })

                m = r.compliance_explanation
                comp_rows.append({
                    "decision_id": m.decision_id,
                    "portfolio_id": m.portfolio_id,
                    "timestamp": m.timestamp,
                    "audit_summary": m.audit_summary,
                    "agent_consensus": m.agent_consensus,
                    "shap_summary": m.shap_summary,
                    "counterfactual_summary": m.counterfactual_summary,
                    "model_version": m.model_version,
                })

                for cf in r.counterfactuals:
                    cf_rows.append({
                        "portfolio_id": r.portfolio_id,
                        "feature_name": cf.feature_name,
                        "current_value": cf.current_value,
                        "counterfactual_value": cf.counterfactual_value,
                        "current_decision": cf.current_decision,
                        "counterfactual_decision": cf.counterfactual_decision,
                        "impact_description": cf.impact_description,
                    })

            df_cli = pd.DataFrame(cli_rows)
            df_adv = pd.DataFrame(adv_rows)
            df_comp = pd.DataFrame(comp_rows)
            df_cf = pd.DataFrame(cf_rows)

            df_cli.to_parquet(self.output_dir / "client_explanations.parquet", index=False)
            df_adv.to_parquet(self.output_dir / "advisor_explanations.parquet", index=False)
            df_comp.to_parquet(self.output_dir / "compliance_explanations.parquet", index=False)

            if self.config.storage.save_csv:
                df_cli.to_csv(self.output_dir / "client_explanations.csv", index=False)
                df_adv.to_csv(self.output_dir / "advisor_explanations.csv", index=False)
                df_comp.to_csv(self.output_dir / "compliance_explanations.csv", index=False)

            df_feature_imp.to_csv(self.output_dir / "feature_importance.csv", index=False)
            df_cf.to_csv(self.output_dir / "counterfactuals.csv", index=False)

            with open(self.output_dir / "explainability_metrics.json", "w", encoding="utf-8") as f:
                json.dump(summary_metrics, f, indent=2)

            logger.info(f"Saved Phase 5 explainability outputs to {self.output_dir}")
