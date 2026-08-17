"""LIME Engine generating local interpretable model-agnostic explanations."""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd

try:
    from lime import lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    lime_tabular = None
    LIME_AVAILABLE = False

from src.core.logger import get_logger
from src.explainability.surrogate_model import SurrogateModel

logger = get_logger(__name__)


class LIMEEngine:
    """Enterprise LIME Engine computing local tabular explanations."""

    def __init__(self, surrogate_model: SurrogateModel) -> None:
        self.surrogate = surrogate_model
        if not self.surrogate.is_fitted:
            self.surrogate.fit_synthetic_baseline()

        if LIME_AVAILABLE:
            try:
                np.random.seed(42)
                drifts = np.random.uniform(0.01, 0.12, 100)
                rc_codes = np.random.randint(1, 6, 100)
                sec_drifts = np.random.uniform(0.005, 0.08, 100)
                vols = np.random.uniform(0.10, 0.35, 100)
                liq = np.random.uniform(50.0, 95.0, 100)
                taxes = np.random.uniform(-5000.0, 10000.0, 100)
                days = np.random.uniform(1.0, 180.0, 100)
                sizes = np.random.uniform(50000.0, 1000000.0, 100)
                cash = np.random.uniform(0.02, 0.20, 100)

                self.background_df = pd.DataFrame({
                    "portfolio_drift": drifts,
                    "risk_category_code": rc_codes,
                    "sector_exposure_drift": sec_drifts,
                    "market_volatility": vols,
                    "liquidity_score": liq,
                    "tax_impact": taxes,
                    "days_since_last_rebalance": days,
                    "portfolio_size": sizes,
                    "cash_allocation": cash,
                }, columns=self.surrogate.FEATURE_NAMES)

                self.explainer = lime_tabular.LimeTabularExplainer(
                    training_data=self.background_df.values,
                    feature_names=self.surrogate.FEATURE_NAMES,
                    class_names=["NO_REBALANCE", "REBALANCE"],
                    mode="classification",
                    random_state=42,
                )
            except Exception as e:
                logger.warning(f"LIME explainer init warning: {e}")
                self.explainer = None
        else:
            self.explainer = None

    def compute_lime_explanation(self, X_sample: pd.DataFrame) -> Dict[str, float]:
        """Compute local LIME feature contributions for a single portfolio sample.

        Args:
            X_sample: Feature row DataFrame (1 sample).

        Returns:
            Dictionary mapping feature_name to LIME contribution score.
        """
        if self.explainer is not None and LIME_AVAILABLE:
            try:
                row_values = X_sample.values[0]
                exp = self.explainer.explain_instance(
                    data_row=row_values,
                    predict_fn=self.surrogate.model.predict_proba,
                    num_features=len(self.surrogate.FEATURE_NAMES),
                )

                res: Dict[str, float] = {}
                for feature_cond, weight in exp.as_list():
                    for fn in self.surrogate.FEATURE_NAMES:
                        if fn in feature_cond:
                            res[fn] = float(weight)
                            break
                return res
            except Exception as e:
                logger.warning(f"LIME evaluation error: {e}. Falling back to baseline feature weights.")

        # Fallback local weights
        importances = self.surrogate.model.feature_importances_
        res = {}
        for i, fn in enumerate(self.surrogate.FEATURE_NAMES):
            val = float(X_sample[fn].iloc[0]) if fn in X_sample else 0.0
            sign = 1.0 if val > 0.03 else -1.0
            res[fn] = round(sign * float(importances[i]) * 0.8, 4)

        return res
