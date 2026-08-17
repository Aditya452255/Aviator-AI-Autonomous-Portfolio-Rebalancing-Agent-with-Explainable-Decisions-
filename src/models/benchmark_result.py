"""Benchmark comparison result domain models."""

from pydantic import BaseModel, Field


class BenchmarkResult(BaseModel):
    """Comparative analysis against market benchmark index."""

    portfolio_id: str = Field(..., description="Target portfolio ID")
    benchmark_name: str = Field(..., description="Benchmark name (NIFTY 50, 60/40, etc.)")
    portfolio_cagr: float = Field(..., description="Portfolio CAGR")
    benchmark_cagr: float = Field(..., description="Benchmark CAGR")
    excess_return: float = Field(..., description="Alpha excess return (Portfolio - Benchmark)")
    portfolio_volatility: float = Field(..., description="Portfolio annual volatility")
    benchmark_volatility: float = Field(..., description="Benchmark annual volatility")
    alpha: float = Field(..., description="Jensen's Alpha")
    beta: float = Field(..., description="Portfolio Beta relative to benchmark")
    tracking_error: float = Field(..., description="Tracking Error relative to benchmark")
    information_ratio: float = Field(..., description="Information Ratio")
