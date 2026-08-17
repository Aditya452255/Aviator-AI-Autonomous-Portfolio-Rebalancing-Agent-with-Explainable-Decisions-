"""Domain models for executable trade recommendations."""

from typing import Optional
from pydantic import BaseModel, Field
from src.core.constants import StrEnum


class TradeAction(StrEnum):
    """Action type for a trade order."""

    BUY = "BUY"
    SELL = "SELL"


class Trade(BaseModel):
    """Domain model representing an executable trade order."""

    trade_id: str = Field(..., description="Unique trade identifier")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    ticker: str = Field(..., description="Security ticker symbol")
    action: TradeAction = Field(..., description="Trade action (BUY or SELL)")
    shares: float = Field(..., gt=0.0, description="Quantity of shares to execute")
    current_weight: float = Field(..., ge=0.0, le=1.0, description="Pre-rebalance weight")
    target_weight: float = Field(..., ge=0.0, le=1.0, description="Post-optimization weight")
    weight_change: float = Field(..., description="Target weight minus current weight")
    price: float = Field(..., gt=0.0, description="Execution reference price per share")
    market_value: float = Field(..., gt=0.0, description="Total trade market value")
    estimated_cost: float = Field(default=0.0, ge=0.0, description="Total estimated transaction fees & slippage")
    tax_impact: float = Field(default=0.0, description="Estimated tax impact (gain/loss tax liability)")
    reason: str = Field(..., description="Rebalancing reason for this trade")
