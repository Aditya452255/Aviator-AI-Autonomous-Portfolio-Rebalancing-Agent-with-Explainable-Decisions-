"""Surrogate ML model training on rebalancing decisions for SHAP/LIME feature attribution."""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from src.core.logger import get_logger

logger = get_logger(__name__)


class SurrogateModel:
    """Enterprise surrogate classifier modeling autonomous portfolio rebalancing decisions."""

    FEATURE_NAMES = [
        "portfolio_drift",
        "risk_category_code",
        "sector_exposure_drift",
        "market_volatility",
        "liquidity_score",
        "tax_impact",
        "days_since_last_rebalance",
        "portfolio_size",
        "cash_allocation",
    ]

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=42,
        )
        self.is_fitted = False

    def extract_features(
        self,
        portfolio_id: str,
        drift_score: float,
        risk_category_str: str = "Balanced",
        sector_drift: float = 0.02,
        market_volatility: float = 0.15,
        liquidity_score: float = 85.0,
        tax_impact: float = 0.0,
        days_since_rebalance: float = 45.0,
        portfolio_size: float = 100000.0,
        cash_allocation: float = 0.05,
    ) -> pd.DataFrame:
        """Extract a single-row feature DataFrame for a portfolio decision.

        Args:
            portfolio_id: Target portfolio ID.
            drift_score: Portfolio RMS drift score.
            risk_category_str: Risk Category string.
            sector_drift: Maximum sector exposure drift.
            market_volatility: Market annualized volatility.
            liquidity_score: Average portfolio liquidity score.
            tax_impact: Net tax impact amount.
            days_since_rebalance: Days since last rebalancing.
            portfolio_size: Total portfolio market value.
            cash_allocation: Cash weight fraction.

        Returns:
            DataFrame containing feature row.
        """
        # Map risk category string to numerical code
        risk_map = {
            "ultra_conservative": 1,
            "conservative": 2,
            "balanced": 3,
            "aggressive": 4,
            "ultra_aggressive": 5,
        }
        rc_code = risk_map.get(risk_category_str.lower(), 3)

        row = {
            "portfolio_drift": float(drift_score),
            "risk_category_code": float(rc_code),
            "sector_exposure_drift": float(sector_drift),
            "market_volatility": float(market_volatility),
            "liquidity_score": float(liquidity_score),
            "tax_impact": float(tax_impact),
            "days_since_last_rebalance": float(days_since_rebalance),
            "portfolio_size": float(portfolio_size),
            "cash_allocation": float(cash_allocation),
        }
        return pd.DataFrame([row], columns=self.FEATURE_NAMES)

    def fit_synthetic_baseline(self, num_samples: int = 500) -> None:
        """Fit surrogate model on synthetic decision domain data.

        Args:
            num_samples: Number of synthetic training samples.
        """
        np.random.seed(42)
        drifts = np.random.uniform(0.01, 0.12, num_samples)
        rc_codes = np.random.randint(1, 6, num_samples)
        sec_drifts = np.random.uniform(0.005, 0.08, num_samples)
        vols = np.random.uniform(0.10, 0.35, num_samples)
        liq = np.random.uniform(50.0, 95.0, num_samples)
        taxes = np.random.uniform(-5000.0, 10000.0, num_samples)
        days = np.random.uniform(1.0, 180.0, num_samples)
        sizes = np.random.uniform(50000.0, 1000000.0, num_samples)
        cash = np.random.uniform(0.02, 0.20, num_samples)

        X = pd.DataFrame({
            "portfolio_drift": drifts,
            "risk_category_code": rc_codes,
            "sector_exposure_drift": sec_drifts,
            "market_volatility": vols,
            "liquidity_score": liq,
            "tax_impact": taxes,
            "days_since_last_rebalance": days,
            "portfolio_size": sizes,
            "cash_allocation": cash,
        }, columns=self.FEATURE_NAMES)

        # Decision rule target: Rebalance (1) if drift > 0.04 or (days > 90 and drift > 0.025)
        y = ((drifts > 0.04) | ((days > 90.0) & (drifts > 0.025))).astype(int)

        self.model.fit(X, y)
        self.is_fitted = True
        logger.debug(f"Surrogate RandomForest model fitted on {num_samples} baseline decision samples.")

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict rebalance probability.

        Args:
            X: Feature DataFrame.

        Returns:
            Numpy array of probabilities.
        """
        if not self.is_fitted:
            self.fit_synthetic_baseline()
        return self.model.predict_proba(X)
