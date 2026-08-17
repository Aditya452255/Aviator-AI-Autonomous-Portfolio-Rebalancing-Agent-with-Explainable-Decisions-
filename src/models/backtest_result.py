"""Backtest result domain models for strategy comparison and historical replay."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class StrategyPerformance(BaseModel):
    """Performance metrics for a single portfolio strategy."""

    strategy_name: str = Field(..., description="Strategy identifier")
    cagr: float = Field(..., description="Compound Annual Growth Rate")
    annual_return: float = Field(..., description="Mean annual return")
    volatility: float = Field(..., description="Annualized volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    sortino_ratio: float = Field(..., description="Sortino ratio")
    calmar_ratio: float = Field(..., description="Calmar ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown percentage")
    recovery_time_days: int = Field(..., description="Days to recover from max drawdown")
    total_trades_count: int = Field(..., description="Total trades executed")
    total_transaction_costs: float = Field(..., description="Cumulative transaction fees")
    net_after_tax_return: float = Field(..., description="Net after-tax CAGR")


class BacktestResult(BaseModel):
    """Complete backtest simulation result."""

    backtest_id: str = Field(..., description="Unique backtest ID")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    replay_frequency: str = Field(..., description="Replay interval (DAILY, MONTHLY, etc.)")
    trading_days: int = Field(..., description="Total trading days simulated")
    strategy_performances: Dict[str, StrategyPerformance] = Field(default_factory=dict)
    best_strategy: str = Field(..., description="Top performing strategy by Sharpe Ratio")
