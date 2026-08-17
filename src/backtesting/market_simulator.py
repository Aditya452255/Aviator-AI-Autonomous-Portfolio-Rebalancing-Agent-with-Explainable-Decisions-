"""Scenario Market Simulator simulating return series under macro regime shocks."""

from typing import Dict, List, Optional
import numpy as np

from src.core.logger import get_logger

logger = get_logger(__name__)


class ScenarioMarketSimulator:
    """Enterprise Scenario Market Simulator for regime stress testing."""

    def simulate_regime_path(
        self,
        initial_value: float,
        days: int = 252,
        annual_return: float = 0.12,
        annual_volatility: float = 0.16,
        shock_pct: float = 0.0,
        seed: int = 42,
    ) -> np.ndarray:
        """Generate cumulative portfolio value path under regime parameters and shock drops.

        Args:
            initial_value: Starting portfolio capital value.
            days: Trading days.
            annual_return: Annual drift.
            annual_volatility: Annual volatility.
            shock_pct: Instantaneous shock percentage drop (e.g. -0.20 for 20% drop).
            seed: Random seed.

        Returns:
            Numpy array of cumulative daily values.
        """
        np.random.seed(seed)
        daily_mean = annual_return / 252.0
        daily_vol = annual_volatility / np.sqrt(252.0)

        returns = np.random.normal(daily_mean, daily_vol, days)

        # Apply shock drop at mid-point day if shock_pct is non-zero
        if shock_pct != 0.0:
            mid_idx = days // 2
            returns[mid_idx] += shock_pct

        path = np.cumprod(1.0 + returns) * initial_value
        return path
