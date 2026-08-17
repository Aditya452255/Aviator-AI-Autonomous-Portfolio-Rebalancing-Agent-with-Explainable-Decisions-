"""Benchmark Statistics analytics reporting excess return, Alpha, and Beta comparisons."""

from typing import List
import pandas as pd
from src.core.logger import get_logger
from src.models.benchmark_result import BenchmarkResult

logger = get_logger(__name__)


class BenchmarkStatistics:
    """Enterprise Benchmark Statistics analytics engine."""

    def compute_benchmark_comparison_df(self, results: List[BenchmarkResult]) -> pd.DataFrame:
        """Compute benchmark comparison summary DataFrame.

        Args:
            results: List of BenchmarkResult objects.

        Returns:
            DataFrame comparing portfolio against indices.
        """
        rows = []
        for r in results:
            rows.append({
                "portfolio_id": r.portfolio_id,
                "benchmark_name": r.benchmark_name,
                "portfolio_cagr_pct": round(r.portfolio_cagr * 100.0, 2),
                "benchmark_cagr_pct": round(r.benchmark_cagr * 100.0, 2),
                "excess_return_pct": round(r.excess_return * 100.0, 2),
                "alpha": r.alpha,
                "beta": r.beta,
                "tracking_error_pct": round(r.tracking_error * 100.0, 2),
                "information_ratio": r.information_ratio,
            })

        if not rows:
            return pd.DataFrame(columns=["portfolio_id", "benchmark_name", "excess_return_pct", "alpha", "beta"])

        return pd.DataFrame(rows)
