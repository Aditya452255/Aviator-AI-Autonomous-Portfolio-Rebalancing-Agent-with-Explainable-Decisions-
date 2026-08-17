"""Asset allocation and security holding models."""

from typing import Dict
from pydantic import BaseModel, Field, model_validator
from src.core.constants import AssetCategory


class TargetAllocation(BaseModel):
    """Target asset category weights model."""

    equity: float = Field(..., ge=0.0, le=1.0)
    fixed_income: float = Field(..., ge=0.0, le=1.0)
    alternatives: float = Field(..., ge=0.0, le=1.0)
    cash: float = Field(..., ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_total_weight(self) -> "TargetAllocation":
        total = self.equity + self.fixed_income + self.alternatives + self.cash
        if not (0.999 <= total <= 1.001):
            raise ValueError(f"Target allocation weights must sum to 1.0 (got {total:.4f})")
        return self


class CurrentAllocation(BaseModel):
    """Current asset category weights and calculated drift model."""

    equity: float = Field(..., ge=0.0, le=1.0)
    fixed_income: float = Field(..., ge=0.0, le=1.0)
    alternatives: float = Field(..., ge=0.0, le=1.0)
    cash: float = Field(..., ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_total_weight(self) -> "CurrentAllocation":
        total = self.equity + self.fixed_income + self.alternatives + self.cash
        if not (0.999 <= total <= 1.001):
            raise ValueError(f"Current allocation weights must sum to 1.0 (got {total:.4f})")
        return self


class SecurityHolding(BaseModel):
    """Detailed position holding for a single security within a portfolio."""

    ticker: str = Field(..., description="Unique security ticker symbol")
    asset_class: str = Field(..., description="Granular asset class")
    asset_category: str = Field(..., description="High-level asset category")
    target_weight: float = Field(..., ge=0.0, le=1.0, description="Target weight fraction")
    current_weight: float = Field(..., ge=0.0, le=1.0, description="Current weight fraction")
    shares: float = Field(..., ge=0.0, description="Number of shares held")
    current_price: float = Field(..., gt=0.0, description="Current market price per share")
    market_value: float = Field(..., ge=0.0, description="Total market value of position")
    cost_basis: float = Field(..., ge=0.0, description="Total cost basis of position")
    unrealized_pnl: float = Field(default=0.0, description="Unrealized profit or loss")
