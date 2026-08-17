"""Explanation Statistics analytics reporting feature importance distributions."""

from typing import List
import pandas as pd

from src.core.logger import get_logger
from src.models.explainability_result import ExplainabilityResult

logger = get_logger(__name__)


class ExplanationStatistics:
    """Enterprise analytics engine computing global feature importance statistics."""

    def compute_feature_importance_df(self, results: List[ExplainabilityResult]) -> pd.DataFrame:
        """Compute aggregated feature importance summary table across all explanation runs.

        Args:
            results: List of ExplainabilityResult domain models.

        Returns:
            DataFrame containing feature names, mean SHAP magnitude, and global ranking.
        """
        rows = []
        for r in results:
            for attr in r.feature_attributions:
                rows.append({
                    "portfolio_id": r.portfolio_id,
                    "feature_name": attr.feature_name,
                    "local_importance": attr.local_importance,
                    "normalized_contribution": attr.normalized_contribution,
                    "signed_contribution": attr.signed_contribution,
                })

        if not rows:
            return pd.DataFrame(columns=["portfolio_id", "feature_name", "local_importance", "normalized_contribution"])

        df_raw = pd.DataFrame(rows)
        df_summary = (
            df_raw.groupby("feature_name")
            .agg({
                "local_importance": "mean",
                "normalized_contribution": "mean",
                "signed_contribution": "mean",
            })
            .reset_index()
            .sort_values(by="local_importance", ascending=False)
        )
        return df_summary
