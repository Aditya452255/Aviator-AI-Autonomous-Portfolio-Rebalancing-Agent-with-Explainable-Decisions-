"""Portfolio domain model."""

from typing import Dict, List
from pydantic import BaseModel, Field, model_validator
from src.core.constants import RiskCategoryKey
from src.models.allocation import SecurityHolding


class Portfolio(BaseModel):
    """Domain model representing a client investment portfolio."""

    portfolio_id: str = Field(..., description="Unique portfolio identifier (e.g. PORT_00001)")
    client_id: str = Field(..., description="ID of the owner client profile")
    risk_category: RiskCategoryKey = Field(..., description="Target risk category key")
    cash_balance: float = Field(..., ge=0.0, description="Available uninvested cash balance")
    total_market_value: float = Field(..., gt=0.0, description="Total portfolio market value (cash + securities)")
    total_cost_basis: float = Field(..., ge=0.0, description="Total cost basis of all assets")
    holdings: List[SecurityHolding] = Field(..., description="List of individual security holdings")
    current_weights: Dict[str, float] = Field(..., description="Current weights breakdown by asset category")
    target_weights: Dict[str, float] = Field(..., description="Target weights breakdown by asset category")
    num_securities: int = Field(..., ge=15, le=40, description="Count of securities held in portfolio")

    @model_validator(mode="after")
    def validate_portfolio_integrity(self) -> "Portfolio":
        """Validate portfolio security count and allocation metrics."""
        if len(self.holdings) != self.num_securities:
            raise ValueError(f"Holdings count ({len(self.holdings)}) does not match num_securities field ({self.num_securities})")
        if not (15 <= len(self.holdings) <= 40):
            raise ValueError(f"Portfolio must contain between 15 and 40 securities (got {len(self.holdings)})")
        return self
