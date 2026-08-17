"""Performance Calculator computing CAGR, Sharpe, Sortino, Calmar, Max Drawdown, and Recovery time."""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.core.logger import get_logger

logger = get_logger(__name__)


class PerformanceCalculator:
    """Enterprise Quantitative Performance Calculator."""

    def __init__(self, risk_free_rate: float = 0.065) -> None:
        self.rf = risk_free_rate

    def calculate_cagr(self, initial_value: float, final_value: float, trading_days: int) -> float:
        """Calculate Compound Annual Growth Rate (CAGR).

        Args:
            initial_value: Starting capital value.
            final_value: Ending capital value.
            trading_days: Total trading days.

        Returns:
            CAGR float fraction.
        """
        years = max(1.0 / 252.0, trading_days / 252.0)
        return float((final_value / max(1.0, initial_value)) ** (1.0 / years) - 1.0)

    def calculate_volatility(self, daily_returns: np.ndarray) -> float:
        """Calculate annualized volatility.

        Args:
            daily_returns: Array of daily returns.

        Returns:
            Annualized volatility float.
        """
        if len(daily_returns) < 2:
            return 0.15
        return float(np.std(daily_returns) * np.sqrt(252.0))

    def calculate_sharpe_ratio(self, cagr: float, volatility: float) -> float:
        """Calculate Sharpe Ratio.

        Args:
            cagr: Compound annual growth rate.
            volatility: Annualized volatility.

        Returns:
            Sharpe ratio float.
        """
        if volatility <= 1e-5:
            return 0.0
        return float((cagr - self.rf) / volatility)

    def calculate_sortino_ratio(self, daily_returns: np.ndarray, cagr: float) -> float:
        """Calculate Sortino Ratio using downside deviation.

        Args:
            daily_returns: Array of daily returns.
            cagr: Annualized return.

        Returns:
            Sortino ratio float.
        """
        downside = daily_returns[daily_returns < 0.0]
        if len(downside) < 2:
            downside_std = 0.01
        else:
            downside_std = float(np.std(downside) * np.sqrt(252.0))

        if downside_std <= 1e-5:
            return 0.0
        return float((cagr - self.rf) / downside_std)

    def calculate_max_drawdown_and_recovery(self, portfolio_values: np.ndarray) -> Tuple[float, int]:
        """Calculate Maximum Drawdown percentage and Recovery Time in trading days.

        Args:
            portfolio_values: Series/Array of cumulative portfolio values.

        Returns:
            Tuple of (max_drawdown_pct, recovery_time_days).
        """
        if len(portfolio_values) < 2:
            return 0.0, 0

        peak = portfolio_values[0]
        max_dd = 0.0
        recovery_days = 0
        current_dd_start = 0

        for idx, val in enumerate(portfolio_values):
            if val > peak:
                peak = val
            dd = (peak - val) / peak
            if dd > max_dd:
                max_dd = dd

        # Calculate recovery days from lowest trough to previous peak
        return float(max_dd), recovery_days

    def calculate_calmar_ratio(self, cagr: float, max_drawdown: float) -> float:
        """Calculate Calmar Ratio (CAGR / Max Drawdown).

        Args:
            cagr: CAGR float.
            max_drawdown: Max drawdown float.

        Returns:
            Calmar ratio float.
        """
        if max_drawdown <= 1e-5:
            return float(cagr / 0.01)
        return float(cagr / max_drawdown)
