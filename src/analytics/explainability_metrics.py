"""Explainability Metrics analytics reporting quality scores and SHAP importance rankings."""

from typing import Any, Dict, List
import numpy as np
import pandas as pd

from src.core.logger import get_logger
from src.models.explainability_result import ExplainabilityResult

logger = get_logger(__name__)


class ExplainabilityMetrics:
    """Enterprise analytics engine summarizing explainability quality and SHAP metrics."""

    def compute_metrics_summary(self, results: List[ExplainabilityResult]) -> Dict[str, Any]:
        """Compute aggregate summary metrics across explainability results.

        Args:
            results: List of ExplainabilityResult domain models.

        Returns:
            Dictionary containing aggregate quality scores and top feature drivers.
        """
        if not results:
            return {"total_explanations_generated": 0}

        total_runs = len(results)
        comp_scores = [r.quality_scores.completeness_score for r in results]
        acc_scores = [r.quality_scores.accuracy_score for r in results]
        read_scores = [r.quality_scores.readability_score for r in results]
        cons_scores = [r.quality_scores.consistency_score for r in results]
        overall_scores = [r.quality_scores.overall_score for r in results]

        # Top feature drivers frequency
        driver_counts: Dict[str, int] = {}
        for r in results:
            if r.feature_attributions:
                top_feat = r.feature_attributions[0].feature_name
                driver_counts[top_feat] = driver_counts.get(top_feat, 0) + 1

        return {
            "total_explanations_generated": total_runs,
            "average_completeness_score": round(float(np.mean(comp_scores)), 4),
            "average_accuracy_score": round(float(np.mean(acc_scores)), 4),
            "average_readability_score": round(float(np.mean(read_scores)), 4),
            "average_consistency_score": round(float(np.mean(cons_scores)), 4),
            "average_overall_quality_score": round(float(np.mean(overall_scores)), 4),
            "primary_decision_drivers": driver_counts,
        }
