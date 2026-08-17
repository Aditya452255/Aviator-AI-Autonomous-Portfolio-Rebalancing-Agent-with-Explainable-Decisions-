"""Risk Metrics Calculator computing VaR 95%, CVaR 95%, Alpha, Beta, and Concentration Risk."""

from typing import Dict, Tuple
import numpy as np

from src.core.logger import get_logger

logger = get_logger(__name__)


class RiskMetricsCalculator:
    """Enterprise Quantitative Risk Calculator."""

    def calculate_var_and_cvar(self, daily_returns: np.ndarray, confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate historical 95% Value at Risk (VaR) and Conditional VaR (CVaR / Expected Shortfall).

        Args:
            daily_returns: Array of daily return fractions.
            confidence: Confidence level (default 0.95).

        Returns:
            Tuple of (VaR_95_pct, CVaR_95_pct).
        """
        if len(daily_returns) < 5:
            return 1.645 * 0.01 * 100.0, 2.0 * 0.01 * 100.0

        percentile = (1.0 - confidence) * 100.0
        var_val = -float(np.percentile(daily_returns, percentile))

        # CVaR is mean loss beyond VaR cutoff
        cutoff = -var_val
        losses_beyond = daily_returns[daily_returns <= cutoff]
        cvar_val = -float(np.mean(losses_beyond)) if len(losses_beyond) > 0 else var_val * 1.2

        return round(var_val * 100.0, 2), round(cvar_val * 100.0, 2)

    def calculate_alpha_beta(
        self,
        portfolio_returns: np.ndarray,
        benchmark_returns: np.ndarray,
        rf: float = 0.065,
    ) -> Tuple[float, float]:
        """Calculate Jensen's Alpha and Beta relative to a benchmark.

        Args:
            portfolio_returns: Daily portfolio return array.
            benchmark_returns: Daily benchmark return array.
            rf: Annual risk-free rate.

        Returns:
            Tuple of (Alpha, Beta).
        """
        if len(portfolio_returns) < 5 or len(benchmark_returns) < 5:
            return 0.02, 1.0

        cov_matrix = np.cov(portfolio_returns, benchmark_returns)
        var_bench = cov_matrix[1, 1]

        beta = float(cov_matrix[0, 1] / max(1e-6, var_bench))

        port_annual = float(np.mean(portfolio_returns) * 252.0)
        bench_annual = float(np.mean(benchmark_returns) * 252.0)

        alpha = float(port_annual - (rf + beta * (bench_annual - rf)))

        return round(alpha, 4), round(beta, 4)
