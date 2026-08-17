"""Security master domain model."""

from pydantic import BaseModel, Field, field_validator
from src.core.constants import AssetClass, Country, Currency, Sector


class Security(BaseModel):
    """Domain model representing a financial security in the Security Master."""

    ticker: str = Field(..., description="Unique ticker identifier (e.g. IN_EQ_001)")
    name: str = Field(..., description="Company or asset name")
    asset_class: AssetClass = Field(..., description="Asset class classification")
    sector: Sector = Field(..., description="Economic sector")
    country: Country = Field(..., description="Primary domicile country")
    currency: Currency = Field(..., description="Trading currency")
    expected_return: float = Field(..., ge=-0.50, le=1.00, description="Annual expected return fraction (e.g., 0.12)")
    volatility: float = Field(..., ge=0.001, le=1.50, description="Annualized volatility fraction (e.g., 0.20)")
    average_daily_volume: float = Field(..., ge=0.0, description="Average daily trading volume in base currency")
    liquidity_score: float = Field(..., ge=1.0, le=100.0, description="Liquidity rating from 1 to 100")
    market_cap: float = Field(..., ge=0.0, description="Total market capitalization in base currency")
    initial_price: float = Field(default=100.0, gt=0.0, description="Baseline starting price for simulation")

    @field_validator("ticker")
    @classmethod
    def validate_ticker_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ticker cannot be empty")
        return v.strip().upper()
