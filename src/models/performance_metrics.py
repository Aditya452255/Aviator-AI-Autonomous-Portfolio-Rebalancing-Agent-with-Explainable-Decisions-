"""Comprehensive quantitative performance and risk metrics models."""

from pydantic import BaseModel, Field


class ReturnAnalysisModel(BaseModel):
    """Return analysis metrics."""

    gross_return_cagr: float
    net_return_cagr: float
    after_tax_cagr: float
    total_transaction_costs: float
    total_tax_savings: float


class RiskMetricsModel(BaseModel):
    """Risk metrics model."""

    var_95_daily: float
    cvar_95_daily: float
    alpha: float
    beta: float
    concentration_risk_score: float
    liquidity_risk_score: float


class PerformanceMetrics(BaseModel):
    """Unified performance metrics summary model."""

    portfolio_id: str
    cagr: float
    annual_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    recovery_time_days: int
    tracking_error: float
    information_ratio: float
    turnover: float
    returns: ReturnAnalysisModel
    risk: RiskMetricsModel
