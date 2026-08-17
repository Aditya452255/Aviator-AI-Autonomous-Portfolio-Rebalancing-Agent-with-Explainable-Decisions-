"""Domain models for tax purchase lots and unrealized/realized tax lot management."""

from typing import Optional
from pydantic import BaseModel, Field


class TaxLot(BaseModel):
    """Domain model representing a specific purchase lot for tax optimization."""

    lot_id: str = Field(..., description="Unique tax lot identifier")
    portfolio_id: str = Field(..., description="Associated portfolio ID")
    ticker: str = Field(..., description="Security ticker symbol")
    purchase_date: str = Field(..., description="Purchase date in YYYY-MM-DD format")
    cost_basis_per_share: float = Field(..., gt=0.0, description="Cost basis per share")
    shares: float = Field(..., gt=0.0, description="Quantity of shares in this lot")
    holding_days: int = Field(..., ge=0, description="Days elapsed since purchase")
    is_long_term: bool = Field(default=False, description="True if holding period qualifies as Long-Term")
    current_price: float = Field(default=100.0, gt=0.0, description="Current market price per share")
    unrealized_gain_loss: float = Field(default=0.0, description="Unrealized PnL for this lot")
