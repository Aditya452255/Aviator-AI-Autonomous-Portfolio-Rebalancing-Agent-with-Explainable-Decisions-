"""SHAP Engine computing TreeSHAP feature attributions and explainability plots."""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    shap = None
    SHAP_AVAILABLE = False

from src.core.logger import get_logger
from src.explainability.surrogate_model import SurrogateModel

logger = get_logger(__name__)


class SHAPEngine:
    """Enterprise SHAP Engine computing local and global TreeSHAP values."""

    def __init__(self, surrogate_model: SurrogateModel) -> None:
        self.surrogate = surrogate_model
        if not self.surrogate.is_fitted:
            self.surrogate.fit_synthetic_baseline()

        if SHAP_AVAILABLE:
            try:
                self.explainer = shap.TreeExplainer(self.surrogate.model)
            except Exception as e:
                logger.warning(f"TreeExplainer failed: {e}. Using fallback feature importances.")
                self.explainer = None
        else:
            self.explainer = None

    def compute_shap_values(self, X_sample: pd.DataFrame) -> Dict[str, float]:
        """Compute local SHAP values for a single portfolio feature row.

        Args:
            X_sample: Feature row DataFrame (1 sample).

        Returns:
            Dictionary of feature_name -> shap_value.
        """
        feature_names = list(X_sample.columns)

        if self.explainer is not None and SHAP_AVAILABLE:
            try:
                shap_vals = self.explainer.shap_values(X_sample)
                if isinstance(shap_vals, list):
                    vals = shap_vals[1][0]
                elif len(shap_vals.shape) == 3:
                    vals = shap_vals[0, :, 1]
                else:
                    vals = shap_vals[0]
                return {feature_names[i]: float(vals[i]) for i in range(len(feature_names))}
            except Exception as e:
                logger.warning(f"SHAP evaluation error: {e}. Falling back to baseline feature importances.")

        # Robust Fallback attribution based on global feature importances and deviation
        importances = self.surrogate.model.feature_importances_
        res = {}
        for i, fn in enumerate(feature_names):
            # Directional attribution based on feature magnitude
            val = float(X_sample[fn].iloc[0]) if fn in X_sample else 0.0
            sign = 1.0 if val > 0.03 else -1.0
            res[fn] = round(sign * float(importances[i]), 4)

        return res

    def get_global_feature_importance(self) -> Dict[str, float]:
        """Get global feature importance from surrogate model.

        Returns:
            Dictionary mapping feature_name to importance score.
        """
        importances = self.surrogate.model.feature_importances_
        feature_names = self.surrogate.FEATURE_NAMES
        return {feature_names[i]: float(importances[i]) for i in range(len(feature_names))}
