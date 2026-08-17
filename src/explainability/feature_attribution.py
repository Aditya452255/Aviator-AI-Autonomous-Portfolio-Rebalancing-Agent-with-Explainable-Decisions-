"""Feature Attribution Engine ranking global and local decision feature contributions."""

from typing import Dict, List
import numpy as np
from src.core.logger import get_logger
from src.models.feature_importance import FeatureAttribution, FeatureAttributionSummary

logger = get_logger(__name__)


class FeatureAttributionEngine:
    """Enterprise Feature Attribution Engine ranking SHAP and model importances."""

    def rank_attributions(
        self,
        portfolio_id: str,
        shap_values: Dict[str, float],
        global_importances: Dict[str, float],
    ) -> FeatureAttributionSummary:
        """Compute ranked FeatureAttribution objects with normalized contributions.

        Args:
            portfolio_id: Target portfolio ID.
            shap_values: Map of feature_name -> local SHAP value.
            global_importances: Map of feature_name -> global model importance.

        Returns:
            FeatureAttributionSummary domain model object.
        """
        attributions: List[FeatureAttribution] = []

        total_abs_shap = sum(abs(v) for v in shap_values.values()) or 1e-5

        for feat_name, shap_val in shap_values.items():
            glob_imp = global_importances.get(feat_name, 0.10)
            loc_imp = abs(shap_val)
            norm_contrib = (loc_imp / total_abs_shap) * 100.0

            attr = FeatureAttribution(
                feature_name=feat_name,
                global_importance=round(float(glob_imp), 4),
                local_importance=round(float(loc_imp), 4),
                normalized_contribution=round(float(norm_contrib), 2),
                signed_contribution=round(float(shap_val), 4),
            )
            attributions.append(attr)

        # Sort by local importance descending
        attributions.sort(key=lambda x: abs(x.signed_contribution), reverse=True)

        top_driver = attributions[0].feature_name if attributions else "portfolio_drift"

        return FeatureAttributionSummary(
            portfolio_id=portfolio_id,
            attributions=attributions,
            top_driver=top_driver,
        )
